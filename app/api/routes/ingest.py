"""Document ingestion API endpoint."""
import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from app.api.schemas.document import IngestResponse
from app.pipeline.ingestion import IngestionPipeline
from app.config import settings

router = APIRouter()


def get_ingestion_pipeline() -> IngestionPipeline:
    """Dependency to get the ingestion pipeline."""
    from app.main import ingestion_pipeline
    return ingestion_pipeline


@router.post("/api/ingest", response_model=IngestResponse)
async def ingest_document(
    file: UploadFile = File(...),
    title: str = Form(None),
    pipeline: IngestionPipeline = Depends(get_ingestion_pipeline)
):
    """Upload and ingest a document into the knowledge base."""
    # Validate file type
    ext = os.path.splitext(file.filename)[1].lower()
    allowed = {".pdf", ".txt", ".md", ".docx"}
    if ext not in allowed:
        raise HTTPException(
            status_code=422,
            detail="Unsupported file format. Allowed: {}".format(", ".join(allowed))
        )

    # Validate file size (10MB max)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 10MB)")

    # Save file
    os.makedirs(settings.upload_dir, exist_ok=True)
    file_path = os.path.join(settings.upload_dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(content)

    # Ingest
    try:
        doc = pipeline.ingest_file(file_path, title)
        return IngestResponse(
            document_id=doc.document_id,
            title=doc.title,
            chunks_ingested=doc.chunk_count,
            status=doc.status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ingestion failed: {}".format(str(e)))
