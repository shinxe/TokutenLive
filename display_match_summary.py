
import os
import sys
from sqlalchemy.orm import Session
from collections import defaultdict

# 'api' ディレクトリをPythonのパスに追加して、modelsをインポートできるようにする
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'api')))

try:
    # LeagueTeamをインポートに追加
    from models import SportName, LeagueName, LeagueMatch, TournamentMatch, SchoolClass, SessionLocal, LeagueTeam
except ImportError as e:
    print(f"エラー: 必要なモジュールが見つかりません。 ({e})")
    print("このスクリプトはプロジェクトのルートディレクトリで実行してください。")
    sys.exit(1)

def get_league_standings(sport: SportName, league: LeagueName, db: Session):
    """
    指定されたリーグの現在の勝ち、負け、引き分けの数を計算する
    """
    # `stats`辞書をクラスIDをキーとして初期化
    stats = defaultdict(lambda: {"wins": 0, "losses": 0, "ties": 0, "name": ""})
    
    # スキーマに基づき、LeagueTeamテーブルからリーグに所属する全チームを取得
    league_teams_query = db.query(LeagueTeam).filter_by(sport=sport, league=league).all()
    if not league_teams_query:
        return {}
        
    # 取得した全チームをstats辞書に初期登録
    for team_assoc in league_teams_query:
        # 関連付けられたSchoolClassオブジェクトからクラス名を取得
        class_name = db.query(SchoolClass).filter_by(id=team_assoc.class_id).first().name
        stats[team_assoc.class_id]["name"] = class_name

    # 完了した試合結果を取得
    matches = db.query(LeagueMatch).filter(
        LeagueMatch.sport == sport,
        LeagueMatch.league == league,
        LeagueMatch.is_finished == True
    ).all()

    for match in matches:
        score1 = match.class1_score if match.class1_score is not None else 0
        score2 = match.class2_score if match.class2_score is not None else 0

        if score1 > score2:
            stats[match.class1_id]["wins"] += 1
            stats[match.class2_id]["losses"] += 1
        elif score2 > score1:
            stats[match.class2_id]["wins"] += 1
            stats[match.class1_id]["losses"] += 1
        else:
            stats[match.class1_id]["ties"] += 1
            stats[match.class2_id]["ties"] += 1
            
    return stats

def main():
    """
    メイン関数：全種目の試合結果をDBから読み込んで表示する
    """
    db = SessionLocal()
    try:
        print("=" * 40)
        print("== 全種目の試合結果サマリー ==")
        print("=" * 40 + "\n")

        for sport in SportName:
            # '臨時得点'は集計から除外
            if sport == SportName.EXTRA:
                continue

            print(f"--- {sport.value} ---")
            
            # --- リーグ戦の結果 ---
            print("\n[リーグ戦]")
            has_league_matches = False
            for league in LeagueName:
                standings = get_league_standings(sport, league, db)
                if not standings:
                    continue
                
                has_league_matches = True
                print(f"\n  - {league.value}リーグ -")
                
                # 勝ち負け表
                print("    [勝敗表]")
                sorted_standings = sorted(standings.items(), key=lambda item: item[1]['name'])
                for class_id, data in sorted_standings:
                    print(f"      {data['name']}: {data['wins']}勝 {data['losses']}敗 {data['ties']}分")

                # 各試合のスコア
                print("\n    [試合結果]")
                matches = db.query(LeagueMatch).filter(
                    LeagueMatch.sport == sport,
                    LeagueMatch.league == league,
                    LeagueMatch.is_finished == True
                ).all()
                
                if not matches:
                    print("      まだ完了した試合がありません。")
                else:
                    for match in matches:
                        print(f"      - {match.class1.name} vs {match.class2.name}  ->  {match.class1_score} - {match.class2_score}")
            
            if not has_league_matches:
                print("  まだ試合がありません。")

            
            print("\n" + "="*30 + "\n")

    finally:
        db.close()

if __name__ == "__main__":
    main()
