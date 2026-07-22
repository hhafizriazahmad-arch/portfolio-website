import os
import shutil
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Handle Vercel read-only filesystem by using /tmp directory for SQLite database
IS_VERCEL = os.environ.get("VERCEL") is not None or os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is not None

if IS_VERCEL:
    db_path = "/tmp/portfolio.db"
    # Copy pre-existing SQLite database if present in workspace
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    local_db = os.path.join(BASE_DIR, "portfolio.db")
    if os.path.exists(local_db) and not os.path.exists(db_path):
        try:
            shutil.copy(local_db, db_path)
        except Exception as e:
            print(f"Failed to copy database to /tmp: {e}")
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"
else:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./portfolio.db"

# connect_args={"check_same_thread": False} is required only for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
