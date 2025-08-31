import enum
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "sqlite:///../class_match.db"
Base = declarative_base()

class SportName(str, enum.Enum):
    VOLLEYBALL = "バレー"
    MEN_BASKETBALL = "男バス"
    WOMEN_BASKETBALL = "女バス"
    SOFTBALL = "ソフトボール"
    SOCCER = "サッカー"
    TABLE_TENNIS = "卓球"
    BADMINTON = "バドミントン"
    EXTRA = "臨時得点"


class LeagueName(str, enum.Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class SchoolClass(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

#予選
class LeagueMatch(Base):
    __tablename__ = "league_matches"
    id = Column(Integer, primary_key=True, index=True)
    sport = Column(Enum(SportName))
    league = Column(Enum(LeagueName))

    # 対戦クラス
    class1_id = Column(Integer, ForeignKey("classes.id"))
    class2_id = Column(Integer, ForeignKey("classes.id"))

    # 得点 (バレー・バスケ・サッカー用)
    class1_score = Column(Integer, default=0)
    class2_score = Column(Integer, default=0)

    # セットカウント（バドミントン・卓球）
    class1_sets_won = Column(Integer, default=0)
    class2_sets_won = Column(Integer, default=0)

    winner_id = Column(Integer, ForeignKey("classes.id"), nullable=True)

    class1 = relationship("SchoolClass", foreign_keys=[class1_id])
    class2 = relationship("SchoolClass", foreign_keys=[class2_id])
    winner = relationship("SchoolClass", foreign_keys=[winner_id])

#決勝
class TournamentMatch(Base):
    __tablename__ = "tournament_matches"
    id = Column(Integer, primary_key=True, index=True)
    sport = Column(Enum(SportName)) # 種目名
    match_name = Column(String) # 試合名 (例: "E1", "E7", "3位決定戦")

    # 対戦クラス
    class1_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    class2_id = Column(Integer, ForeignKey("classes.id"), nullable=True)

    # どのクラスが勝ったか
    winner_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    
    class1 = relationship("SchoolClass", foreign_keys=[class1_id])
    class2 = relationship("SchoolClass", foreign_keys=[class2_id])
    winner = relationship("SchoolClass", foreign_keys=[winner_id])


# dbの生成
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_db()
    print("OK")