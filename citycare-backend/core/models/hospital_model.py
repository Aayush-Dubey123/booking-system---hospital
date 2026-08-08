from datetime import datetime
from typing import Optional

from odmantic import Model


class Hospital(Model):
    name: str
    address: str
    phone: str
    owner_id: Optional[str] = None
    created_at: datetime = datetime.utcnow()

    model_config = {
        "collection": "hospitals",
    }
