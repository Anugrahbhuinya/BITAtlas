from typing import Dict

class ResponseFormatter:
    """
    Automatically injects structured markdown layout instructions into the prompt
    based on the active intent, guaranteeing standard response sections in the UI.
    """
    def __init__(self):
        self.formats: Dict[str, str] = {
            "academic": """RESPONSE STRUCTURE REQUIRED:
Your response MUST be organized under these exact headings:
### Title
[A short title summarizing the topic]

### Answer
[Your detailed answer with proper markdown formatting and source citations]

### Sources
[A list of the exact source documents, PDFs, or websites and page numbers used to construct the answer]

### Suggestions
[Recommended next actions for the student (e.g., contact specific dean, visit ERP, apply before a deadline)]""",

            "navigation": """RESPONSE STRUCTURE REQUIRED:
Your response MUST be organized under these exact headings:
### Destination
[Name of the target building, lecture hall, lab, or office]

### Walking Time
[Estimated walking time and distance, e.g., ~5 minutes (approx. 350m)]

### Directions
[Clear step-by-step walking path from current location, including accessibility guidelines if requested]

### Landmarks
[Noteworthy gates, structures, or departments along the route to assist navigation]""",

            "planner": """RESPONSE STRUCTURE REQUIRED:
Your response MUST be organized under these exact headings:
### Tasks
[A checklist of study tasks, assignments, or quizzes to complete]

### Priority
[Critical tasks or deadlines that need immediate attention]

### Deadlines
[Exact dates/times for submissions, quizzes, or exams]""",

            "general": """RESPONSE STRUCTURE REQUIRED:
Your response MUST be organized under these exact headings:
### Summary
[A concise 1-2 sentence overview of the answer]

### Details
[In-depth details, bullet points, names, numbers, or specific instructions]

### Next Actions
[Actionable suggestions for the student to follow up on]""",

            "attendance": """RESPONSE STRUCTURE REQUIRED:
Your response MUST be organized under these exact headings:
### Current Attendance
[Subject-wise breakdown of attendance percentage, lectures attended, and total lectures]

### Bunk Advisor
[Detailed calculation of how many lectures can be safely skipped or must be attended consecutively]

### Recommendations
[Steps the student should take next to address attendance issues]"""
        }

    def get_formatting_instructions(self, intent: str) -> str:
        """
        Retrieves the exact markdown formatting template for the selected intent.
        Defaults to the 'general' intent format.
        """
        intent_key = intent.lower()
        if intent_key == "rag":
            # RAG uses academic structure by default
            intent_key = "academic"
            
        return self.formats.get(intent_key, self.formats.get("general", ""))
