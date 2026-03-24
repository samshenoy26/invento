from fastapi import FastAPI, Depends, Header, HTTPException, status
from book_inventory import Library
from pydantic import BaseModel, Field
from typing import Optional
from jose import jwt, JWTError
import os


app = FastAPI(title="Books API (RBAC v1)")

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALG = "HS256"
ALLOWED_ROLES = {"user", "admin"}

LIB_PATH = "books.json"
lib = Library()

class AuthContext(BaseModel):
    user_id: Optional[str] = None
    role: str

class BookIn(BaseModel):
    name: str = Field(..., min_length=1)
    rating: int = Field(..., ge=0, le=5)
    genre: str = Field(..., min_length=1)

async def get_auth_context(
        authorization: Optional[str] = Header(default=None, alias="Authorization"),
        #after the above, authorization = Bearer ey....
    ) -> AuthContext:
    
    #Checking if authorization header contains any data at all
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid Authorization header")
    
    #Checking if 
    authorization = authorization.strip()
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid Authorization header")
    
    token = authorization.split(" ", 1)[1]

    try:
        claims = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALG],
        )
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    

    #Extract claims
    user_id = claims.get("sub")
    roles = claims.get("roles")

    if not roles or not isinstance(roles, list):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    
    roles_normalized = {r.strip().lower() for r in roles}

    if "admin" in roles_normalized:
        role = "admin"
    elif "user" in roles_normalized:
        role = "user"
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    
    return AuthContext(user_id=user_id, role=role)

def require_role(*allowed_roles: str):

    async def checker(ctx: AuthContext = Depends(get_auth_context)) -> AuthContext:
        if ctx.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return ctx
    return checker

lib.load_from_file(LIB_PATH)

@app.get("/health")
async def health():
    return {"status" : "ok", "count" : len(lib.books)}

@app.get("/books", dependencies=[Depends(require_role("user","admin"))])
async def list_books():
    return lib.books

@app.post(
    "/books",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin"))],
)
async def create_book(book: BookIn):
    created = lib.add_book(book.name, book.rating, book.genre)
    if created is None:
        #Duplicate name
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail = "Book already exists"
        )
    lib.save_to_file(LIB_PATH)
    return created