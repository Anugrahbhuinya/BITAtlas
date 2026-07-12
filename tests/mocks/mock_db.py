"""
Mock database and vector store implementations for unit and integration testing.
"""
from __future__ import annotations

import json
import os
from unittest.mock import MagicMock
from bson import ObjectId
from langchain_core.documents import Document

FIXTURES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fixtures", "student_fixtures.json")


class MockCursor:
    """Mock for Motor async cursor."""
    def __init__(self, data):
        self.data = data
        self.index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index < len(self.data):
            val = self.data[self.index]
            self.index += 1
            return val
        raise StopAsyncIteration

    async def to_list(self, length=None):
        return self.data[:length] if length else self.data


class MockCollection:
    """Mock for Motor MongoDB collection."""
    def __init__(self, name, initial_data=None):
        self.name = name
        self.data = initial_data or []

    def _match_val(self, item_val, spec_val):
        if isinstance(spec_val, dict):
            if "$ne" in spec_val:
                # Handle dict operators inside $ne robustly too
                return not self._match_val(item_val, spec_val["$ne"])
            if "$in" in spec_val:
                return any(self._match_val(item_val, x) for x in spec_val["$in"])
        # Robust comparison for ObjectId / string
        if isinstance(item_val, ObjectId) or isinstance(spec_val, ObjectId):
            return str(item_val) == str(spec_val)
        return item_val == spec_val

    async def find_one(self, spec, *args, **kwargs):
        print(f"\nDEBUG find_one collection={self.name} spec={spec} data_ids={[str(i.get('_id')) for i in self.data]}")
        # Flatten queries
        for item in self.data:
            match = True
            for k, v in spec.items():
                item_val = item.get(k)
                matched = self._match_val(item_val, v)
                print(f"  Compare key={k}: item_val={item_val} ({type(item_val)}) spec_val={v} ({type(v)}) -> matched={matched}")
                if k == "_id" and isinstance(v, dict) and "$in" in v:
                    if item_val not in v["$in"]:
                        match = False
                        break
                elif not matched:
                    match = False
                    break
            if match:
                print(f"  FOUND MATCH: {item.get('_id')}")
                return item
        print("  NO MATCH FOUND")
        return None

    def find(self, spec=None, *args, **kwargs):
        spec = spec or {}
        matched = []
        for item in self.data:
            match = True
            for k, v in spec.items():
                if k == "_id" and isinstance(v, dict) and "$in" in v:
                    if item.get(k) not in v["$in"]:
                        match = False
                        break
                elif not self._match_val(item.get(k), v):
                    match = False
                    break
            if match:
                matched.append(item)
        return MockCursor(matched)

    async def insert_one(self, doc, *args, **kwargs):
        if "_id" not in doc:
            doc["_id"] = ObjectId()
        self.data.append(doc)
        mock_res = MagicMock()
        mock_res.inserted_id = doc["_id"]
        return mock_res

    async def update_one(self, spec, document, *args, **kwargs):
        item = await self.find_one(spec)
        if item:
            # Simple set mapping
            update_op = document.get("$set", {})
            for k, v in update_op.items():
                item[k] = v
            mock_res = MagicMock()
            mock_res.modified_count = 1
            return mock_res
        mock_res = MagicMock()
        mock_res.modified_count = 0
        return mock_res

    async def delete_many(self, spec, *args, **kwargs):
        original_len = len(self.data)
        self.data = [
            item for item in self.data
            if not all(item.get(k) == v for k, v in spec.items())
        ]
        mock_res = MagicMock()
        mock_res.deleted_count = original_len - len(self.data)
        return mock_res


class MockMongoDatabase:
    """Mock for Motor MongoDB database."""
    def __init__(self):
        self.collections = {}
        self.load_fixtures()

    def load_fixtures(self):
        try:
            with open(FIXTURES_PATH, "r") as f:
                fixtures = json.load(f)
        except Exception:
            fixtures = {}
            
        for col_name in ["students", "attendance_records", "timetables", "attendance_logs", "planner_tasks", "sessions"]:
            initial_data = fixtures.get(col_name, [])
            self.collections[col_name] = MockCollection(col_name, initial_data)

    def __getitem__(self, name):
        if name not in self.collections:
            self.collections[name] = MockCollection(name)
        return self.collections[name]

    def __getattr__(self, name):
        return self[name]


class MockVectorStore:
    """Mock for Chroma vector store."""
    def __init__(self):
        self.documents = [
            Document(
                page_content="BIT Mesra campus has 10 hostels for boys and 3 for girls.",
                metadata={"source": "handbook.pdf", "page": 5}
            ),
            Document(
                page_content="Hostel mess timings: Breakfast: 8:00-9:30 AM, Lunch: 1:00-2:30 PM, Dinner: 8:00-9:30 PM.",
                metadata={"source": "mess_rules.txt"}
            ),
            Document(
                page_content="Central Library timings are 9 AM to 9 PM on all working days.",
                metadata={"source": "library_rules.txt"}
            )
        ]

    def similarity_search_with_score(self, query, k=3, *args, **kwargs):
        # Simple mock search returning first k matches
        return [(doc, 0.9 - (i * 0.1)) for i, doc in enumerate(self.documents[:k])]


# Global singleton database and vector store mocks
_mock_db = MockMongoDatabase()
_mock_vector_store = MockVectorStore()


def get_mock_database():
    return _mock_db


def get_mock_vector_store():
    return _mock_vector_store
