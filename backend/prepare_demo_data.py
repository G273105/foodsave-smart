
from datetime import datetime
from pathlib import Path
import csv

from db import get_db_connection


# Dates for the FoodSave Smart demonstration.
# Only these 12 existing batches will be updated.
DEMO_BATCHES = {
    # Already expired
    1: "2026-10-15 20:30:29",
    2: "2026-10-16 20:30:29",
    3: "2026-10-17 20:30:29",

    # Expiring around the presentation
    4: "2026-11-06 20:30:29",
    17: "2026-11-07 19:52:37",
    18: "2026-11-07 19:52:37",

    # Remaining available after the presentation
    19: "2026-11-15 19:52:37",
    20: "2026-11-18 19:52:37",
    21: "2026-11-20 19:52:37",
    22: "2026-11-22 19:52:37",
    23: "2026-11-25 19:54:06",
    24: "2026-11-30 19:54:23",
}


def main():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        ids = sorted(DEMO_BATCHES)
        placeholders = ", ".join(["%s"] * len(ids))

        cursor.execute(
            f"""
            SELECT batch_id, name, sell_by_at,
                   quantity_available, availability_status
            FROM batches
            WHERE batch_id IN ({placeholders})
            ORDER BY batch_id
            """,
            tuple(ids),
        )

        rows = cursor.fetchall()

        if len(rows) != len(ids):
            raise RuntimeError(
                "Some demo batches are missing. No changes made."
            )

        # Create a backup before making any changes.
        backup_path = Path(__file__).parent / "demo_batches_backup.csv"

        if not backup_path.exists():
            with backup_path.open(
                "w", newline="", encoding="utf-8"
            ) as file:
                writer = csv.writer(file)
                writer.writerow([
                    "batch_id",
                    "name",
                    "sell_by_at",
                    "quantity_available",
                    "availability_status",
                ])

                for row in rows:
                    writer.writerow([
                        row["batch_id"],
                        row["name"],
                        row["sell_by_at"],
                        row["quantity_available"],
                        row["availability_status"],
                    ])

            print(f"Backup created: {backup_path}")
        else:
            print("Existing backup preserved.")

        print("\nPlanned demo dates:\n")

        for row in rows:
            batch_id = row["batch_id"]
            print(
                f"{batch_id}: {row['name']} -> "
                f"{DEMO_BATCHES[batch_id]}"
            )

        confirmation = input(
            "\nType YES to update these 12 batches: "
        )

        if confirmation != "YES":
            print("Cancelled. No database changes made.")
            return

        for batch_id, date_text in DEMO_BATCHES.items():
            new_date = datetime.strptime(
                date_text, "%Y-%m-%d %H:%M:%S"
            )

            cursor.execute(
                """
                UPDATE batches
                SET sell_by_at = %s
                WHERE batch_id = %s
                """,
                (new_date, batch_id),
            )

        connection.commit()

        print("\nSUCCESS: Demo dates updated in Aiven.")
        print("All 12 selected batches have been processed.")

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
