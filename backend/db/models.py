import uuid
from sqlalchemy import ForeignKey, Boolean, Column, UUID, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum
from uuid import uuid4
from datetime import datetime


Base = declarative_base()




class User(Base):
    __tablename__ = "users"
    id = Column(UUID, primary_key=True, default=uuid4)
    username = Column(String(50), unique=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)


class Medication(Base):
    __tablename__ = "medications"
    id = Column(UUID, primary_key=True, default=uuid4)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    dosage = Column(String(50))
    instructions = Column(String(), nullable=True)



class ReminderTask(Base):
    __tablename__ = "reminder_tasks"

    id = Column(UUID, primary_key=True, default=uuid4)
    medication_id = Column(UUID, ForeignKey("medications.id", ondelete="CASCADE"))
    time = Column(DateTime(timezone=True))
    is_completed = Column(Boolean, default=False)
    is_notified = Column(Boolean, default=False)


class PushSubscription(Base):
    __tablename__ = "push_subscriptions"
    id = Column(UUID, primary_key=True, default=uuid4)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    endpoint = Column(String, nullable=False)
    p256dh = Column(String, nullable=False)
    auth = Column(String, nullable=False)