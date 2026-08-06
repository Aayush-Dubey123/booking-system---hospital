from datetime import date

from fastapi import HTTPException, status

from core.cruds.schedule_crud import ScheduleCRUD
from common.logger import logger

logging = logger(__name__)

VALID_SLOTS = [
    "10:00",
    "10:30",
    "11:00",
    "11:30",
    "12:00",
    "12:30",
    "17:00",
    "17:30",
    "18:00",
    "18:30",
    "19:00",
    "19:30",
]


class ScheduleController:
    def __init__(self) -> None:
        self.schedule_crud = ScheduleCRUD()

    async def get_schedule(self, appointment_date: date) -> dict:
        try:
            logging.info("Calling ScheduleController.get_schedule")

            booked_slots = await self.schedule_crud.get_booked_slots(
                appointment_date
            )

            free_slots = [
                slot for slot in VALID_SLOTS if slot not in booked_slots
            ]

            logging.info(
                f"Schedule computed for {appointment_date}: "
                f"{len(booked_slots)} booked, {len(free_slots)} free"
            )

            return {
                "appointment_date": appointment_date,
                "booked_slots": booked_slots,
                "free_slots": free_slots,
                "total_slots": len(VALID_SLOTS),
                "available_count": len(free_slots),
                "booked_count": len(booked_slots),
            }

        except HTTPException:
            raise

        except Exception as error:
            logging.error(f"Error in ScheduleController.get_schedule: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while fetching the schedule.",
            )
