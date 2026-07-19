# Entity Type constants
ENTITY_FACULTY = "faculty"
ENTITY_DEPARTMENT = "department"
ENTITY_BUILDING = "building"
ENTITY_HOSTEL = "hostel"
ENTITY_CALENDAR = "calendar"
ENTITY_NOTICE = "notice"

# Pronoun gender mappings
MALE_PRONOUNS = ["he", "him", "his"]
FEMALE_PRONOUNS = ["she", "her", "hers"]
NEUTER_PRONOUNS = ["it", "its", "they", "them", "their", "there", "here"]

# Lexicons for Entity recognition
DEPARTMENT_KEYWORDS = [
    "cse", "ece", "eee", "mechanical", "civil", "chemical", "chemistry",
    "physics", "math", "mathematics", "architecture", "management", 
    "pharmaceutical", "production", "biotechnology", "quantitative economics", 
    "remote sensing", "space engineering", "humanities", "aiml"
]

BUILDING_KEYWORDS = [
    "central library", "library", "lecture hall complex", "lhc", 
    "r&d building", "r&d", "main building", "administrative building", 
    "seminar hall"
]

HOSTEL_KEYWORDS = [
    "aryabhatta hostel", "aryabhatta", "hostel 1", "hostel 2", "hostel 3", 
    "hostel 4", "hostel 5", "hostel 6", "hostel 7", "hostel 8", "hostel 9", 
    "hostel 10", "hostel 11", "hostel 12", "hostel 13", "kanya hostel", 
    "girls hostel"
]

CALENDAR_KEYWORDS = [
    "mid semester examination", "mid semester exams", "mid semester", "mid sem", 
    "end semester examination", "end semester exams", "end sem", "holiday", 
    "vacation", "exams", "exam"
]

NOTICE_KEYWORDS = [
    "internship notice", "placement notice", "notice", "circular"
]
