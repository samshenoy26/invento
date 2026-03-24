from jose import jwt
import time

JWT_SECRET = "dev-secret-change-me"
JWT_ALG = "HS256"

def make_token(sub, roles, minutes=60):
    payload = {
        "sub": sub,
        "roles": roles,
        "exp": int(time.time()) + minutes * 60
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

user_token = make_token("user1", ["user"])
admin_token = make_token("admin1", ["admin"])

print("USER TOKEN:\n", user_token)
print("\nADMIN TOKEN:\n", admin_token)