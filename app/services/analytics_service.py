from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
from app.models.client_model import Client

class AnalyticsService:
    @staticmethod
    def get_gym_attendance_stats(db: Session):
        # Attendance tracking removed. Returning empty stats.
        return {
            "today_attendance": 0,
            "weekly_average": 0,
            "peak_hour": "N/A",
            "inactive_clients": 0
        }

    @staticmethod
    def get_client_consistency(client_id: int, db: Session):
        # Attendance tracking removed. Returning empty stats.
        return {
            "monthly_visits": 0,
            "current_streak": 0,
            "last_visit": None
        }

analytics_service = AnalyticsService()
