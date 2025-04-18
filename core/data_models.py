# core/models.py

from pydantic import BaseModel, Field, field_validator, ConfigDict, HttpUrl

from typing import List, Optional

from datetime import datetime

from dateutil import parser


class UserPreferences(BaseModel):
    industry: str = Field(
        ...,
        description="Startup industry (e.g. 'fintech', 'healthtech')"
    )

    location: str = Field(
        ...,
        description="Human-readable location (e.g. 'New York, NY')"
    )

    stage: str = Field(
        ...,
        description="Funding stage (e.g. 'seed', 'series A')"
    )

    available_dates: List[datetime] = Field(
        ...,
        description="List of dates/times when the founder is free"
    )

    @field_validator('available_dates', mode='before')
    def parse_dates(cls, v):
        if isinstance(v, list):
            parsed = []
            for item in v:
                if isinstance(item, datetime):
                    parsed.append(item)
                else:
                    try:
                        parsed.append(parser.isoparse(item))
                    except Exception:
                        raise ValueError(f"Could not parse date: {item!r}")
            return parsed
        if isinstance(v, datetime):
            return [v]
        try:
            return [parser.isoparse(v)]
        except Exception:
            raise ValueError(f"Could not parse date: {v!r}")

    # Pydantic v2 JSON encoder config
    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()}
    )


class InvestorProfile(BaseModel):
    name: str = Field(..., description="Investor's name")
    location: str = Field(..., description="Investor's location")
    interests: List[str] = Field(..., description="Investor's areas of interest")
    profile_url: Optional[HttpUrl] = Field(None, description="Link to investor profile")


class Event(BaseModel):
    name: str = Field(..., description="Event or meetup name")
    date: datetime = Field(..., description="Date and time of the event")
    location: str = Field(..., description="Event location")
    description: Optional[str] = Field(None, description="Brief description of the event")
    event_url: Optional[HttpUrl] = Field(None, description="Link to event details")


class Coordinates(BaseModel):
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")


class CommuteInfo(BaseModel):
    origin: Coordinates = Field(..., description="Starting coordinates")
    destination: Coordinates = Field(..., description="Destination coordinates")
    travel_time_minutes: int = Field(..., description="Estimated travel time in minutes")
    distance_km: float = Field(..., description="Distance in kilometers")


class MeetingSlot(BaseModel):
    participant: str = Field(..., description="Meeting participant (investor or event)")
    start_time: datetime = Field(..., description="Start time of the meeting")
    end_time: datetime = Field(..., description="End time of the meeting")
    location: Coordinates = Field(..., description="Coordinates of the meeting location")
    commute: Optional[CommuteInfo] = Field(None, description="Commute information")


class Schedule(BaseModel):
    slots: List[MeetingSlot] = Field(..., description="List of scheduled meeting slots")


class SchedulingRequest(BaseModel):
    user: UserPreferences = Field(..., description="Founder preferences")
    investors: List[InvestorProfile] = Field(..., description="List of investors to consider")
    events: List[Event] = Field(..., description="List of events to consider")

