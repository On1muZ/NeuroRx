from db.models import User
from sqlalchemy import delete, update, select
from sqlalchemy.ext.asyncio import AsyncSession
from utils.crypto import get_password_hash
from schemas.user import UserCreate
from uuid import UUID
from db.models import Medication, FrequencyType
from datetime import datetime


async def create_medication(
    user_id: UUID,
    name: str,
    dosage: str,
    instructions: str | None,
    raw_ocr_data: dict,
    start_time: datetime,
    end_time: datetime | None,
    frequency_type: FrequencyType,
    schedule_pattern: dict | None,
    reminder_times: list[datetime],
    db: AsyncSession,
):
    medication = Medication(
        user_id=user_id,
        name=name,
        dosage=dosage,
        instructions=instructions,
        raw_ocr_data=raw_ocr_data,
        start_time=start_time,
        end_time=end_time,
        frequency_type=frequency_type,
        schedule_pattern=schedule_pattern,
        reminder_times=[t.isoformat() for t in reminder_times],
    )
    db.add(medication)
    await db.commit()
    await db.refresh(medication)
    return medication


async def get_all_user_medications(user_id: UUID, db: AsyncSession):
    query = select(Medication).where(Medication.user_id == user_id)
    result = await db.execute(query)
    medications = result.scalars().all()
    return medications
