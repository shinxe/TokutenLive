import sqlite3

# データベースに接続
conn = sqlite3.connect('class_match.db')
cursor = conn.cursor()

# leaguesテーブルにis_finishedカラムを追加
try:
    cursor.execute('ALTER TABLE leagues ADD COLUMN is_finished BOOLEAN DEFAULT 0')
    print("leaguesテーブルにis_finishedカラムを追加しました。")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("leaguesテーブルには既にis_finishedカラムが存在します。")
    elif "no such table" in str(e):
        print("leaguesテーブルが存在しないため、スキップします。")
    else:
        # その他のエラーの場合は表示するが、処理は続行
        print(f"leaguesテーブルの更新中に予期せぬエラーが発生しました: {e}")

# tournament_matchesテーブルにis_finishedカラムを追加
try:
    cursor.execute('ALTER TABLE tournament_matches ADD COLUMN is_finished BOOLEAN DEFAULT 0')
    print("tournament_matchesテーブルにis_finishedカラムを追加しました。")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("tournament_matchesテーブルには既にis_finishedカラムが存在します。")
    else:
        # その他のエラーの場合は表示するが、処理は続行
        print(f"tournament_matchesテーブルの更新中に予期せぬエラーが発生しました: {e}")
        
# league_matchesテーブルにis_finishedカラムを追加
try:
    cursor.execute('ALTER TABLE league_matches ADD COLUMN is_finished BOOLEAN DEFAULT 0')
    print("league_matchesテーブルにis_finishedカラムを追加しました。")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("league_matchesテーブルには既にis_finishedカラムが存在します。")
    else:
        # その他のエラーの場合は表示するが、処理は続行
        print(f"league_matchesテーブルの更新中に予期せぬエラーが発生しました: {e}")

# 変更をコミット
conn.commit()

# 接続を閉じる
conn.close()

print("\nデータベースの更新処理が完了しました。")