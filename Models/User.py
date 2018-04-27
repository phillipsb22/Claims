from sqlalchemy import Column, Integer, String
from Misc.database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(500))
    email = Column(String(500))
    token = Column(String(1000))
    admin = Column(Integer, default = 0)

    #additionally encrypt id so that we dont pass clear text ids

    def __repr__(self):
        return ("<User(public_id = {self.public_id}, name = {self.name}, email = {self.email}, admin = {self.admin})>").format(self = self)
