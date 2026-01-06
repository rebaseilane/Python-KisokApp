from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SERVER = 'localhost'
DATABASE = 'KioskDB'
DRIVER = 'ODBC Driver 17 for SQL Server'

DATABASE_URL = (
    f"mssql+pyodbc://@{SERVER}/{DATABASE}"
    f"?driver={DRIVER}&trusted_connection=yes"
)


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
