from datetime import datetime
from typing import Optional
from odmantic import Model


class Prescription(Model):
    appointment_id: str
    patient_id: str
    doctor_id: str
    diagnosis: str
    medicines: str
    notes: Optional[str] = ""
    pdf_url: str
    created_at: datetime = datetime.utcnow()

    model_config = {
        "collection": "prescriptions",
    }
