from db.models import User
from sqlalchemy import delete, update, select
from sqlalchemy.ext.asyncio import AsyncSession
from utils.crypto import get_password_hash
from schemas.user import UserCreate
from uuid import UUID
from db.models import Medication, ReminderTask
from datetime import datetime, timedelta, timezone
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
                               end_time: datetime | None,
                               nday: int,
                               times: list[datetime]):
    
    # Если дата окончания не передана, по умолчанию ставим курс на 30 дней
    if end_time is None:
        end_time = start_time + timedelta(days=30)

    # Убеждаемся, что переданные даты имеют часовой пояс (если нет — считаем их UTC)
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=timezone.utc)
    if end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=timezone.utc)
    
    reminder_tasks = []
    
    for t in times:
        if t.tzinfo is None:
            t = t.replace(tzinfo=timezone.utc)
            
        current_reminder_time = t
        
        while current_reminder_time <= end_time:
            if current_reminder_time >= start_time:
                task = ReminderTask(
                    medication_id=medication_id,
                    time=current_reminder_time,
                    is_completed=False
                )
                db.add(task)
                reminder_tasks.append(task)
            
            # Увеличиваем на нужное количество дней
            current_reminder_time += timedelta(days=nday + 1)
    
    await db.commit()
    return reminder_tasks



async def get_all_active_reminders(db: AsyncSession, user_id: UUID):
    query = select(ReminderTask, Medication).join(Medication).where(Medication.user_id == user_id, ReminderTask.is_completed == False)
    result = await db.execute(query)
    return result.all()


async def get_all_medications(db: AsyncSession, user_id: UUID):
    query = select(Medication).where(Medication.user_id == user_id)
    result = await db.execute(query)
    medications = result.scalars().all()
    return medications


async def complete_reminder(db: AsyncSession, reminder_id: UUID, user_id: UUID):
    # Ищем задачу и проверяем, что она принадлежит текущему пользователю
    query = select(ReminderTask).join(Medication).where(
        ReminderTask.id == reminder_id,
        Medication.user_id == user_id
    )
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    if task:
        task.is_completed = True
        await db.commit()
        return True
    return False
