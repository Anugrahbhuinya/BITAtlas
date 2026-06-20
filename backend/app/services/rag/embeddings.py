from app.services.rag.vector_store import get_vector_store


def save_documents(documents):

    vector_store = get_vector_store()

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