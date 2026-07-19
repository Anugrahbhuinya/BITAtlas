import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from app.services.context_resolver.constants import (
    ENTITY_FACULTY, ENTITY_DEPARTMENT, ENTITY_BUILDING, ENTITY_HOSTEL, ENTITY_CALENDAR, ENTITY_NOTICE,
    MALE_PRONOUNS, FEMALE_PRONOUNS, NEUTER_PRONOUNS,
    DEPARTMENT_KEYWORDS, BUILDING_KEYWORDS, HOSTEL_KEYWORDS, CALENDAR_KEYWORDS, NOTICE_KEYWORDS
)
from app.services.faculty_service import FacultyService

logger = logging.getLogger("conversation_context_resolver")

class ConversationContextResolver:
    def __init__(self) -> None:
        pass

    async def resolve_references(self, query: str, session_id: Optional[str]) -> Tuple[str, bool]:
        """
        Resolves conversational references in the user query based on session history.
        Returns:
        - resolved_query: The rewritten query (or original if no rewrite needed).
        - clarification_needed: True if query is ambiguous and needs clarification.
        """
        q_lower = query.lower()

        # Check if the query actually contains any pronoun/reference keywords
        pronouns_to_resolve = [
            "he", "him", "his", "she", "her", "hers", "it", "its", "they", "them", 
            "their", "this professor", "this faculty", "this teacher", "this department",
            "that building", "this hostel", "this notice", "that event", "there", "here",
            "the above", "the previous one", "the same faculty"
        ]
        
        has_pronoun = any(re.search(r"\b" + re.escape(p) + r"\b", q_lower) for p in pronouns_to_resolve)
        
        # Check for implicit attribute queries
        has_implicit_dept = ("hod" in q_lower or "head" in q_lower) and not any(kw in q_lower for kw in DEPARTMENT_KEYWORDS)
        has_implicit_notice = ("deadline" in q_lower or "last date" in q_lower or "due date" in q_lower) and not any(kw in q_lower for kw in NOTICE_KEYWORDS)
        
        if not has_pronoun and not has_implicit_dept and not has_implicit_notice:
            return query, False

        # Load session history
        history = []
        if session_id:
            try:
                from app.services.history_service import get_chat_history
                history = await get_chat_history(session_id)
            except Exception as e:
                logger.error(f"Error fetching chat history for reference resolution: {e}")

        # Check if this is a plural/subset filter query (e.g. "Who among them...") with an existing list in metadata.
        # If so, let the downstream router handle the filtering.
        is_plural_filter = any(re.search(r"\b" + re.escape(p) + r"\b", q_lower) for p in ["them", "their", "they"])
        has_previous_list = False
        if history:
            last_msg = None
            for msg in reversed(history):
                if msg.get("role") == "assistant":
                    last_msg = msg
                    break
            if last_msg and last_msg.get("metadata") and last_msg["metadata"].get("faculty_ids"):
                has_previous_list = True

        if is_plural_filter and has_previous_list:
            logger.info("Plural reference detected with existing faculty list context. Bypassing resolver for downstream subset filtering.")
            return query, False

        # Scan history and build entity memory
        entities = self._scan_history_for_entities(history)
        if not entities:
            # Pronoun present but no context in history
            if has_pronoun:
                # Neuter pronouns (it, its) can sometimes be generic, but singular personal pronouns are ambiguous without context
                is_personal = any(re.search(r"\b" + re.escape(p) + r"\b", q_lower) for p in MALE_PRONOUNS + FEMALE_PRONOUNS + ["this professor", "this faculty", "this teacher", "the same faculty"])
                if is_personal:
                    logger.info("Reference pronoun detected but no entity context exists in history.")
                    return "Could you clarify which faculty member you mean?", True
            return query, False

        # Group entities by type
        entities_by_type = {}
        for ent in entities:
            t = ent["type"]
            if t not in entities_by_type:
                entities_by_type[t] = []
            entities_by_type[t].append(ent)

        # 1. Resolve Faculty references
        is_faculty_pronoun = any(re.search(r"\b" + re.escape(p) + r"\b", q_lower) for p in MALE_PRONOUNS + FEMALE_PRONOUNS + ["this professor", "this faculty", "this teacher", "the same faculty"])
        if is_faculty_pronoun:
            faculty_list = entities_by_type.get(ENTITY_FACULTY, [])
            if not faculty_list:
                return "Could you clarify which faculty member you mean?", True

            # Disambiguate by gender if applicable
            has_female_pronoun = any(re.search(r"\b" + re.escape(p) + r"\b", q_lower) for p in FEMALE_PRONOUNS)
            has_male_pronoun = any(re.search(r"\b" + re.escape(p) + r"\b", q_lower) for p in MALE_PRONOUNS)

            # Filter candidates by gender match
            candidates = []
            if has_female_pronoun:
                candidates = [f for f in faculty_list if f.get("gender") == "female"]
            elif has_male_pronoun:
                candidates = [f for f in faculty_list if f.get("gender") == "male"]
            else:
                candidates = faculty_list

            # Remove duplicate names in the candidate list while preserving order
            unique_candidates = []
            seen_names = set()
            for cand in candidates:
                if cand["name"] not in seen_names:
                    unique_candidates.append(cand)
                    seen_names.add(cand["name"])

            if len(unique_candidates) > 1:
                # If we have multiple candidates of the same gender matching the pronoun, ask for clarification
                logger.info(f"Ambiguity detected: multiple faculty candidates matching pronoun: {unique_candidates}")
                return "Could you clarify which faculty member you mean?", True
            elif len(unique_candidates) == 1:
                target_faculty = unique_candidates[0]
                rewritten = self._rewrite_faculty_query(query, target_faculty["name"])
                logger.info(f"Query rewritten: '{query}' -> '{rewritten}' using entity: '{target_faculty['name']}'")
                return rewritten, False
            else:
                # Pronoun doesn't match any candidates (e.g. female pronoun but only male candidates)
                return "Could you clarify which faculty member you mean?", True

        # 2. Resolve Department references
        if has_implicit_dept or any(p in q_lower for p in ["this department", "that department"]):
            depts = entities_by_type.get(ENTITY_DEPARTMENT, [])
            if depts:
                # Resolve to the most recent department
                target = depts[0]["name"]
                clean_q = query.strip().rstrip("?").rstrip(".")
                return f"{clean_q} of the {target}?", False

        # 3. Resolve Notice references
        if has_implicit_notice or any(p in q_lower for p in ["this notice", "that notice"]):
            notices = entities_by_type.get(ENTITY_NOTICE, [])
            if notices:
                target = notices[0]["name"]
                clean_q = query.strip().rstrip("?").rstrip(".")
                return f"{clean_q} of the {target}?", False

        # 4. Resolve Building / Hostel / Calendar references (Neuter Pronouns)
        if any(re.search(r"\b" + re.escape(p) + r"\b", q_lower) for p in NEUTER_PRONOUNS):
            # Prioritize Hostel or Building if close/Wi-Fi keywords are matched
            if "close" in q_lower or "open" in q_lower or "located" in q_lower or "where" in q_lower:
                buildings = entities_by_type.get(ENTITY_BUILDING, [])
                if buildings:
                    return self._rewrite_neuter_query(query, buildings[0]["name"]), False
            if "wi-fi" in q_lower or "wifi" in q_lower or "mess" in q_lower or "room" in q_lower:
                hostels = entities_by_type.get(ENTITY_HOSTEL, [])
                if hostels:
                    return self._rewrite_neuter_query(query, hostels[0]["name"]), False

            # General neuter fallback (Building -> Hostel -> Calendar)
            for t in [ENTITY_BUILDING, ENTITY_HOSTEL, ENTITY_CALENDAR]:
                items = entities_by_type.get(t, [])
                if items:
                    return self._rewrite_neuter_query(query, items[0]["name"]), False

        return query, False

    def _scan_history_for_entities(self, history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Scans history from newest to oldest and extracts discussed entities.
        """
        entities = []
        all_faculty = FacultyService.get_all()

        for msg in reversed(history):
            content = msg.get("content", "")
            role = msg.get("role", "")
            if not content:
                continue

            content_lower = content.lower()

            # 1. Faculty Names
            for f in all_faculty:
                name = f["name"]
                norm_name = name.lower()
                # Check for full name or last name tokens
                name_parts = [p for p in norm_name.split() if len(p) > 2]
                matched = False
                if norm_name in content_lower:
                    matched = True
                elif name_parts and all(part in content_lower for part in name_parts):
                    matched = True

                if matched:
                    # Deduce gender from text or pre-mapped database check
                    gender = "male"
                    if " she " in content_lower or " her " in content_lower:
                        gender = "female"
                    elif name in ["Vandana Bhattacharjee", "Anjali Pathak", "Anjali"]:
                        gender = "female"
                    
                    entities.append({
                        "type": ENTITY_FACULTY,
                        "name": name,
                        "gender": gender,
                        "id": f["id"]
                    })

            # 2. Departments
            for kw in DEPARTMENT_KEYWORDS:
                if re.search(r"\b" + re.escape(kw) + r"\b", content_lower):
                    entities.append({
                        "type": ENTITY_DEPARTMENT,
                        "name": f"{kw.upper()} Department"
                    })

            # 3. Buildings
            for kw in BUILDING_KEYWORDS:
                if kw in content_lower:
                    entities.append({
                        "type": ENTITY_BUILDING,
                        "name": kw.title()
                    })

            # 4. Hostels
            for kw in HOSTEL_KEYWORDS:
                if kw in content_lower:
                    entities.append({
                        "type": ENTITY_HOSTEL,
                        "name": kw.title()
                    })

            # 5. Calendar
            for kw in CALENDAR_KEYWORDS:
                if kw in content_lower:
                    entities.append({
                        "type": ENTITY_CALENDAR,
                        "name": kw.title()
                    })

            # 6. Notices
            for kw in NOTICE_KEYWORDS:
                if kw in content_lower:
                    entities.append({
                        "type": ENTITY_NOTICE,
                        "name": f"{kw} notice"
                    })

        return entities

    def _rewrite_faculty_query(self, query: str, name: str) -> str:
        q_lower = query.lower()
        # Clean prefix if the name contains honorifics
        clean_name = name
        if clean_name.lower().startswith("dr."):
            clean_name = clean_name[3:].strip()
        elif clean_name.lower().startswith("dr "):
            clean_name = clean_name[2:].strip()

        display_name = f"Dr. {clean_name}"

        # Resolve pronouns
        if re.search(r"\bher\b", q_lower):
            query = re.sub(r"\bher\b", f"{display_name}'s", query, flags=re.IGNORECASE)
        elif re.search(r"\bhis\b", q_lower):
            query = re.sub(r"\bhis\b", f"{display_name}'s", query, flags=re.IGNORECASE)
        elif re.search(r"\bshe\b", q_lower):
            query = re.sub(r"\bshe\b", display_name, query, flags=re.IGNORECASE)
        elif re.search(r"\bhe\b", q_lower):
            query = re.sub(r"\bhe\b", display_name, query, flags=re.IGNORECASE)
        elif re.search(r"\bhim\b", q_lower):
            query = re.sub(r"\bhim\b", display_name, query, flags=re.IGNORECASE)
        elif re.search(r"\bthis professor\b|\bthis faculty\b|\bthis teacher\b|\bthe same faculty\b", q_lower):
            query = re.sub(r"\bthis professor\b|\bthis faculty\b|\bthis teacher\b|\bthe same faculty\b", display_name, query, flags=re.IGNORECASE)

        return query

    def _rewrite_neuter_query(self, query: str, name: str) -> str:
        q_lower = query.lower()
        if re.search(r"\bit\b", q_lower):
            query = re.sub(r"\bit\b", name, query, flags=re.IGNORECASE)
        elif re.search(r"\bits\b", q_lower):
            query = re.sub(r"\bits\b", f"{name}'s", query, flags=re.IGNORECASE)
        elif re.search(r"\bthey\b", q_lower):
            query = re.sub(r"\bthey\b", name, query, flags=re.IGNORECASE)
        elif re.search(r"\bthem\b", q_lower):
            query = re.sub(r"\bthem\b", name, query, flags=re.IGNORECASE)
        elif re.search(r"\bthere\b", q_lower):
            query = re.sub(r"\bthere\b", f"at {name}", query, flags=re.IGNORECASE)
        elif re.search(r"\bhere\b", q_lower):
            query = re.sub(r"\bhere\b", f"at {name}", query, flags=re.IGNORECASE)
        return query
