from typing import List

from pydantic import BaseModel


class ResumeMetadata(BaseModel):
    full_name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    linkedin: str | None = None
    github: str | None = None
    summary: str | None = None

    skills: List[str] | None = None
    education: List[str] | None = None
    experience: List[str] | None = None
    projects: List[str] | None = None
    certifications: List[str] | None = None
    languages: List[str] | None = None


class ResumeResponse(BaseModel):
    pdf_id: int
    filename: str
    stored_filename: str
    file_path: str
    file_size: int
    uploaded_at: str
    metadata: ResumeMetadata


class UpdateResumeRequest(ResumeMetadata):
    pass