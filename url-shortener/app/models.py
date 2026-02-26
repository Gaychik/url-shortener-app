from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    links = relationship("Link", back_populates="owner")

class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, index=True, nullable=False)
    short_code = Column(String, unique=True, index=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expiration_date = Column(DateTime(timezone=True), nullable=True)

    owner = relationship("User", back_populates="links")
    clicks = relationship("Click", back_populates="link")
    
    @property
    def total_clicks(self):
        """Возвращает количество кликов для этой ссылки."""
        return len(self.clicks) if self.clicks else 0
    
    @property
    def total_clicks(self):
        """Возвращает количество кликов для этой ссылки."""
        return len(self.clicks) if self.clicks else 0


class Click(Base):
    __tablename__ = "clicks"

    id = Column(Integer, primary_key=True, index=True)
    link_id = Column(Integer, ForeignKey("links.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    country = Column(String, nullable=True)
    device = Column(String, nullable=True) # Можно будет определять из User-Agent

    link = relationship("Link", back_populates="clicks")
