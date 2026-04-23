from db.models import User
from sqlalchemy import delete, update, select
from sqlalchemy.ext.asyncio import AsyncSession
from utils.crypto import get_password_hash
from schemas.user import UserCreate
from uuid import UUID
from db.models import Medication, ReminderTask
from datetime import datetime, timedelta
from uuid import uuid4




async def create_medication(db: AsyncSession, 
                            user_id: UUID, 
                            name: str, 
                            dosage: str, 
                            instructions: str):
    medication = Medication(user_id=user_id, name=name, dosage=dosage, instructions=instructions)
    db.add(medication)
    await db.commit()
    await db.refresh(medication)
    return medication


async def create_all_reminders(db: AsyncSession,
                               medication_id: UUID,
                               start_time: datetime,
                               end_time: datetime,
                               nday: int,
                               times: int):
    current_date = start_time.date()
    end_date = end_time.date()
    
    reminder_tasks = []
    
    while current_date <= end_date:
        for t in times:
            # Combine current date with the specific time from the times array
            reminder_datetime = datetime.combine(current_date, t.time())
            
            # Ensure we don't create reminders in the past if start_time is today
            if reminder_datetime >= start_time and reminder_datetime <= end_time:
                task = ReminderTask(
                    medication_id=medication_id,
                    time=reminder_datetime,
                    is_completed=False
                )
                db.add(task)
                reminder_tasks.append(task)
        
        # Increment by nday + 1 (1 = every other day, so we add 2 days)
        current_date += timedelta(days=nday + 1)
    
    await db.commit()
    return reminder_tasks



async def get_all_user_medications(db: AsyncSession, user_id: UUID):
    query = select(Medication).where(Medication.user_id == user_id)
    result = await db.execute(query)
    medications = result.scalars().all()
    return medications