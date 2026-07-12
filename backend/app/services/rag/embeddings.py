from app.services.rag.vector_store import get_vector_store


def save_documents(documents, source_types=None):

    vector_store = get_vector_store()

    if source_types:
        for src_type in source_types:
            try:
                # Query ChromaDB for documents matching this source type metadata
                existing = vector_store.get(where={"source": src_type})
                ids = existing.get("ids", [])
                if ids:
                    vector_store.delete(ids=ids)
                    print(f"Cleared {len(ids)} existing '{src_type}' documents from ChromaDB.")
            except Exception as e:
                print(f"Failed to clear source type '{src_type}': {e}")
    else:
        # Fallback to legacy behavior if source_types not specified (for safety/compatibility)
        try:
            count = vector_store._collection.count()
            if count > 0:
                vector_store.delete(
                    ids=vector_store.get()["ids"]
                )
                print(
                    f"Cleared {count} existing documents."
                )
        except Exception:
            pass

    vector_store.add_documents(documents)

    print(
        f"Stored {len(documents)} documents"
    )