from datetime import datetime

from odmantic import Model


class User(Model):
    first_name: str
    last_name: str
    email: str
    password: str
    role: str = "patient"
    status: str = "active"
    created_at: datetime = datetime.utcnow()

    model_config = {
        "collection": "users",
    }

    