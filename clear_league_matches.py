import sqlite3

def clear_league_matches():
    """
    Deletes all records from the league_matches table in the class_match.db.
    """
    db_file = 'class_match.db'
    conn = None  # Initialize conn to None
    try:
        # Connect to the database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Check if the table exists and get the row count
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='league_matches'")
        if cursor.fetchone() is None:
            print("Table 'league_matches' does not exist. Nothing to delete.")
            return

        cursor.execute("SELECT COUNT(*) FROM league_matches")
        count = cursor.fetchone()[0]

        if count == 0:
            print("The 'league_matches' table is already empty.")
            return

        # Execute the delete statement
        cursor.execute("DELETE FROM league_matches;")

        # Commit the changes
        conn.commit()

        print(f"Successfully deleted {count} records from the league_matches table.")

    except sqlite3.Error as e:
        print(f"An unexpected database error occurred: {e}")
    finally:
        # Close the connection
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Attempting to delete all records from the 'league_matches' table...")
    clear_league_matches()
    print("Operation finished.")
