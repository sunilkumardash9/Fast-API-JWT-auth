from pydantic import BaseModel, Field, EmailStr

class post_schema(BaseModel):
    id : int = Field(default=None)
    #email: str = Field(...)
    title: str = Field(...)
    body : str = Field(...)


class user_schema(BaseModel):
    fullname : str = Field(...)
    email : EmailStr = Field(...)
    password : str = Field(...)
    #disabled : bool = None

    class Config:
        schema_extra = {
            "example": {
                "fullname": "Joe Doe",
                "email": "joe@xyz.com",
                "password": "any"
            }
        }


class UserLoginSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "email": "joe@xyz.com",
                "password": "any"
            }
        }
