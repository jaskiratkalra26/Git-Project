from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    github_username: str

class UserCreate(UserBase):
    github_id: int
    github_email: str | None = None
    github_access_token: str

class User(UserBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

class UserResponse(BaseModel):
    user_id: int
    github_username: str
