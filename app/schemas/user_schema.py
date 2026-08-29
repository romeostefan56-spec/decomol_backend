from pydantic import BaseModel


class UserCreate(BaseModel):
    code: str
    name: str
    password: str
