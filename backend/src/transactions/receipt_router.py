"""Authenticated receipt review and storage endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_current_user, get_db
from src.transactions import receipts
from src.transactions.receipt_schemas import (
    ReceiptCreate, ReceiptDraft, ReceiptResult, ReceiptTotals, ReceiptUpload,
)

router = APIRouter(prefix="/receipts", tags=["receipts"])


@router.post("/upload", response_model=ReceiptUpload)
async def upload_receipt(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    data = await file.read(receipts.MAX_UPLOAD_BYTES + 1)
    return await receipts.extract_receipt(db, user.id, data)


@router.post("/preview", response_model=ReceiptTotals)
async def preview_receipt(body: ReceiptDraft, _user=Depends(get_current_user)):
    return receipts.calculate_totals(body)


@router.post("", response_model=ReceiptResult, status_code=201)
async def save_receipt(
    body: ReceiptCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)
):
    return await receipts.save_receipt(db, user.id, body)


@router.put("/{transaction_id}", response_model=ReceiptResult)
async def revise_receipt(
    transaction_id: UUID, body: ReceiptDraft,
    db: AsyncSession = Depends(get_db), user=Depends(get_current_user),
):
    return await receipts.revise_receipt(db, user.id, transaction_id, body)
