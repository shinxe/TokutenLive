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


# --- リーグ所属チーム ---
class LeagueTeamBase(BaseModel):
    sport: SportName
    league: LeagueName
    class_id: int

class LeagueTeamCreate(LeagueTeamBase):
    pass

class LeagueTeam(LeagueTeamBase):
    id: int
    school_class: SchoolClass

    class Config:
        orm_mode = True


class LeagueTeamDelete(BaseModel):
    sport: SportName
    league: LeagueName
    class_id: int


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
    winner_id: Optional[int] = None

class LeagueMatchCreate(LeagueMatchBase):
    pass

class LeagueMatch(LeagueMatchBase):
    id: int
    is_finished: bool
    class1: SchoolClass
    class2: SchoolClass
    winner: Optional[SchoolClass] = None

    class Config:
        orm_mode = True

# --- リーグ順位 ---
class LeagueStanding(BaseModel):
    rank: int
    class_id: int
    class_name: str
    wins: int
    losses: int
    ties: int
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
    class1_score: Optional[int] = None
    class2_score: Optional[int] = None
    class1_sets_won: Optional[int] = None
    class2_sets_won: Optional[int] = None
    is_finished: bool

    class Config:
        orm_mode = True

class TournamentMatchUpdate(BaseModel):
    winner_id: int
    class1_score: Optional[int] = None
    class2_score: Optional[int] = None
    class1_sets_won: Optional[int] = None
    class2_sets_won: Optional[int] = None

class TotalRanking(BaseModel):
    rank: int
    class_id: int
    class_name: str
    total_points: int
    league_points_details: dict
    tournament_points_details: dict

class LeagueMatchUpdate(BaseModel):
    class1_score: int
    class2_score: int
    class1_sets_won: int
    class2_sets_won: int
    winner_id: Optional[int] = None