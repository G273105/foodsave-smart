
import os
import mysql.connector
from dotenv import load_dotenv
from pathlib import Path

# Load database credentials from the .env file.
load_dotenv(Path(__file__).resolve().parent / ".env")


def get_db_connection():
    """Establish a connection to the FoodSave Smart database."""

    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )
