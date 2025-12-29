from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from APP.MODELS.alert import Alert
from APP.MODELS.alert_type import AlertType
from APP.MODELS.employee import Employee
from APP.MODELS.department import Department


class AlertRepository:
    def __init__(self, db: Session):
        self.db = db

    # ------------------- Writes -------------------
    def get_or_create_alert_type(
        self, name: str, severity_level: int, description: Optional[str] = None
    ) -> AlertType:
        obj = self.db.query(AlertType).filter(AlertType.name == name).first()
        if obj:
            return obj
        obj = AlertType(
            name=name,
            description=description or name,
            severity_level=severity_level,
            is_active=True,
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def create_alert(
        self,
        *,
        alert_type_id: int,
        department_id: int,
        employee_id: Optional[int],
        message: str,
        is_resolved: bool = False,
    ) -> Alert:
        alert = Alert(
            alert_type_id=alert_type_id,
            department_id=department_id,
            employee_id=employee_id,
            message=message,
            is_resolved=is_resolved,
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def counts_by_type(self) -> List[Dict[str, Any]]:
        q = (
            self.db.query(
                AlertType.name.label("label"), func.count(Alert.id).label("count")
            )
            .join(Alert, Alert.alert_type_id == AlertType.id)
            .group_by(AlertType.name)
            .order_by(AlertType.name)
        )
        rows = q.all()
        return [{"label": r.label, "count": int(r.count)} for r in rows]

    def status_buckets(self) -> Dict[str, int]:
        now = datetime.now()
        in_progress_threshold = now - timedelta(days=3)

        # waiting: unresolved created within last 3 days
        waiting = (
            self.db.query(func.count(Alert.id))
            .filter(Alert.is_resolved == False)  # noqa: E712
            .filter(Alert.created_at >= in_progress_threshold)
            .scalar()
            or 0
        )

        # in_progress: unresolved older than 3 days
        in_progress = (
            self.db.query(func.count(Alert.id))
            .filter(Alert.is_resolved == False)  # noqa: E712
            .filter(Alert.created_at < in_progress_threshold)
            .scalar()
            or 0
        )

        # done: resolved
        done = (
            self.db.query(func.count(Alert.id))
            .filter(Alert.is_resolved == True)  # noqa: E712
            .scalar()
            or 0
        )

        return {
            "waiting": int(waiting),
            "in_progress": int(in_progress),
            "done": int(done),
        }

    def list_recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        q = (
            self.db.query(
                Alert,
                AlertType,
                Employee,
                Department,
            )
            .join(AlertType, Alert.alert_type_id == AlertType.id)
            .join(Department, Alert.department_id == Department.id)
            .outerjoin(Employee, Alert.employee_id == Employee.id)
            .order_by(Alert.created_at.desc())
            .limit(limit)
        )
        rows = q.all()
        result: List[Dict[str, Any]] = []
        for alert, atype, emp, dept in rows:
            result.append(
                {
                    "id": alert.id,
                    "type": atype.name,
                    "severity_level": atype.severity_level,
                    "department": getattr(dept, "name", None),
                    "employee": getattr(emp, "name", None),
                    "employee_id": getattr(emp, "id", None),
                    "message": alert.message,
                    "created_at": alert.created_at,
                    "is_resolved": alert.is_resolved,
                }
            )
        return result
