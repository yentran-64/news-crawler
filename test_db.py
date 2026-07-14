from sqlmodel import Session

from app.core.database import engine

with Session(engine) as session:
    print("Database connected successfully!")