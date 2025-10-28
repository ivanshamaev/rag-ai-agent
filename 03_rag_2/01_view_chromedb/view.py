import chromadb

# Подключаемся к persistent Chroma
client = chromadb.PersistentClient(path="embeddings/")

# Список коллекций
print("Коллекции:", client.list_collections())

# Получаем коллекцию
collection = client.get_collection("tables")

# Получаем все документы и embeddings
results = collection.get(include=["documents", "embeddings", "metadatas"])

for i, doc in enumerate(results["documents"]):
    metadata = results["metadatas"][i] if results["metadatas"] else {}
    doc_id = metadata.get('id', i) if metadata else i
    print(f"ID документа: {doc_id}")
    print(f"Текст (первые 100 символов): {doc[:100]}...")
    print("-"*50)

print(f"Всего документов: {len(results['documents'])}")
