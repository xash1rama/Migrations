from sqlalchemy import create_engine, String, Integer, Column, Boolean, JSON, ForeignKey, Sequence,ARRAY as Array
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

engine = create_engine("postgresql+psycopg2://admin:admin@postgres_container:5432/app_db")
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class Coffee(Base):
    __tablename__ = "coffee"
    id:int = Column(Integer, primary_key=True, nullable=False)
    title:str = Column(String(200), nullable=False)
    origin:str = Column(String(200))
    intensifier:str = Column(String(100))
    notes:str = Column(Array(String))

    # test_A:str = Column(String)
    test_B:str = Column(String)

    user = relationship("User", back_populates="coffee",
                          lazy="select",
                          cascade="all")

    def __repr__(self):
        return f"coffe {self.title} from {self.origin}"

    def to_json(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}



class User(Base):
    __tablename__ = "users"
    id: int = Column(Integer, Sequence("user_id_seq"), primary_key=True, nullable=False)
    name: str = Column(String(50), nullable=False)
    has_sale:bool = Column(Boolean)
    address = Column(JSON)
    coffee_id:int = Column(Integer, ForeignKey("coffee.id"))
    surname:str = Column(String)

    coffee = relationship("Coffee", back_populates="user",
                          lazy="select",
                          cascade="all")

    def __repr__(self):
        res = "'coffee not selected.'"
        if self.coffee_id:
            res = self.coffee.title

        return f"User {self.name} likes coffee {res}"

    def to_json(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}