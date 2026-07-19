import logging
import re
from typing import Dict, Any, List, Optional
from app.services.routing.constants import (
    FACULTY_DIRECTORY, WEBSITE_KNOWLEDGE_BASE,
    STATUS_FOUND, STATUS_NOT_APPLICABLE, STATUS_NOT_FOUND, STATUS_ERROR
)
from app.services.routing.extractor import FacultyQueryExtractor
from app.services.routing.rules import RoutingRules
from app.services.faculty_service import FacultyService

logger = logging.getLogger("faculty_query_router")

class FacultyQueryRouter:
    def __init__(self) -> None:
        pass

    async def route_query(
        self,
        query: str,
        previous_faculty_ids: Optional[List[str]] = None,
        last_assistant_msg: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main entry point to route a faculty-related query.
        Determines the target entity and requested attribute, then searches
        appropriate datasources with internal fallback logic.
        """
        logger.info(f"Routing query: '{query}' with previous_faculty_ids: {previous_faculty_ids}")

        # 1. Check for suggestion affirmation follow-up first
        entity = None
        last_assistant_text = last_assistant_msg.get("content", "") if last_assistant_msg else ""
        
        def is_affirmative(text: str) -> bool:
            clean = text.lower().strip().replace(".", "").replace("!", "").replace(",", "")
            return clean in ["yes", "yeah", "yup", "yes please", "sure", "correct", "that is correct", "indeed", "right", "that is right", "yes he is", "yes she is"]

        if previous_faculty_ids and len(previous_faculty_ids) == 1 and "did you mean" in last_assistant_text.lower() and is_affirmative(query):
            entity = FacultyService.get_by_id(previous_faculty_ids[0])
            logger.info(f"Resolved entity '{entity.get('name')}' from suggestion affirmation.")

        # 2. Check for suggestion/clarification message from Name Resolver for new queries
        if not entity and not previous_faculty_ids:
            try:
                from app.services.faculty.resolver import FacultyNameResolver
                resolution = FacultyNameResolver.resolve(query)
                if resolution.get("message") and ("did you mean" in resolution["message"].lower() or "which one did you mean" in resolution["message"].lower()):
                    logger.info("Resolver returned suggestion or clarification message.")
                    return {
                        "status": STATUS_FOUND,
                        "answer": resolution["message"],
                        "faculty_ids": [m["id"] for m in resolution.get("candidates", [])]
                    }
                if resolution.get("candidates"):
                    entity = resolution["candidates"][0]
            except Exception as e:
                logger.error(f"Error checking name resolver in router: {e}")

        # 3. Fallback to previous faculty context if entity not set
        if not entity and previous_faculty_ids:
            try:
                entity = FacultyService.get_by_id(previous_faculty_ids[0])
                logger.info(f"Fallback resolved entity '{entity.get('name')}' from history context.")
            except Exception as e:
                logger.error(f"Error fetching faculty by context ID '{previous_faculty_ids[0]}': {e}")

        # 4. Fallback to extractor if still no entity
        if not entity:
            entity = FacultyQueryExtractor.extract_entity(query)

        if not entity:
            logger.info("No faculty entity could be extracted from query.")
            return {
                "status": STATUS_NOT_FOUND,
                "answer": "I couldn't find any faculty member matching your request.",
                "faculty_ids": []
            }

        # 5. Attribute Extraction
        attribute_type = FacultyQueryExtractor.extract_attribute(query)
        logger.info(f"Extracted entity: '{entity.get('name')}', attribute type: '{attribute_type}'")

        # 6. Get Datasource Priority
        priority = RoutingRules.get_datasource_priority(attribute_type)
        logger.info(f"Datasource execution priority: {priority}")

        # 7. Execute Datasources in Priority Order
        for datasource in priority:
            if datasource == FACULTY_DIRECTORY:
                res = self._execute_faculty_directory(query, entity, attribute_type)
                if res["status"] == STATUS_FOUND:
                    logger.info("Answer resolved successfully via Faculty Directory.")
                    return res
                else:
                    logger.info(f"Faculty Directory returned {res['status']}. Trying next datasource.")
            elif datasource == WEBSITE_KNOWLEDGE_BASE:
                res = await self._execute_website_knowledge_base(query, entity)
                if res["status"] == STATUS_FOUND:
                    logger.info("Answer resolved successfully via Website Knowledge Base.")
                    return res
                else:
                    logger.info(f"Website Knowledge Base returned {res['status']}. Trying next datasource.")

        # 8. Fallback exhausted
        logger.info("All datasources exhausted.")
        return {
            "status": STATUS_NOT_FOUND,
            "answer": "I couldn't find that information in my knowledge base.",
            "faculty_ids": [entity["id"]]
        }

    def _execute_faculty_directory(
        self,
        query: str,
        entity: Dict[str, Any],
        attribute_type: str
    ) -> Dict[str, Any]:
        """
        Executes query against the structured Faculty Directory.
        """
        name = entity.get("name", "")
        q_lower = query.lower()

        # Clean display name to avoid double honorifics
        display_name = name
        if display_name.lower().startswith("dr."):
            display_name = display_name[3:].strip()
        elif display_name.lower().startswith("dr "):
            display_name = display_name[2:].strip()
        elif display_name.lower().startswith("prof."):
            display_name = display_name[5:].strip()
        elif display_name.lower().startswith("prof "):
            display_name = display_name[4:].strip()

        # If the attribute type is descriptive, the directory is not applicable
        if attribute_type == "descriptive":
            return {"status": STATUS_NOT_APPLICABLE, "answer": None}

        # Check if the query asks specifically for the attribute of a person,
        # e.g., contains "email of", "email for", "email address", "what is X's email", "what is the email", etc.
        # Otherwise, if it is a general search lookup, we return the full profile card.
        is_specific_request = False
        if "what is" in q_lower or "what are" in q_lower or "get" in q_lower or "tell me" in q_lower or "give me" in q_lower:
            if not any(w in q_lower for w in ["who is in", "find faculty", "search for"]):
                is_specific_request = True
        elif any(phrase in q_lower for phrase in ["email of", "email for", "phone of", "phone for", "contact of", "office of", "room of", "cabin of", "building of", "department of", "designation of"]):
            is_specific_request = True

        if is_specific_request:
            if "email" in q_lower:
                email = entity.get("email")
                if email:
                    return {
                        "status": STATUS_FOUND,
                        "answer": f"The email address of Dr. {display_name} is {email}.",
                        "faculty_ids": [entity["id"]]
                    }
                return {"status": STATUS_NOT_FOUND, "answer": None}

            if any(w in q_lower for w in ["phone", "contact", "number"]):
                phone = entity.get("phone")
                if phone:
                    return {
                        "status": STATUS_FOUND,
                        "answer": f"The contact number of Dr. {display_name} is {phone}.",
                        "faculty_ids": [entity["id"]]
                    }
                return {"status": STATUS_NOT_FOUND, "answer": None}

            if any(phrase in q_lower for phrase in ["office of", "room of", "cabin of", "what is the office", "what is the room"]):
                office = entity.get("office")
                if office:
                    return {
                        "status": STATUS_FOUND,
                        "answer": f"The office of Dr. {display_name} is located at {office}.",
                        "faculty_ids": [entity["id"]]
                    }
                return {"status": STATUS_NOT_FOUND, "answer": None}

            if any(phrase in q_lower for phrase in ["building of", "what is the building"]):
                building = entity.get("building")
                if building:
                    return {
                        "status": STATUS_FOUND,
                        "answer": f"The office building of Dr. {display_name} is {building}.",
                        "faculty_ids": [entity["id"]]
                    }
                return {"status": STATUS_NOT_FOUND, "answer": None}

            if "department" in q_lower:
                dept = entity.get("department")
                if dept:
                    return {
                        "status": STATUS_FOUND,
                        "answer": f"Dr. {display_name} belongs to the department of {dept}.",
                        "faculty_ids": [entity["id"]]
                    }
                return {"status": STATUS_NOT_FOUND, "answer": None}

            if any(w in q_lower for w in ["designation", "role"]):
                desig = entity.get("designation")
                if desig:
                    return {
                        "status": STATUS_FOUND,
                        "answer": f"Dr. {display_name} is currently a {desig}.",
                        "faculty_ids": [entity["id"]]
                    }
                return {"status": STATUS_NOT_FOUND, "answer": None}

            if any(w in q_lower for w in ["research interests", "interests"]):
                interests = entity.get("research_interests")
                if interests:
                    interests_str = ", ".join(interests)
                    return {
                        "status": STATUS_FOUND,
                        "answer": f"The research interests of Dr. {display_name} include: {interests_str}.",
                        "faculty_ids": [entity["id"]]
                    }
                return {"status": STATUS_NOT_FOUND, "answer": None}

        # If it is a lookup like "Who is in Room 201?" or we didn't trigger specific attributes, format the full profile card
        designation = entity.get("designation") or "Faculty Member"
        department = entity.get("department")
        email = entity.get("email")
        phone = entity.get("phone")
        office = entity.get("office")
        building = entity.get("building")
        interests = entity.get("research_interests")
        
        ans_content = f"I found the following faculty member matching your request:\n\n"
        ans_content += f"• **{name}**\n"
        ans_content += f"  * Designation: {designation}\n"
        ans_content += f"  * Department: {department}\n"
        if interests:
            ans_content += f"  * Research Interests: {', '.join(interests)}\n"
        ans_content += f"  * Email: {email}\n"
        if phone:
            ans_content += f"  * Phone: {phone}\n"
        if office:
            ans_content += f"  * Office: {office}\n"
        if building:
            ans_content += f"  * Building: {building}\n"
        
        return {
            "status": STATUS_FOUND,
            "answer": ans_content,
            "faculty_ids": [entity["id"]]
        }

    async def _execute_website_knowledge_base(
        self,
        query: str,
        entity: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes query against the Website Knowledge Base.
        """
        try:
            from app.services.rag.rag_service import query_rag
            import asyncio

            # Fetch relevant documents from Website RAG
            rag_result = await asyncio.to_thread(query_rag, query, "Website QA")
            if not rag_result or not rag_result.get("documents"):
                return {"status": STATUS_NOT_FOUND, "answer": None}

            docs: List[str] = rag_result["documents"]

            # Name verification filter to prevent hallucination / irrelevant routing
            from app.services.faculty.normalizer import normalize_name
            norm_name = normalize_name(entity.get("name", ""))
            name_tokens = [t for t in norm_name.split() if len(t) > 2]

            found_name = False
            for doc in docs:
                norm_doc = normalize_name(doc)
                if all(token in norm_doc for token in name_tokens):
                    found_name = True
                    break

            if not found_name:
                logger.info(f"Bypassing Gemini: Faculty name '{entity.get('name')}' tokens not found in retrieved documents.")
                return {"status": STATUS_NOT_FOUND, "answer": None}

            # If name is present, call Gemini to answer
            from app.services.llm.gemini_service import generate_response
            context_str = "\n\n---\n\n".join(docs)
            prompt = (
                "You are the BIT Mesra AI Assistant.\n"
                "Use the following official website documents to answer the question about the faculty member.\n"
                "If the requested information is not found in the documents, return 'I couldn't find that information in my knowledge base.'\n\n"
                f"Context:\n{context_str}\n\n"
                f"Question: {query}\n"
                "Answer:"
            )

            response = await asyncio.to_thread(generate_response, prompt)
            response_clean = response.strip()

            refusal_phrases = [
                "couldn't find", "could not find", "no information", 
                "not found", "not available", "do not have", "cannot find"
            ]
            if any(phrase in response_clean.lower() for phrase in refusal_phrases):
                logger.info("Gemini indicated information could not be found.")
                return {"status": STATUS_NOT_FOUND, "answer": None}

            return {
                "status": STATUS_FOUND,
                "answer": response_clean,
                "faculty_ids": [entity["id"]]
            }

        except Exception as e:
            logger.error(f"Error querying Website Knowledge Base: {e}", exc_info=True)
            return {"status": STATUS_ERROR, "answer": None}
