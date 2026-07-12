from typing import List, Dict

class FewShotExample:
    """
    Holds a single query and response pair for few-shot learning.
    """
    def __init__(self, question: str, answer: str):
        self.question = question
        self.answer = answer

    def to_string(self) -> str:
        return f"User Query: {self.question}\nExpected Response:\n{self.answer}"

class FewShotEngine:
    """
    Repository for few-shot examples, grouped by intent (academic, navigation, etc.).
    Extracts relevant examples up to a limit to prevent token bloat.
    """
    def __init__(self):
        self.examples: Dict[str, List[FewShotExample]] = {}
        self._load_default_examples()

    def _load_default_examples(self):
        # 1. Academic Examples
        self.examples["academic"] = [
            FewShotExample(
                question="What is the CGPA required to stay out of academic probation?",
                answer="""According to the BIT Mesra Academic Guidelines, a student must maintain a minimum CGPA of 5.0. If your CGPA falls below 5.0, you will be placed on academic probation.
[Source: Academic Regulations 2024, Page: 18]"""
            ),
            FewShotExample(
                question="How can I apply for a branch change after the first year?",
                answer="""Branch changes are permitted after the second semester. You must have passed all subjects in the first attempt with a minimum CGPA of 8.5. Applications open in July after the declaration of spring semester results.
[Source: Branch Change Notification, Page: 2]"""
            )
        ]

        # 2. Navigation Examples
        self.examples["navigation"] = [
            FewShotExample(
                question="Where is LH-2 and how do I get there from Hostel 3?",
                answer="""LH-2 (Lecture Hall 2) is in the Main Lecture Hall Complex.
Estimated Walking Time: ~6 minutes (distance ~400m).
Route: Walk east out of Hostel 3, turn left at the main avenue, and follow the signs towards the Lecture Hall Complex.
Landmarks: Right behind the Administrative Building."""
            ),
            FewShotExample(
                question="My class starts in 5 minutes. I am at the library and need to reach RIC-204. Will I be late?",
                answer="""Yes, you might be slightly late. RIC-204 is in the Research & Innovation Center, which is about a 7-minute walk (~500m) from the Library. If you leave now, you will arrive in approximately 7 minutes."""
            )
        ]

        # 3. Planner Examples
        self.examples["planner"] = [
            FewShotExample(
                question="Show me my study tasks for this week.",
                answer="""Here are your scheduled study tasks for this week:
- Quiz 1 (Database Management Systems): July 8, 10:00 AM (Priority: High)
- Assignment 1 (Software Engineering): July 11, 11:59 PM (Priority: Medium)
Consider allocating time tonight to review ER diagrams."""
            )
        ]

        # 4. Attendance Examples
        self.examples["attendance"] = [
            FewShotExample(
                question="My attendance is 71% (15 out of 21 lectures) in Mathematics. How many classes to reach 75%?",
                answer="""Your current attendance is 71.4%. To cross the 75.0% threshold, you need to attend the next 3 lectures consecutively without bunking. This will raise your attendance to 75.0% (18 out of 24)."""
            ),
            FewShotExample(
                question="Can I bunk next week's Physics class? My current attendance is 80% (16/20).",
                answer="""Bunking next week's lecture (assuming 1 class per week) will drop your attendance to 76.1% (16 out of 21). You will stay above the 75% minimum, but it is highly recommended to attend to keep a buffer."""
            )
        ]

        # 5. General Examples
        self.examples["general"] = [
            FewShotExample(
                question="How do I contact Hostel 14 warden?",
                answer="""Hostel 14 Warden's office is located near the hostel entrance.
Office Hours: 4:00 PM - 6:00 PM (Monday-Friday)
Email: warden.h14@bitmesra.ac.in.
For urgent maintenance, contact the hostel clerk directly in the office."""
            )
        ]

        # 6. RAG Examples
        self.examples["rag"] = [
            FewShotExample(
                question="What is the late fee for monsoon semester registration?",
                answer="""The late registration fee for the monsoon semester is Rs. 1000 if registered during the extended window (typically 5 days after the deadline).
[Source: Registration Notice 2024, Page: 1]"""
            )
        ]

    def get_examples(self, intent: str, limit: int = 1) -> str:
        """
        Retrieves the top few-shot examples for the given intent.
        Returns a formatted text string containing the examples.
        """
        intent_key = intent.lower()
        intent_examples = self.examples.get(intent_key, self.examples.get("general", []))

        if not intent_examples:
            return ""

        # Limit to prevent prompt token bloat
        selected = intent_examples[:limit]
        formatted = []
        for idx, ex in enumerate(selected, 1):
            formatted.append(f"### Example {idx}\n{ex.to_string()}")

        return "\n\n".join(formatted)
