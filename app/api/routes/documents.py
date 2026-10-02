"""Document management API endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from app.api.schemas.document import DocumentListResponse, DeleteResponse

router = APIRouter()


def get_ingestion_pipeline():
    """Dependency to get the ingestion pipeline."""
    from app.main import ingestion_pipeline
    return ingestion_pipeline


@router.get("/api/documents", response_model=DocumentListResponse)
async def list_documents(pipeline=Depends(get_ingestion_pipeline)):
    """List all ingested documents."""
    documents = pipeline.document_store.list_documents()
    return DocumentListResponse(
        documents=documents,
        total=len(documents)
    )


@router.delete("/api/documents/{document_id}", response_model=DeleteResponse)
async def delete_document(document_id: str, pipeline=Depends(get_ingestion_pipeline)):
    """Delete a document and its chunks."""
    doc = pipeline.document_store.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete from vector store
    pipeline.vector_store.delete_by_document(document_id)

    # Delete from document store
    pipeline.document_store.delete_document(document_id)

    # Delete file
    import os
    if os.path.exists(doc.source):
        os.remove(doc.source)

    return DeleteResponse(
        status="success",
        message="Document '{}' deleted successfully".format(doc.title)
    )
