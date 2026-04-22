from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from sqlalchemy.engine import create
from db.models import User
import shutil
import os
import uuid
from api.deps import get_current_user
from db.sessions import get_db
from crud.prescription import create_medication
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.prescription import MedicationCreate
from datetime import timezone

# Todo:
# from services.ocr import get_medication_info


router = APIRouter(prefix="/prescription")


@router.post("/upload-photo")
async def upload_prescription_photo(file: UploadFile = File(...)):
    # Create a temporary directory if it doesn't exist
    upload_dir = "temp_uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate a unique filename to prevent collisions
    file_extension = os.path.splitext(file.filename)[1]
    file_path = os.path.join(upload_dir, f"{uuid.uuid4()}{file_extension}")
    
    try:
        # Save the uploaded file locally
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Пока не реализовано
        # medication_info = await get_medication_info(file_path)
        medication_info = {"test": "test"}
        return medication_info

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the image: {str(e)}"
        )
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@router.post("/create-prescription")
async def create_prescription(
    medication: MedicationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
): 
    try:
        new_med = await create_medication(
            user_id=current_user.id,
            name=medication.name,
            dosage=medication.dosage,
            instructions=medication.instructions,
            raw_ocr_data=medication.raw_ocr_data,
            start_time=medication.start_time.astimezone(timezone.utc).replace(tzinfo=None),
            end_time=medication.end_time.astimezone(timezone.utc).replace(tzinfo=None) if medication.end_time else None,
            frequency_type=medication.frequency_type,
            schedule_pattern=medication.schedule_pattern,
            reminder_times=medication.reminder_times,
            db=db
        )
        return new_med
        
    except Exception as e:
        print(f"Error creating prescription: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
