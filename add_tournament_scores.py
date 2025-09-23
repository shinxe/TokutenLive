import sqlite3

DB_PATH = "class_match.db"

def add_columns_to_tournament_matches():
    """
    tournament_matchesテーブルにスコアとセット数のカラムを追加します。
    このスクリプトは一度だけ実行してください。
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # カラムの存在をチェックするためのPRAGMA
        cursor.execute("PRAGMA table_info(tournament_matches);")
        columns = [info[1] for info in cursor.fetchall()]

        # 追加するカラムのリスト
        new_columns = {
            "class1_score": "INTEGER",
            "class2_score": "INTEGER",
            "class1_sets_won": "INTEGER",
            "class2_sets_won": "INTEGER"
        }

        for col_name, col_type in new_columns.items():
            if col_name not in columns:
                print(f"Adding column '{col_name}' to 'tournament_matches' table...")
                cursor.execute(f"ALTER TABLE tournament_matches ADD COLUMN {col_name} {col_type}")
                print(f"Column '{col_name}' added successfully.")
            else:
                print(f"Column '{col_name}' already exists.")

        conn.commit()
        print("\nDatabase schema updated successfully.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    add_columns_to_tournament_matches()
