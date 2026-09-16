from sqlmodel import Session, text


class HealthService:
    def __init__(self, session: Session):
        self.session = session

    def database_ready(self) -> bool:
        try:
            self.session.exec(text("SELECT 1")).one()
            return True
        except Exception:
            return False
