from datetime import datetime, timezone
from db import SessionLocal, TimeSession


def test_session_creation():
    db = SessionLocal()

    try:
        test_session = TimeSession(
            project="Test",
            task="testing",
            start_time=datetime.now(timezone.utc),
        )
        db.add(test_session)
        db.commit()

        saved = db.query(TimeSession).filter(TimeSession.project == "Test").first()
        assert saved.task == "testing"
        
        db.delete(saved)
        db.commit()
        deleted = db.query(TimeSession).filter(TimeSession.project == "Test").first()
        assert deleted is None
    finally:
        db.close()
