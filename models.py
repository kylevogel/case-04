from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator

# Model for validating incoming survey data
class SurveySubmission(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=13, le=120)
    consent: bool = Field(..., description="Must be true to accept")
    rating: Optional[int] = Field(None, ge=1, le=5)
    comments: Optional[str] = Field(None, max_length=1000)
    
    # Fields for Exercises 1 and 3
    user_agent: Optional[str] = None
    submission_id: Optional[str] = None

    @validator("comments")
    def strip_comments(cls, v):
        return v.strip() if isinstance(v, str) else v
    
    @validator("consent")
    def must_consent(cls, v):
        if v is not True:
            raise ValueError("consent must be true")
        return v

# Model for the data that is actually stored to disk
class StoredSurveyRecord(SurveySubmission):
    received_at: datetime
    ip: str
    
    # Override types for hashed PII (Exercise 2)
    email: str
    age: str
