from pydantic import BaseModel
from typing import List, Optional
from models import SportName, LeagueName

class SchoolClassBase(BaseModel):
    name: str

class SchoolClassCreate(SchoolClassBase):
    pass

class SchoolClass(SchoolClassBase):
    id: int

    class Config:
        orm_mode = True

# --- 予選リーグの試合結果 ---
class LeagueMatchBase(BaseModel):
    sport: SportName
    league: LeagueName
    class1_id: int
    class2_id: int
    class1_score: Optional[int] = 0
    class2_score: Optional[int] = 0
    class1_sets_won: Optional[int] = 0
    class2_sets_won: Optional[int] = 0
    winner_id: int

class LeagueMatchCreate(LeagueMatchBase):
    pass

class LeagueMatch(LeagueMatchBase):
    id: int
    class1: SchoolClass
    class2: SchoolClass
    winner: SchoolClass

    class Config:
        orm_mode = True

# --- リーグ順位 ---
class LeagueStanding(BaseModel):
    rank: int
    class_id: int
    class_name: str
    wins: int
    losses: int
    sets_won_points: int
    league_points: int

    class Config:
        orm_mode = True

# 結晶
class TournamentMatchBase(BaseModel):
    sport: SportName
    match_name: str

class TournamentMatchCreate(TournamentMatchBase):
    class1_id: Optional[int] = None
    class2_id: Optional[int] = None

class TournamentMatch(TournamentMatchBase):
    id: int
    class1: Optional[SchoolClass] = None
    class2: Optional[SchoolClass] = None
    winner: Optional[SchoolClass] = None

    class Config:
        orm_mode = True

class TournamentMatchUpdate(BaseModel):
    winner_id: int

class TotalRanking(BaseModel):
    rank: int
    class_id: int
    class_name: str
    total_points: int
    league_points_details: dict
    tournament_points_details: dict