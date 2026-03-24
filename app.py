from fastapi import FastAPI, Depends, Header, HTTPException, status
from book_inventory import Library
from pydantic import BaseModel, Field
from typing import Optional



app = FastAPI(title="Books API (RBAC v1)")

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
        x_user_id: Optional[str] = Header(default=None, alias="X-User-Id"),
        x_role: Optional[str] = Header(default=None, alias="X-Role")
        ,) -> AuthContext:
    if not x_role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing role")
    role = x_role.strip().lower()
    if role not in {"user", "admin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden role")
     
    return AuthContext(user_id=x_user_id, role=role)

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