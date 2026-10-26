
from db import get_db_connection

try:
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM batches")
    total_products = cursor.fetchone()[0]

    print("SUCCESS: Connected to Aiven MySQL!")
    print(f"Products in database: {total_products}")

    cursor.close()
    connection.close()

except Exception as error:
    print(f"CONNECTION FAILED: {error}")
