from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend import db_access
from backend.tools.document_tools import check_documents

router = APIRouter(tags=["documents"])


class DocumentCreate(BaseModel):
    type: str
    issue_date: str | None = None
    expiry_date: str


class DocumentUpdate(BaseModel):
    type: str | None = None
    issue_date: str | None = None
    expiry_date: str | None = None


@router.get("/api/vehicle/{vehicle_id}/documents")
def get_documents(vehicle_id: str):
    return check_documents(vehicle_id)


@router.post("/api/vehicle/{vehicle_id}/documents")
def add_document(vehicle_id: str, body: DocumentCreate):
    return db_access.add_document(vehicle_id, body.type, body.issue_date, body.expiry_date)


@router.put("/api/documents/{doc_id}")
def update_document(doc_id: int, body: DocumentUpdate):
    existing = db_access.get_document(doc_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Document not found")
    fields = {k: v for k, v in body.model_dump().items() if v is not None}
    return db_access.update_document(doc_id, **fields)
