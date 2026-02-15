from contextlib import contextmanager
from trailine_model.base import SessionLocal, DATABASE_URL

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


print(DATABASE_URL)