"""
SQLAlchemy database models for Nigerian tourism website.

Defines core data models for destinations, services, and contact information
with comprehensive validation, relationships, and audit capabilities.
"""

import re
from datetime import datetime
from typing import Optional

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    CheckConstraint,
    Index,
    String,
    Text,
    Integer,
    Float,
    DateTime,
    Boolean,
    Enum as SQLEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property
from enum import Enum as PyEnum

db = SQLAlchemy()


class ServiceType(PyEnum):
    """Enumeration of available tourism service types."""
    ACCOMMODATION = "accommodation"
    TRANSPORTATION = "transportation"
    TOUR_GUIDE = "tour_guide"
    RESTAURANT = "restaurant"
    ACTIVITY = "activity"
    CULTURAL_EXPERIENCE = "cultural_experience"
    ADVENTURE = "adventure"
    SHOPPING = "shopping"


class ContactType(PyEnum):
    """Enumeration of contact inquiry types."""
    GENERAL = "general"
    BOOKING = "booking"
    SUPPORT = "support"
    PARTNERSHIP = "partnership"
    FEEDBACK = "feedback"


class ContactStatus(PyEnum):
    """Enumeration of contact inquiry status."""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TimestampMixin:
    """Mixin for automatic timestamp management."""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


class Destination(db.Model, TimestampMixin):
    """
    Tourism destination model.
    
    Represents tourist destinations across Nigeria with comprehensive
    information including location, description, and associated services.
    """
    
    __tablename__ = 'destinations'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        unique=True,
        index=True
    )
    slug: Mapped[str] = mapped_column(
        String(250),
        nullable=False,
        unique=True,
        index=True
    )
    state: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    short_description: Mapped[str] = mapped_column(String(500), nullable=False)
    
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    featured: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    
    visit_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    services: Mapped[list["Service"]] = relationship(
        "Service",
        back_populates="destination",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    __table_args__ = (
        CheckConstraint(
            'latitude >= -90 AND latitude <= 90',
            name='check_latitude_range'
        ),
        CheckConstraint(
            'longitude >= -180 AND longitude <= 180',
            name='check_longitude_range'
        ),
        CheckConstraint(
            'rating >= 0 AND rating <= 5',
            name='check_rating_range'
        ),
        CheckConstraint(
            'visit_count >= 0',
            name='check_visit_count_positive'
        ),
        CheckConstraint(
            "LENGTH(name) >= 3",
            name='check_name_min_length'
        ),
        CheckConstraint(
            "LENGTH(short_description) >= 20",
            name='check_short_description_min_length'
        ),
        Index('idx_destination_location', 'state', 'city'),
        Index('idx_destination_featured_active', 'featured', 'active'),
    )
    
    @validates('name')
    def validate_name(self, key: str, value: str) -> str:
        """Validate destination name."""
        if not value or not value.strip():
            raise ValueError("Destination name cannot be empty")
        
        value = value.strip()
        if len(value) < 3:
            raise ValueError("Destination name must be at least 3 characters")
        
        if len(value) > 200:
            raise ValueError("Destination name cannot exceed 200 characters")
        
        return value
    
    @validates('slug')
    def validate_slug(self, key: str, value: str) -> str:
        """Validate URL slug format."""
        if not value or not value.strip():
            raise ValueError("Slug cannot be empty")
        
        value = value.strip().lower()
        
        if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', value):
            raise ValueError(
                "Slug must contain only lowercase letters, numbers, and hyphens"
            )
        
        if len(value) > 250:
            raise ValueError("Slug cannot exceed 250 characters")
        
        return value
    
    @validates('state', 'city')
    def validate_location(self, key: str, value: str) -> str:
        """Validate location fields."""
        if not value or not value.strip():
            raise ValueError(f"{key.capitalize()} cannot be empty")
        
        value = value.strip()
        if len(value) < 2:
            raise ValueError(f"{key.capitalize()} must be at least 2 characters")
        
        return value
    
    @validates('description')
    def validate_description(self, key: str, value: str) -> str:
        """Validate description content."""
        if not value or not value.strip():
            raise ValueError("Description cannot be empty")
        
        value = value.strip()
        if len(value) < 50:
            raise ValueError("Description must be at least 50 characters")
        
        return value
    
    @validates('short_description')
    def validate_short_description(self, key: str, value: str) -> str:
        """Validate short description content."""
        if not value or not value.strip():
            raise ValueError("Short description cannot be empty")
        
        value = value.strip()
        if len(value) < 20:
            raise ValueError("Short description must be at least 20 characters")
        
        if len(value) > 500:
            raise ValueError("Short description cannot exceed 500 characters")
        
        return value
    
    @validates('image_url')
    def validate_image_url(self, key: str, value: Optional[str]) -> Optional[str]:
        """Validate image URL format."""
        if value is None:
            return value
        
        value = value.strip()
        if not value:
            return None
        
        url_pattern = re.compile(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$',
            re.IGNORECASE
        )
        
        if not url_pattern.match(value):
            raise ValueError("Invalid image URL format")
        
        return value
    
    @validates('rating')
    def validate_rating(self, key: str, value: Optional[float]) -> Optional[float]:
        """Validate rating value."""
        if value is None:
            return value
        
        if not isinstance(value, (int, float)):
            raise ValueError("Rating must be a number")
        
        if value < 0 or value > 5:
            raise ValueError("Rating must be between 0 and 5")
        
        return round(float(value), 2)
    
    @hybrid_property
    def has_coordinates(self) -> bool:
        """Check if destination has valid coordinates."""
        return self.latitude is not None and self.longitude is not None
    
    def increment_visit_count(self) -> None:
        """Increment the visit counter for analytics."""
        self.visit_count += 1
    
    def __repr__(self) -> str:
        return f"<Destination {self.name} ({self.state})>"


class Service(db.Model, TimestampMixin):
    """
    Tourism service model.
    
    Represents services available at destinations including accommodations,
    tours, restaurants, and activities.
    """
    
    __tablename__ = 'services'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    destination_id: Mapped[int] = mapped_column(
        Integer,
        db.ForeignKey('destinations.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    service_type: Mapped[str] = mapped_column(
        SQLEnum(ServiceType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    provider_name: Mapped[str] = mapped_column(String(200), nullable=False)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    website_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    price_range: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default='NGN', nullable=False)
    
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    
    destination: Mapped["Destination"] = relationship(
        "Destination",
        back_populates="services"
    )
    
    __table_args__ = (
        CheckConstraint(
            "LENGTH(name) >= 3",
            name='check_service_name_min_length'
        ),
        CheckConstraint(
            "LENGTH(description) >= 20",
            name='check_service_description_min_length'
        ),
        CheckConstraint(
            "LENGTH(currency) = 3",
            name='check_currency_code_length'
        ),
        Index('idx_service_destination_type', 'destination_id', 'service_type'),
        Index('idx_service_active_verified', 'active', 'verified'),
    )
    
    @validates('name')
    def validate_name(self, key: str, value: str) -> str:
        """Validate service name."""
        if not value or not value.strip():
            raise ValueError("Service name cannot be empty")
        
        value = value.strip()
        if len(value) < 3:
            raise ValueError("Service name must be at least 3 characters")
        
        if len(value) > 200:
            raise ValueError("Service name cannot exceed 200 characters")
        
        return value
    
    @validates('description')
    def validate_description(self, key: str, value: str) -> str:
        """Validate service description."""
        if not value or not value.strip():
            raise ValueError("Service description cannot be empty")
        
        value = value.strip()
        if len(value) < 20:
            raise ValueError("Service description must be at least 20 characters")
        
        return value
    
    @validates('provider_name')
    def validate_provider_name(self, key: str, value: str) -> str:
        """Validate provider name."""
        if not value or not value.strip():
            raise ValueError("Provider name cannot be empty")
        
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Provider name must be at least 2 characters")
        
        return value
    
    @validates('contact_phone')
    def validate_contact_phone(self, key: str, value: Optional[str]) -> Optional[str]:
        """Validate phone number format."""
        if value is None:
            return value
        
        value = value.strip()
        if not value:
            return None
        
        phone_pattern = re.compile(r'^\+?[0-9\s\-\(\)]{10,20}$')
        if not phone_pattern.match(value):
            raise ValueError("Invalid phone number format")
        
        return value
    
    @validates('contact_email')
    def validate_contact_email(self, key: str, value: Optional[str]) -> Optional[str]:
        """Validate email address format."""
        if value is None:
            return value
        
        value = value.strip().lower()
        if not value:
            return None
        
        email_pattern = re.compile(
            r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$',
            re.IGNORECASE
        )
        if not email_pattern.match(value):
            raise ValueError("Invalid email address format")
        
        return value
    
    @validates('website_url')
    def validate_website_url(self, key: str, value: Optional[str]) -> Optional[str]:
        """Validate website URL format."""
        if value is None:
            return value
        
        value = value.strip()
        if not value:
            return None
        
        url_pattern = re.compile(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$',
            re.IGNORECASE
        )
        
        if not url_pattern.match(value):
            raise ValueError("Invalid website URL format")
        
        return value
    
    @validates('currency')
    def validate_currency(self, key: str, value: str) -> str:
        """Validate currency code format."""
        if not value or not value.strip():
            raise ValueError("Currency code cannot be empty")
        
        value = value.strip().upper()
        if len(value) != 3:
            raise ValueError("Currency code must be exactly 3 characters")
        
        if not value.isalpha():
            raise ValueError("Currency code must contain only letters")
        
        return value
    
    def __repr__(self) -> str:
        return f"<Service {self.name} ({self.service_type.value})>"


class Contact(db.Model, TimestampMixin):
    """
    Contact inquiry model.
    
    Stores customer inquiries, feedback, and support requests with
    status tracking and response management.
    """
    
    __tablename__ = 'contacts'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    contact_type: Mapped[str] = mapped_column(
        SQLEnum(ContactType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True
    )
    subject: Mapped[str] = mapped_column(String(300), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    
    status: Mapped[str] = mapped_column(
        SQLEnum(ContactStatus, values_callable=lambda x: [e.value for e in x]),
        default=ContactStatus.NEW.value,
        nullable=False,
        index=True
    )
    
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    responded_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )
    response_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    __table_args__ = (
        CheckConstraint(
            "LENGTH(name) >= 2",
            name='check_contact_name_min_length'
        ),
        CheckConstraint(
            "LENGTH(subject) >= 5",
            name='check_subject_min_length'
        ),
        CheckConstraint(
            "LENGTH(message) >= 10",
            name='check_message_min_length'
        ),
        Index('idx_contact_status_created', 'status', 'created_at'),
        Index('idx_contact_type_status', 'contact_type', 'status'),
    )
    
    @validates('name')
    def validate_name(self, key: str, value: str) -> str:
        """Validate contact name."""
        if not value or not value.strip():
            raise ValueError("Name cannot be empty")
        
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Name must be at least 2 characters")
        
        if len(value) > 200:
            raise ValueError("Name cannot exceed 200 characters")
        
        return value
    
    @validates('email')
    def validate_email(self, key: str, value: str) -> str:
        """Validate email address format."""
        if not value or not value.strip():
            raise ValueError("Email cannot be empty")
        
        value = value.strip().lower()
        
        email_pattern = re.compile(
            r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$',
            re.IGNORECASE
        )
        if not email_pattern.match(value):
            raise ValueError("Invalid email address format")
        
        if len(value) > 255:
            raise ValueError("Email cannot exceed 255 characters")
        
        return value
    
    @validates('phone')
    def validate_phone(self, key: str, value: Optional[str]) -> Optional[str]:
        """Validate phone number format."""
        if value is None:
            return value
        
        value = value.strip()
        if not value:
            return None
        
        phone_pattern = re.compile(r'^\+?[0-9\s\-\(\)]{10,20}$')
        if not phone_pattern.match(value):
            raise ValueError("Invalid phone number format")
        
        return value
    
    @validates('subject')
    def validate_subject(self, key: str, value: str) -> str:
        """Validate subject line."""
        if not value or not value.strip():
            raise ValueError("Subject cannot be empty")
        
        value = value.strip()
        if len(value) < 5:
            raise ValueError("Subject must be at least 5 characters")
        
        if len(value) > 300:
            raise ValueError("Subject cannot exceed 300 characters")
        
        return value
    
    @validates('message')
    def validate_message(self, key: str, value: str) -> str:
        """Validate message content."""
        if not value or not value.strip():
            raise ValueError("Message cannot be empty")
        
        value = value.strip()
        if len(value) < 10:
            raise ValueError("Message must be at least 10 characters")
        
        return value
    
    @validates('ip_address')
    def validate_ip_address(self, key: str, value: Optional[str]) -> Optional[str]:
        """Validate IP address format."""
        if value is None:
            return value
        
        value = value.strip()
        if not value:
            return None
        
        ipv4_pattern = re.compile(
            r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
            r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        )
        ipv6_pattern = re.compile(
            r'^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
        )
        
        if not (ipv4_pattern.match(value) or ipv6_pattern.match(value)):
            raise ValueError("Invalid IP address format")
        
        return value
    
    def mark_responded(self, notes: Optional[str] = None) -> None:
        """Mark contact as responded with optional notes."""
        self.status = ContactStatus.RESOLVED.value
        self.responded_at = datetime.utcnow()
        if notes:
            self.response_notes = notes.strip()
    
    @hybrid_property
    def is_pending(self) -> bool:
        """Check if contact is pending response."""
        return self.status in (ContactStatus.NEW.value, ContactStatus.IN_PROGRESS.value)
    
    def __repr__(self) -> str:
        return f"<Contact {self.name} ({self.contact_type.value})>"