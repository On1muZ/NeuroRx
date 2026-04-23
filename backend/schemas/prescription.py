from datetime import datetime
from pydantic import BaseModel


class MedicationBase(BaseModel):
    name: str
    dosage: str
    instructions: str | None
    start_time: datetime
    end_time: datetime | None
    nday: int = 0
    times: list[datetime]


class MedicationCreate(MedicationBase):
    pass


class Medication(MedicationBase):
    id: str
    user_id: str
