# Hybrid RAG & AI Pipeline

This document describes the Retrieval-Augmented Generation (RAG) architecture, document chunking schemes, vector indexes, prompt builders, and telemetry tracing implementations in the **BIT Mesra AI Workspace**.

---

## 1. Document Ingestion Pipeline

The ingestion pipeline handles raw document formatting to prepare structured vector datasets:

```
[ PDF Document / HTML Webpage ]
              │
              ▼
  [ Boilerplate Stripping ] (beautifulsoup / text extraction tools)
              │
              ▼
  [ Recursive Character Splitting ] (500 char length, 50 char overlap)
              │
              ▼
[ HuggingFace BAAI/bge-small-en-v1.5 ] (384-dimensional dense vectors)
              │
              ▼
   [ ChromaDB Vector Store ]
```

---

## 2. Ingestion Parameters

### 2.1 PDF Parsing
- Uses PyPDF to extract text stream pages.
- Standardizes page boundaries, filters headers/footers, and appends original file metadata (file name, title, page numbers).

### 2.2 Web Scraper Ingestion
- Cleans HTML trees by stripping script tags, styling sheets, trackers, and navigation lists.
- Extracts table content as structured, vertical grid rows separated by delimiters (`|`) to maintain table formatting for the LLM.
- **SHA-256 Hashing**: Applies regex filters to clean content of variable timestamps, copyright marks, session variables, and whitespaces. If the content hash differs from the stored MongoDB record, the system re-embeds the updated content.

### 2.3 Text Chunking Configuration
- **Chunk Size**: `500` characters.
- **Chunk Overlap**: `50` characters.
- Chunks are separated at logical boundaries (paragraphs first, then newlines, then sentence periods, then words).

---

## 3. Retrieval & Re-ranking (Two-Stage RAG)

The system uses a two-stage retrieval pipeline:

```
                  [ User Question ]
                         │
                         ▼
        [ Stage 1: Vector Space Retrieval ]
         Queries ChromaDB (Cosine similarity)
                         │
                         ▼
           [ Stage 2: Cross-Encoder Rerank ]
       Sentence-Transformers MS-MARCO Re-ranking
                         │
                         ▼
       [ Top K Grounded Context Prompt Assembly ]
```

### 3.1 Stage 1: Semantic Vector Lookup
- Queries ChromaDB using dense embeddings generated from the `BAAI/bge-small-en-v1.5` model.
- Retrieves the top `N` candidates (`N = 10` chunks) based on cosine similarity scores.

### 3.2 Stage 2: Cross-Encoder Re-ranking
- Feeds the user question and retrieved chunks concurrently into the Cross-Encoder model (`sentence-transformers/ms-marco-MiniLM-L-6-v2`).
- The Cross-Encoder computes a query-document score representing how well each chunk answers the query.
- Sorts results by relevance score and filters out low-scoring chunks (score < `0.3`), retaining the top `5` highest-quality candidates.

---

## 4. Prompt Assembly & Context Integration

Once RAG chunks and academic records are gathered, they are structured into a prompt:
- **System Role**: Standard BIT Mesra Assistant guidelines (act as a helpful campus assistant, ground answers strictly in citations, do not make up facts).
- **Academic Context**: Renders current student profile, course timetable schedules for today/tomorrow, and attendance warnings.
- **Retrieved Chunks**: Renders the ranked RAG document snippets with source IDs and page indices.
- **Conversation Logs**: Appends the last 5 conversation history turns.
- **Token Budget Checks**: `TokenBudgetManager` tokenizes the prompt. If the size exceeds `3,500` tokens, RAG chunks and history items are trimmed.

---

## 5. Telemetry & Diagnostics Tracing

When developer mode is active, the assistant endpoint outputs detailed telemetry diagnostics logs:
- **`elapsed_ms`**: Latency in milliseconds across the intent, context gathering, and Gemini generation stages.
- **`tokens_used`**: Total tokens consumed.
- **`intent`**: Classified query category.
- **`debug_rag`**: Diagnostic tracing mapping:
  - Total document candidates retrieved.
  - Final re-ranked candidates list with source labels, raw scores, combined scores, and decision reason explanations.
