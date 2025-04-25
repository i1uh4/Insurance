from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
from psycopg2.extras import RealDictCursor
import pathlib

from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def execute_sql_file(file_path, params=None):
    base_path = pathlib.Path(__file__).parent.absolute()
    full_path = base_path / "sql" / file_path

    with open(full_path, 'r') as f:
        sql = f.read()

    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        cursor.execute(sql, params or {})

        try:
            result = cursor.fetchall()
            conn.commit()
            return result
        except psycopg2.ProgrammingError:
            conn.commit()
            return None

    except Exception as error:
        print(f"Error executing SQL: {error}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            cursor.close()
            conn.close()