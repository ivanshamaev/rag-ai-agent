
## 1️⃣ Через Python (самый простой)

```python
import chromadb
from chromadb.utils import embedding_functions

# Путь к папке с базой
persist_dir = "embeddings/"

# Подключаемся к Chroma
client = chromadb.PersistentClient(path=persist_dir)

# Список всех коллекций
print("Коллекции:", client.list_collections())

# Получаем коллекцию
collection = client.get_collection("tables")  # или имя твоей коллекции

# Смотрим все документы
results = collection.get(include=["documents", "ids"])
for doc_id, doc_text in zip(results["ids"], results["documents"]):
    print(f"ID: {doc_id}\nТекст: {doc_text}\n{'-'*40}")
```

✅ Таким образом можно проверить **все тексты**, которые были занесены в базу, и их ID.

---

## 2️⃣ Проверка количества векторов и их размерности

```python
info = collection.count()
print(f"Документов: {info}")
```

Или получить **embedding** конкретного документа:

```python
emb = collection.get(ids=["0"], include=["embeddings"])
print(emb["embeddings"][0][:10], "...")  # первые 10 чисел вектора
```

---

## 3️⃣ Использовать SQL-like запросы (Chroma позволяет ограниченный поиск)

```python
query = "Таблица dim_products"
results = collection.query(query_texts=[query], n_results=3, include=["documents", "ids"])
print(results["documents"][0])
```

* `n_results` — сколько ближайших документов искать.
* `include=["documents","ids"]` — какие поля вернуть.

---

## 4️⃣ Альтернатива: открыть физические файлы

* Chroma хранит данные в папке `embeddings/` в виде файлов SQLite + JSON.
* Можно открыть `.sqlite` через **DB Browser for SQLite** или любой SQL-клиент.
* Но чаще удобнее пользоваться **Python API**, чтобы не ковыряться в бинарных файлах.

