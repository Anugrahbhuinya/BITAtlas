# Faculty Directory Dataset

## Purpose
This directory houses the structured faculty directory dataset for Birla Institute of Technology, Mesra. It contains contact details, designation, department normalization, and research interests of all faculty members.

## RAG & AI Isolation (CRITICAL)
This dataset is **strictly structured application data**. It is intentionally separated from the AI Knowledge Base, ChromaDB, vector database, and the general RAG pipeline for the following reasons:
1. **Factual Integrity**: Contact details (emails, phone numbers) must be retrieved with absolute precision without hallucination risk.
2. **Database Performance**: Querying structured directory listings is significantly faster, lighter, and more reliable via direct JSON key-value search rather than fuzzy semantic embedding search.
3. **Pipeline Isolation**: Directory queries do not need to consume Gemini API tokens or search vector collections, conserving resources.

## Folder Structure
```
backend/app/data/faculty/
├── faculty_directory.json  # Structured directory JSON
└── README.md               # Documentation and schema specifications
```

## JSON Schema
Each record follows this schema:
```json
{
  "id": "cse_001",
  "name": "Dr. Name",
  "designation": "Assistant Professor",
  "department": "Computer Science & Engineering",
  "email": "name@bitmesra.ac.in",
  "phone": "9999999999",
  "research_interests": [
    "Machine Learning",
    "Computer Vision"
  ],
  "office": null,
  "building": null,
  "office_hours": null,
  "website": null,
  "photo": null
}
```

## Validation Rules
To update the directory:
1. **Deterministic IDs**: Generates using prefix + sequential index (e.g. `cse_001`). IDs must be sorted alphabetically by name per department first before indexing to maintain deterministic indexing order.
2. **Normalisation**: Ensure department names match the approved normalized list.
3. **No Placeholders**: "Not Provided" and "Not Available" must be serialized as `null`.
4. **Unique Contacts**: Duplicate emails are strictly forbidden and validated upon build/ingestion.