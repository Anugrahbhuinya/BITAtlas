# backend/app/navigation/constants.py

from enum import Enum

class RoomType(str, Enum):
    CLASSROOM = "Classroom"
    LABORATORY = "Laboratory"
    SEMINAR_HALL = "Seminar Hall"
    FACULTY_OFFICE = "Faculty Office"
    ADMINISTRATIVE_OFFICE = "Administrative Office"
    AUDITORIUM = "Auditorium"
    LIBRARY_ROOM = "Library Room"
    CONFERENCE_ROOM = "Conference Room"

class BuildingCategory(str, Enum):
    ACADEMIC = "Academic"
    ADMINISTRATIVE = "Administrative"
    RESIDENTIAL = "Residential"
    STUDENT_SERVICES = "Student Services"
    SPORTS = "Sports"
    RESEARCH = "Research"
    OTHER = "Other"

class LandmarkCategory(str, Enum):
    GATE = "Gate"
    TOWER = "Tower"
    LAWN = "Lawn"
    STATUE = "Statue"
    FOUNTAIN = "Fountain"
    OTHER = "Other"

class FacilityCategory(str, Enum):
    CAFETERIA = "Cafeteria"
    ATM = "ATM"
    XEROX = "Xerox"
    MEDICAL_CENTRE = "Medical Centre"
    BANK = "Bank"
    PARKING = "Parking"
    BUS_STOP = "Bus Stop"
    SPORTS_COMPLEX = "Sports Complex"
    OTHER = "Other"

class PathType(str, Enum):
    WALKWAY = "walkway"
    CORRIDOR = "corridor"
    ROAD = "road"
    STAIRCASE = "staircase"
    ELEVATOR = "elevator"

class SurfaceType(str, Enum):
    ASPHALT = "asphalt"
    CONCRETE = "concrete"
    GRASS = "grass"
    TILE = "tile"
    DIRT = "dirt"

class LightingLevel(str, Enum):
    EXCELLENT = "excellent"
    MODERATE = "moderate"
    NONE = "none"
