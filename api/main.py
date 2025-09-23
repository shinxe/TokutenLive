from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

import models, schemas, services
from models import SessionLocal, engine

# データベーステーブルを作成
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware


origins = [
    "http://localhost:5173",
    "http://127.0.0.1:8000",
    "https://tokuten-live.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Authentication ---
ADMIN_PASSWORD = "cm2025"
API_TOKEN = "secret-token"

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

class LoginRequest(BaseModel):
    password: str

async def verify_token(authorization: str = Depends(api_key_header)):
    if authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
        )
    return authorization

@app.post("/login", tags=["Auth"])
def login(login_data: LoginRequest):
    if login_data.password == ADMIN_PASSWORD:
        return {"token": API_TOKEN}
    else:
        raise HTTPException(status_code=401, detail="Incorrect password")

# --- データベースセッションの依存関係 ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- APIエンドポイント ---

@app.post("/classes/", response_model=schemas.SchoolClass, tags=["Classes"], dependencies=[Depends(verify_token)])
def create_class(class_data: schemas.SchoolClassCreate, db: Session = Depends(get_db)):
    """新しいクラスを登録する"""
    db_class = models.SchoolClass(name=class_data.name)
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class

@app.get("/classes/", response_model=List[schemas.SchoolClass], tags=["Classes"])
def read_classes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """登録されているクラスの一覧を取得する"""
    classes = db.query(models.SchoolClass).offset(skip).limit(limit).all()
    return classes

# === リーグ所属チームの管理 ===
@app.post("/leagues/teams/", response_model=schemas.LeagueTeam, tags=["League Teams"], dependencies=[Depends(verify_token)])
def add_team_to_league(team_data: schemas.LeagueTeamCreate, db: Session = Depends(get_db)):
    """リーグにチームを追加する"""
    db_league_team = models.LeagueTeam(**team_data.dict())
    db.add(db_league_team)
    db.commit()
    db.refresh(db_league_team)
    return db_league_team

@app.get("/leagues/{sport}/{league}/teams/", response_model=List[schemas.SchoolClass], tags=["League Teams"])
def get_league_teams(sport: models.SportName, league: models.LeagueName, db: Session = Depends(get_db)):
    """指定されたリーグの全チームを取得する"""
    league_teams = db.query(models.LeagueTeam).filter_by(sport=sport, league=league).all()
    if not league_teams:
        return []
    return [lt.school_class for lt in league_teams]


@app.delete("/leagues/teams/", status_code=200, tags=["League Teams"], dependencies=[Depends(verify_token)])
def remove_team_from_league_endpoint(team_data: schemas.LeagueTeamDelete, db: Session = Depends(get_db)):
    """リーグからチームを削除する"""
    return services.remove_team_from_league(team_data, db)


# === 予選リーグの試合結果管理 ===
@app.get("/leagues/{sport}/{league}/matches/", response_model=List[schemas.LeagueMatch], tags=["League Matches"])
def get_league_matches(sport: models.SportName, league: models.LeagueName, db: Session = Depends(get_db)):
    """指定されたリーグの全対戦カードを取得する"""
    matches = db.query(models.LeagueMatch).filter_by(sport=sport, league=league).all()
    print(f"[Backend] get_league_matches for {sport}-{league}: Found {len(matches)} matches.")
    return matches


@app.post("/league_matches/", response_model=schemas.LeagueMatch, tags=["League Matches"], dependencies=[Depends(verify_token)])
def create_league_match(match_data: schemas.LeagueMatchCreate, db: Session = Depends(get_db)):
    """新しい予選リーグの試合を作成する"""
    db_match = models.LeagueMatch(**match_data.dict(), is_finished=False)
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match


@app.put("/leagues/matches/{match_id}/", response_model=schemas.LeagueMatch, tags=["League Matches"], dependencies=[Depends(verify_token)])
def update_league_match(match_id: int, match_data: schemas.LeagueMatchUpdate, db: Session = Depends(get_db)):
    """予選リーグの試合結果を更新する"""
    match = db.query(models.LeagueMatch).filter(models.LeagueMatch.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    match.class1_score = match_data.class1_score
    match.class2_score = match_data.class2_score
    match.class1_sets_won = match_data.class1_sets_won
    match.class2_sets_won = match_data.class2_sets_won
    match.winner_id = match_data.winner_id
    match.is_finished = True # 試合を完了済みにする
    
    db.commit()
    db.refresh(match)
    return match


@app.delete("/leagues/{sport}/{league}/matches/", status_code=200, tags=["League Matches"], dependencies=[Depends(verify_token)])
def delete_all_league_matches(sport: models.SportName, league: models.LeagueName, db: Session = Depends(get_db)):
    """指定されたリーグの全試合を削除する"""
    result = services.delete_league_matches(sport, league, db)
    return result


@app.post("/leagues/{sport}/{league}/generate_matches/", tags=["League Matches"], dependencies=[Depends(verify_token)])
def generate_league_matches_endpoint(sport: models.SportName, league: models.LeagueName, db: Session = Depends(get_db)):
    """
    指定されたリーグの総当たり戦の組み合わせを自動生成します。
    既存の試合はスキップされます。
    """
    return services.generate_league_matches(sport, league, db)

@app.get("/league_matches/", response_model=List[schemas.LeagueMatch], tags=["League Matches"])
def read_league_matches(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """登録されている予選リーグの試合結果をすべて取得する"""
    matches = db.query(models.LeagueMatch).offset(skip).limit(limit).all()
    return matches

@app.get("/leagues/{sport}/{league}/standings/", response_model=List[schemas.LeagueStanding], tags=["League Standings"])
def get_league_standings(sport: models.SportName, league: models.LeagueName, db: Session = Depends(get_db)):
    """指定された予選リーグの順位表を計算して取得する"""
    standings = services.calculate_league_standings(sport, league, db)
    if not standings:
        raise HTTPException(status_code=404, detail="No matches found for this league")
    return standings

@app.post("/tournaments/{sport}/generate/", response_model=List[schemas.TournamentMatch], tags=["Tournaments"], dependencies=[Depends(verify_token)])
def generate_tournament(sport: models.SportName, db: Session = Depends(get_db)):
    """指定された種目の決勝トーナメントの組み合わせを生成する"""
    return services.generate_tournament_bracket(sport, db)

@app.get("/tournaments/{sport}/", response_model=List[schemas.TournamentMatch], tags=["Tournaments"])
def get_tournament_matches(sport: models.SportName, db: Session = Depends(get_db)):
    """指定された種目の決勝トーナメントの試合一覧を取得する"""
    matches = db.query(models.TournamentMatch).filter(models.TournamentMatch.sport == sport).all()
    if not matches:
        raise HTTPException(status_code=404, detail="Tournament not found for this sport.")
    return matches

@app.put("/tournaments/{sport}/matches/{match_id}/", response_model=schemas.TournamentMatch, tags=["Tournaments"], dependencies=[Depends(verify_token)])
def update_tournament_match_result(
    sport: models.SportName, 
    match_id: int, 
    match_update: schemas.TournamentMatchUpdate, 
    db: Session = Depends(get_db)
):
    """決勝トーナamentsの特定の試合結果を更新し、勝者と敗者を次の試合へ進める"""
    return services.update_tournament_match(sport, match_id, match_update, db)

@app.get("/rankings/total/", response_model=List[schemas.TotalRanking], tags=["Rankings"])
def get_total_rankings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """全種目の結果を集計した総合得点ランキングを取得する"""
    return services.get_total_rankings(db, skip=skip, limit=limit)

@app.delete("/all-leagues", status_code=200, tags=["League"], dependencies=[Depends(verify_token)])
def delete_all_leagues_endpoint(db: Session = Depends(get_db)):
    """
    Deletes all league matches and team associations.
    """
    result = services.delete_all_league_data(db)
    return result

@app.delete("/scores/all", status_code=200, tags=["Admin"], dependencies=[Depends(verify_token)])
def delete_all_scores_endpoint(db: Session = Depends(get_db)):
    """
    Deletes all league and tournament matches, but keeps team associations.
    """
    result = services.delete_all_scores(db)
    return result

