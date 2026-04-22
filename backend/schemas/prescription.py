from datetime import datetime
from pydantic import BaseModel
from db.models import FrequencyType


class MedicationBase(BaseModel):
    name: str
    dosage: str
    instructions: str | None
    raw_ocr_data: dict
    start_time: datetime
    end_time: datetime | None
    frequency_type: FrequencyType
    schedule_pattern: dict | None
    reminder_times: list[datetime]


class MedicationCreate(MedicationBase):
    pass


class Medication(MedicationBase):
    id: str
    user_id: str
