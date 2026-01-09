"""
Database models for the Nigerian Tourism Business Website.

Provides SQLAlchemy ORM models for managing tourism-related data including
destinations, bookings, and user information. Implements comprehensive data
validation, relationships, and business logic constraints.
"""

from datetime import datetime
from typing import Optional

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Text, Float, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

db = SQLAlchemy()


class Destination(db.Model):
    """
    Destination model representing Nigerian tourism locations.
    
    Stores comprehensive information about tourist destinations including
    location data, categorization, highlights, and optimal visiting periods.
    Supports filtering, search, and detailed destination views.
    """
    
    __tablename__ = 'destinations'
    
    # Primary identification
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    
    # Descriptive content
    description: Mapped[str] = mapped_column(Text, nullable=False)
    highlights: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Categorization and classification
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Geographic information
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Visiting information
    best_time_to_visit: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    # Media
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    def __repr__(self) -> str:
        """String representation of Destination instance."""
        return f'<Destination {self.name}>'
    
    def to_dict(self) -> dict:
        """
        Convert destination to dictionary representation.
        
        Returns:
            Dictionary containing all destination fields
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'highlights': self.highlights,
            'category': self.category,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'best_time_to_visit': self.best_time_to_visit,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }