from models import SessionLocal, SchoolClass

# 追加したいクラス名をリストとして定義
class_names = [f"{grade}-{class_num}" for grade in range(1, 4) for class_num in range(1, 7)]
# 生成されるリスト: ['1-1', '1-2', ..., '3-5', '3-6']

# データベースセッションを開始
db = SessionLocal()

print("クラスの追加を開始します...")

try:
    # 各クラス名をデータベースに追加
    for name in class_names:
        # 既に同じ名前のクラスが存在しないかチェック (任意)
        exists = db.query(SchoolClass).filter(SchoolClass.name == name).first()
        if not exists:
            db_class = SchoolClass(name=name)
            db.add(db_class)
            print(f"  - {name} を追加")

    # 変更をコミット（保存）
    db.commit()
    print("正常にクラスが追加されました。")

except Exception as e:
    print(f"エラーが発生しました: {e}")
    db.rollback() # エラーが発生した場合は変更を元に戻す

finally:
    # セッションを閉じる
    db.close()