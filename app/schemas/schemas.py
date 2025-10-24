from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import Optional, List

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Habit Schemas
class HabitBase(BaseModel):
    name: str
    description: Optional[str] = None
    frequency: str = "daily"

class HabitCreate(HabitBase):
    pass

class Habit(HabitBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Record Schemas
class RecordBase(BaseModel):
    date: date
    completed: bool = False
    notes: Optional[str] = None

class RecordCreate(RecordBase):
    habit_id: int

class Record(RecordBase):
    id: int
    habit_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True 

# Report Schemas

# Notification Schemas
class NotificationBase(BaseModel):
    title: str
    message: str
    is_read: bool = False

class NotificationCreate(NotificationBase):
    user_id: int
    actions: List["NotificationActionCreate"] = Field(default_factory=list)

class Notification(NotificationBase):
    id: int
    user_id: int
    created_at: datetime
    actions: List["NotificationAction"] = Field(default_factory=list)

    class Config:
        from_attributes = True


class NotificationActionBase(BaseModel):
    action_type: str
    label: str
    payload: Optional[str] = None


class NotificationActionCreate(NotificationActionBase):
    pass


class NotificationAction(NotificationActionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


Notification.model_rebuild()
NotificationCreate.model_rebuild()
