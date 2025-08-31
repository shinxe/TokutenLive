from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models, schemas,services
from models import SessionLocal, engine

# データベーステーブルを作成
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware


origins = [
    "http://localhost:5173",
    "https://boat-racing-nu.vercel.app",#prevent!
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- データベースセッションの依存関係 ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- APIエンドポイント ---

@app.post("/classes/", response_model=schemas.SchoolClass, tags=["Classes"])
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

# === 予選リーグの試合結果管理 ===
@app.get("/leagues/{sport}/{league}/matches/", response_model=List[schemas.LeagueMatch], tags=["League Matches"])
def get_league_matches(sport: models.SportName, league: models.LeagueName, db: Session = Depends(get_db)):
    """指定されたリーグの全対戦カードを取得する"""
    matches = db.query(models.LeagueMatch).filter_by(sport=sport, league=league).all()
    return matches

@app.put("/leagues/matches/{match_id}/", response_model=schemas.LeagueMatch, tags=["League Matches"])
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

@app.post("/tournaments/{sport}/generate/", response_model=List[schemas.TournamentMatch], tags=["Tournaments"])
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

@app.put("/tournaments/{sport}/matches/{match_id}/", response_model=schemas.TournamentMatch, tags=["Tournaments"])
def update_tournament_match_result(
    sport: models.SportName, 
    match_id: int, 
    match_update: schemas.TournamentMatchUpdate, 
    db: Session = Depends(get_db)
):
    """決勝トーナメントの特定の試合結果を更新し、勝者と敗者を次の試合へ進める"""
    return services.update_tournament_match(sport, match_id, match_update.winner_id, db)

@app.get("/rankings/total/", response_model=List[schemas.TotalRanking], tags=["Rankings"])
def get_total_rankings(db: Session = Depends(get_db)):
    """全種目の結果を集計した総合得点ランキングを取得する"""
    return services.get_total_rankings(db)