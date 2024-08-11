"""
FastAPI SqlModel code from official documentation
<https://sqlmodel.tiangolo.com/tutorial/fastapi/simple-hero-api/>
"""

from fastapi import FastAPI
from sqlmodel import Field, Session, SQLModel, create_engine, select

class HeroBase(SQLModel):
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)

class Hero(HeroBase, table=True):
    id: int | None = Field(default=None,primary_key=True)

# Multiple models

class HeroCreate(HeroBase):
    pass


class HeroPublic(HeroBase):
    id: int


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Create new hero
@app.post("/heroes/", response_model=HeroPublic) # Return type is `HeroPublic`
def create_hero(hero: HeroCreate): # using the HeroCreate method
    with Session(engine) as session:
        db_hero = Hero.model_validate(hero) # validating the hero
        session.add(db_hero)
        session.commit()
        session.refresh(db_hero)
        return db_hero

@app.get("/heroes/", response_model=list[Hero]) # Response model
def read_heroes():
    with Session(engine) as session:
        heroes = session.exec(select(Hero)).all()
        return heroes