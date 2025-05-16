from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import psycopg2
import pathlib
from psycopg2.extras import RealDictCursor

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_SLAVE_URL = os.getenv("DATABASE_SLAVE_URL", DATABASE_URL)

# Основное соединение (Мастер)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Соединение с репликой (Слейв) - только для чтения
slave_engine = create_engine(DATABASE_SLAVE_URL)
SlaveSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=slave_engine)


def get_db():
    """Получение сессии с мастер-базой (для чтения и записи)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_slave_db():
    """Получение сессии с реплика-базой (только для чтения)"""
    db = SlaveSessionLocal()
    try:
        yield db
    finally:
        db.close()


def execute_sql_file(file_path, params=None, read_only=False):
    """
    Выполнение SQL-файла

    Args:
        file_path: путь к SQL-файлу
        params: параметры для SQL-запроса
        read_only: если True, запрос выполняется на реплике (только для SELECT)
    """
    base_path = pathlib.Path(__file__).parent.absolute()
    full_path = base_path / "sql" / file_path

    with open(full_path, 'r') as f:
        sql = f.read()

    # Определяем, является ли запрос только для чтения
    is_select_query = sql.strip().lower().startswith('select')

    # Выбираем соединение в зависимости от типа запроса
    connection_string = DATABASE_SLAVE_URL if is_select_query and read_only else DATABASE_URL

    conn = None
    try:
        conn = psycopg2.connect(connection_string, cursor_factory=RealDictCursor)
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
