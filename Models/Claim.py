from sqlalchemy import Column, Integer, String
from Misc.database import Base

class Claim(Base):
    __tablename__ = 'Claim'
    id = Column(Integer, primary_key = True)
    file_loc = Column(String(500))
    amount = Column(Integer, default = 0)
    status_id = Column(String(50))
    user_id = Column(Integer)

    def __repr__(self):
        return("<Claim(id = {self.id}, file_loc = {self.file_loc}, amount = {self.amount}, status = {self.status}, user_id = {self.user_id})>").format(self = self)

class ClaimConversations(Base):
    __tablename__ = 'ClaimConversations'
    id = Column(Integer, primary_key = True)
    claim_id = Column(Integer, nullable = False)
    message = Column(String(1000))
    user_id = Column(Integer)
    status = Column(String(50))

    def __repr__(self):
        return("<ClaimConversations(id = {self.id}, claim_id = {self.claim_id}, message = {self.message}, user_id = {self.user_id}, status = {self.status})>").format(self = self)
