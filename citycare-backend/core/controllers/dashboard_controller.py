from datetime import date

from fastapi import HTTPException, status

from core.cruds.dashboard_crud import DashboardCRUD
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


class DashboardController:
    def __init__(self) -> None:
        self.dashboard_crud = DashboardCRUD()

    async def get_dashboard(self) -> dict:
        try:
            logging.info("Calling DashboardController.get_dashboard")

            total_appointments = (
                await self.dashboard_crud.get_total_appointments()
            )

            booked_count = await self.dashboard_crud.get_appointments_by_status(
                "booked"
            )

            today = date.today()
            today_appointments = await self.dashboard_crud.get_appointments_by_date(
                today
            )
            today_count = len(today_appointments)

            today_booked_slots = [appt.slot for appt in today_appointments]
            today_free_slots = [
                slot for slot in VALID_SLOTS if slot not in today_booked_slots
            ]

            logging.info("Dashboard statistics computed successfully")

            return {
                "total_appointments": total_appointments,
                "booked_appointments": booked_count,
                "todays_appointments": today_count,
                "todays_free_slots": len(today_free_slots),
                "todays_booked_slots": today_count,
                "total_slots_per_day": len(VALID_SLOTS),
            }

        except HTTPException:
            raise

        except Exception as error:
            logging.error(
                f"Error in DashboardController.get_dashboard: {error}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while fetching dashboard statistics.",
            )
