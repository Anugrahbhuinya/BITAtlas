from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class NotificationPreferencesSchema(BaseModel):
    email_notifications: bool = Field(default=True, description="Enable email alerts")
    push_notifications: bool = Field(default=True, description="Enable push alerts")
    notice_updates: bool = Field(default=True, description="Enable new notice alerts")
    event_reminders: bool = Field(default=True, description="Enable campus event reminders")
    academic_alerts: bool = Field(default=True, description="Enable academic alerts")

    # Allow dynamic notification updates in the future
    model_config = ConfigDict(extra="allow")

class StudentPreferencesResponse(BaseModel):
    preferred_language: str = Field("English", description="System language selection")
    theme: str = Field("System", description="Visual theme setting")
    notifications: NotificationPreferencesSchema = Field(default_factory=lambda: NotificationPreferencesSchema())
    ai_response_style: str = Field("Detailed", description="AI responses granularity")
    default_home_page: str = Field("Dashboard", description="Initial landing page")

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

class StudentPreferencesUpdateRequest(BaseModel):
    preferred_language: str = Field(..., description="System language Selection")
    theme: str = Field(..., description="Visual theme selection")
    notifications: NotificationPreferencesSchema = Field(..., description="Notification checkboxes")
    ai_response_style: str = Field(..., description="AI response granularity selection")
    default_home_page: str = Field(..., description="Preferred landing dashboard")

    @field_validator("preferred_language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        v_strip = v.strip()
        if v_strip not in {"English", "Hindi"}:
            raise ValueError("preferred_language must be English or Hindi")
        return v_strip

    @field_validator("theme")
    @classmethod
    def validate_theme(cls, v: str) -> str:
        v_strip = v.strip()
        if v_strip not in {"Light", "Dark", "System"}:
            raise ValueError("theme must be Light, Dark, or System")
        return v_strip

    @field_validator("ai_response_style")
    @classmethod
    def validate_ai_style(cls, v: str) -> str:
        v_strip = v.strip()
        if v_strip not in {"Brief", "Detailed"}:
            raise ValueError("ai_response_style must be Brief or Detailed")
        return v_strip

    @field_validator("default_home_page")
    @classmethod
    def validate_home_page(cls, v: str) -> str:
        v_strip = v.strip()
        if v_strip not in {"Dashboard", "Chat", "Notices", "Calendar", "Profile"}:
            raise ValueError("default_home_page must be Dashboard, Chat, Notices, Calendar, or Profile")
        return v_strip

class StudentPreferencesPartialUpdateRequest(BaseModel):
    preferred_language: Optional[str] = Field(None, description="Partial language update")
    theme: Optional[str] = Field(None, description="Partial theme update")
    notifications: Optional[Dict[str, Any]] = Field(None, description="Partial notification settings toggle dictionary")
    ai_response_style: Optional[str] = Field(None, description="Partial AI response style selection")
    default_home_page: Optional[str] = Field(None, description="Partial default home page update")

    # Allow custom values for personalization extensions
    model_config = ConfigDict(extra="allow")

    @field_validator("preferred_language")
    @classmethod
    def validate_language(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v_strip = v.strip()
        if v_strip not in {"English", "Hindi"}:
            raise ValueError("preferred_language must be English or Hindi")
        return v_strip

    @field_validator("theme")
    @classmethod
    def validate_theme(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v_strip = v.strip()
        if v_strip not in {"Light", "Dark", "System"}:
            raise ValueError("theme must be Light, Dark, or System")
        return v_strip

    @field_validator("ai_response_style")
    @classmethod
    def validate_ai_style(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v_strip = v.strip()
        if v_strip not in {"Brief", "Detailed"}:
            raise ValueError("ai_response_style must be Brief or Detailed")
        return v_strip

    @field_validator("default_home_page")
    @classmethod
    def validate_home_page(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v_strip = v.strip()
        if v_strip not in {"Dashboard", "Chat", "Notices", "Calendar", "Profile"}:
            raise ValueError("default_home_page must be Dashboard, Chat, Notices, Calendar, or Profile")
        return v_strip
