from datetime import datetime
from typing import Optional

from odmantic import Model


class User(Model):
    first_name: str
    last_name: str
    email: str
    password: str
    role: str = "patient"
    status: str = "active"
    hospital_id: Optional[str] = None
    created_at: datetime = datetime.utcnow()

    model_config = {
        "collection": "users",
    }

    