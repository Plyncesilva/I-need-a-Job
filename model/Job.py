from enum import Enum
from pydantic import BaseModel

class JobType(Enum):
    CYBERSECURITY = "CYBERSECURITY"
    SOFTWARE_DEVELOPMENT = "SOFTWARE_DEVELOPMENT"
    IT_CONSULTANT = "IT_CONSULTANT"
    IT_SUPPORT = "IT_SUPPORT"
    CUSTOMER_SERVICE = "CUSTOMER_SERVICE"
    OTHER = "OTHER"

class Job(BaseModel):
    job_type: JobType
    published: str
    deadline: str
    start: str
    contract: str
    language: str
    job_title: str
    company_name: str
    location: str
    description: str
    requirements: list[str]
    key_skills: list[str]
    contacts: str
    cv_photo_details: str
    apply_uri: str

class JobList(BaseModel):
    jobs: list[Job]