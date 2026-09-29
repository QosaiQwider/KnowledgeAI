from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str

class KnowledgeBaseCreate(BaseModel):
    name: str