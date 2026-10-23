from getpass import getpass

from werkzeug.security import generate_password_hash
from db import get_db_connection


users = [
    (1, "alex@example.com", "Alex Student", "STUDENT"),
    (2, "maria@example.com", "Maria Staff", "STAFF"),
    (3, "laurentiu@example.com", "Laurentiu Admin", "ADMIN"),
    (4, "florin@example.com", "Florin Student", "STUDENT"),
    (5, "costel@example.com", "Costel Student", "STUDENT"),
    (6, "marius@example.com", "Marius Staff", "STAFF"),
]


connection = get_db_connection()
cursor = connection.cursor()

try:
    for user_id, email, name, role in users:                                                                                                   
        password = getpass(f"Password for {name}: ")

        if len(password) < 12:
            raise ValueError("Password must contain at least 12 characters.")

        password_hash = generate_password_hash(password)

        cursor.execute(
            """
            INSERT INTO users
                (user_id, email, password_hash, display_name, role)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                email = %s,
                password_hash = %s,
                display_name = %s,
                role = %s
            """,
            (
                user_id, email, password_hash, name, role,
                email, password_hash, name, role
            )
        )

    connection.commit()
    print("SUCCESS: 6 test users configured")

except Exception:
    connection.rollback()
    raise

finally:
    cursor.close()
    connection.close()