from sqlalchemy import Enum, JSON, ForeignKey, Boolean, Column, UUID, String, DateTime
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
    medications = relationship("Medication", back_populates="user")


class FrequencyType(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    INTERVAL = "interval"


class Medication(Base):
    __tablename__ = "medications"
    id = Column(UUID, primary_key=True, default=uuid4)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    dosage = Column(String(50))
    instructions = Column(String(), nullable=True)
    raw_ocr_data = Column(JSON)

    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    frequency_type = Column(Enum(FrequencyType), default=FrequencyType.DAILY)
    schedule_pattern = Column(JSON, nullable=True)
    reminder_times = Column(JSON, nullable=False)
    user = relationship("User", back_populates="medications")
    reminders = relationship("ReminderTask", back_populates="medication", cascade="all, delete-orphan")


class ReminderTask(Base):
    __tablename__ = "reminder_tasks"

    id = Column(UUID, primary_key=True, index=True)
    medication_id = Column(UUID, ForeignKey("medications.id"))
    
    scheduled_at = Column(DateTime, nullable=False)
    is_taken = Column(Boolean, default=False)
    
    medication = relationship("Medication", back_populates="reminders")