def retrieve_context(query, collection, top_k=3):
    results = collection.query(query_texts=[query], n_results=top_k)
    return results["documents"][0]
