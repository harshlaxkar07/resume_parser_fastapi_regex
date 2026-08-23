
import json
import os
import shutil
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile

from api.schemas import (
    UpdateResumeRequest,
)
from extractor.database_writer import (
    delete_resume,
    get_all_resumes,
    get_resume,
    save_resume,
    update_resume,
)
from extractor.extractor import parse_resume
from extractor.pdf_reader import extract_text_from_pdf
from extractor.text_cleaner import clean_text


router = APIRouter()


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    os.makedirs("resumes", exist_ok=True)

    file_extension = os.path.splitext(file.filename)[1]
    stored_filename = f"{uuid.uuid4()}{file_extension}"

    file_path = os.path.join(
        "resumes",
        stored_filename,
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)

    raw_text = extract_text_from_pdf(file_path)
    # print(raw_text)
    cleaned_text = clean_text(raw_text)
    metadata = parse_resume(cleaned_text)

    pdf_id = save_resume(
        filename=file.filename,
        stored_filename=stored_filename,
        file_path=file_path,
        file_size=file_size,
        metadata=metadata,
    )

    return {
        "message": "Resume uploaded successfully.",
        "pdf_id": pdf_id,
        "metadata": metadata,
    }


@router.get("/resume")
def list_resumes():
    resumes = get_all_resumes()

    for resume in resumes:
        resume["skills"] = (
            json.loads(resume["skills"])
            if resume["skills"]
            else None
        )
        resume["education"] = (
            json.loads(resume["education"])
            if resume["education"]
            else None
        )
        resume["experience"] = (
            json.loads(resume["experience"])
            if resume["experience"]
            else None
        )
        resume["projects"] = (
            json.loads(resume["projects"])
            if resume["projects"]
            else None
        )
        resume["certifications"] = (
            json.loads(resume["certifications"])
            if resume["certifications"]
            else None
        )
        resume["languages"] = (
            json.loads(resume["languages"])
            if resume["languages"]
            else None
        )

    return resumes


@router.get("/resume/{pdf_id}")
def get_resume_by_id(pdf_id: int):
    resume = get_resume(pdf_id)

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found.",
        )

    resume["skills"] = (
        json.loads(resume["skills"])
        if resume["skills"]
        else None
    )
    resume["education"] = (
        json.loads(resume["education"])
        if resume["education"]
        else None
    )
    resume["experience"] = (
        json.loads(resume["experience"])
        if resume["experience"]
        else None
    )
    resume["projects"] = (
        json.loads(resume["projects"])
        if resume["projects"]
        else None
    )
    resume["certifications"] = (
        json.loads(resume["certifications"])
        if resume["certifications"]
        else None
    )
    resume["languages"] = (
        json.loads(resume["languages"])
        if resume["languages"]
        else None
    )

    return resume


@router.post("/resume/{pdf_id}")
def update_resume_by_id(
    pdf_id: int,
    metadata: UpdateResumeRequest,
):
    rows = update_resume(
        pdf_id,
        metadata.model_dump(),
    )

    if rows == 0:
        raise HTTPException(
            status_code=404,
            detail="Resume not found.",
        )

    return {
        "message": "Resume updated successfully.",
    }


@router.delete("/resume/{pdf_id}")
def delete_resume_by_id(pdf_id: int):
    resume = get_resume(pdf_id)

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found.",
        )

    if os.path.exists(resume["file_path"]):
        os.remove(resume["file_path"])

    delete_resume(pdf_id)

    return {
        "message": "Resume deleted successfully.",
    }

