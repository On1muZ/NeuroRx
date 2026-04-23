from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from uuid import UUID
from sqlalchemy.engine import create
from db.models import User
import json
from api.deps import get_current_user
from db.sessions import get_db
from crud.prescription import create_medication, create_all_reminders, get_all_active_reminders, complete_reminder
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.prescription import MedicationCreate
from datetime import timezone
from pydantic import ValidationError

from services.ocr_engine import process_image


router = APIRouter()


@router.post("/upload-photo", response_model=list[MedicationCreate])
async def upload_prescription_photo(file: UploadFile = File(...)):
    try:
        # Читаем файл в память в виде байтов
        file_bytes = await file.read()
        
        # Передаем байты в OCR-модель
        ocr_result_str = await process_image(file_bytes)
        
        if not ocr_result_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не удалось распознать рецепт на изображении."
            )
            
        try:
            raw_info = json.loads(ocr_result_str)
            
            if isinstance(raw_info, dict):
                raw_info = [raw_info]
                
            medications = [MedicationCreate(**item) for item in raw_info]
            return medications
            
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при парсинге ответа от модели OCR."
            )
        except ValidationError as ve:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Ошибка валидации данных от модели OCR: {ve.errors()}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the image: {str(e)}"
        )


@router.post("/create-prescription")
async def create_prescription(
    medication: MedicationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
): 
    try:
        # 1. Create the medication record
        new_medication = await create_medication(
            db=db,
            user_id=current_user.id,
            name=medication.name,
            dosage=medication.dosage,
            instructions=medication.instructions
        )
        reminders = await create_all_reminders(
            db=db,
            medication_id=new_medication.id,
            start_time=medication.start_time,
            end_time=medication.end_time,
            nday=medication.nday,
            times=medication.times
        )

        return {
            "status": "success",
            "medication_id": new_medication.id,
            "reminders_created": len(reminders)
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create prescription: {str(e)}"
        )


@router.get("/get-reminders")
async def get_reminders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    rows = await get_all_active_reminders(db, current_user.id)
    data = {}
    for reminder, medication in rows:
        data[reminder.id] = {
            "medication_id": reminder.medication_id,
            "name": medication.name,
            "dosage": medication.dosage,
            "instructions": medication.instructions,
            "time": reminder.time.astimezone(timezone.utc).isoformat(),
            "is_completed": reminder.is_completed
        }
    return data


@router.patch("/complete-reminder")
async def complete_reminder_endpoint(
    reminder_id: UUID,
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    success = await complete_reminder(db, reminder_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Напоминание не найдено или нет прав доступа"
        )
    return {"status": "success"}