# seed.py

from models import SessionLocal, SchoolClass, LeagueMatch, SportName, LeagueName, Base, engine
from itertools import combinations # 組み合わせを生成するためのライブラリ

print("データベースとテーブルを確認・作成します...")
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # --- クラスの登録 ---
    print("クラスを登録中...")
    class_names = [f"{g}-{c}" for g in range(1, 4) for c in range(1, 7)]
    for name in class_names:
        if not db.query(SchoolClass).filter(SchoolClass.name == name).first():
            db.add(SchoolClass(name=name))
    db.commit()
    print("クラス登録完了。")

    # --- ここからリーグの組み合わせを自動生成 ---
    print("リーグの対戦表を生成中...")
    if db.query(LeagueMatch).first():
        print("既に対戦表が存在するため、スキップします。")
    else:
        all_classes = db.query(SchoolClass).all()
        class_map = {cls.name: cls.id for cls in all_classes}
        
        # リーグごとの参加クラスを定義
        league_teams = {
            'A': [f"{g}-{c}" for g in [1,2,3] for c in [1,2]], # 例: 1-1, 1-2, 2-1, 2-2, 3-1, 3-2
            'B': [f"{g}-{c}" for g in [1,2,3] for c in [3,4]],
            'C': [f"{g}-{c}" for g in [1,2,3] for c in [5]],
            'D': [f"{g}-{c}" for g in [1,2,3] for c in [6]],
        }

        for sport in SportName:
            for league_name, teams in league_teams.items():
                team_ids = [class_map[team_name] for team_name in teams]
                # 総当たりの組み合わせを生成
                for team1_id, team2_id in combinations(team_ids, 2):
                    fixture = LeagueMatch(
                        sport=sport,
                        league=LeagueName[league_name],
                        class1_id=team1_id,
                        class2_id=team2_id,
                        is_finished=False # 最初は未完了
                    )
                    db.add(fixture)
        db.commit()
        print("対戦表の生成完了。")

finally:
    db.close()