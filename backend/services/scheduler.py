from apscheduler.schedulers.asyncio import AsyncIOScheduler
from db.sessions import AsyncSessionLocal
from db.models import ReminderTask, Medication, PushSubscription
from sqlalchemy import select
from datetime import datetime, timezone
from pywebpush import webpush, WebPushException
import json
import asyncio
from core.config import settings

scheduler = AsyncIOScheduler()

async def send_push_notification(sub: PushSubscription, title: str, body: str, db = None):
    """Отправляет пуш-уведомление на конкретное устройство."""
    try:
        await asyncio.to_thread(
            webpush,
            subscription_info={
                "endpoint": sub.endpoint, 
                "keys": {"p256dh": sub.p256dh, "auth": sub.auth}
            },
            data=json.dumps({
                "title": title,
                "body": body
            }),
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={"sub": settings.VAPID_SUBJECT}
        )
        return True
    except WebPushException as ex:
        print(f"Ошибка WebPush для {sub.endpoint}: {ex}")
        if ex.response is not None and ex.response.status_code in [404, 410]:
            print(f"Удаляем недействительную подписку: {sub.endpoint}")
            if db:
                await db.delete(sub)
        return False

async def check_reminders():
    async with AsyncSessionLocal() as db:
        now = datetime.now(timezone.utc)
        
        query = select(ReminderTask, Medication).join(
            Medication, ReminderTask.medication_id == Medication.id
        ).where(
            ReminderTask.time <= now,
            ReminderTask.is_completed == False,
            ReminderTask.is_notified == False
        )
        result = await db.execute(query)
        rows = result.all()
        
        if not rows:
            return

        print(f"[{now}] Найдено задач для уведомления: {len(rows)}")

        for task, medication in rows:
            print(f"Обработка: {medication.name} ({medication.dosage}) для пользователя {medication.user_id}")
            
            sub_query = select(PushSubscription).where(PushSubscription.user_id == medication.user_id)
            sub_result = await db.execute(sub_query)
            subs = sub_result.scalars().all()

            if subs:
                for sub in subs:
                    await send_push_notification(
                        sub, 
                        "💊 Пора выпить лекарство!", 
                        f"Примите {medication.name} - {medication.dosage}",
                        db=db
                    )
            else:
                print(f"!!! ПРЕДУПРЕЖДЕНИЕ: Нет подписок для пользователя {medication.user_id}")

            task.is_notified = True

        await db.commit()

scheduler.add_job(check_reminders, 'interval', minutes=1)
