
## 🚀 Цель

Создадим минимальную рабочую версию RAG, которая:

* Подгружает YAML-описание таблиц;
* Создаёт текстовые "часы" (chunks);
* Индексирует их в **векторной БД** (используем **Chroma** — просто, локально, без интернета);
* Позволяет задавать вопросы, на которые агент отвечает с учётом контекста таблиц;
* Использует **OpenRouter LLM API** для генерации ответов.

---

## 📁 Структура проекта

```
rag_dwh_agent/
├── data/
│   └── tables.yaml               # описание таблиц и связей
├── embeddings/                   # векторное хранилище (создаётся автоматически)
├── src/
│   ├── loader.py                 # загрузка YAML
│   ├── embedder.py               # создание эмбеддингов
│   ├── retriever.py              # поиск релевантных контекстов
│   ├── rag_agent.py              # основная логика RAG
│   └── main.py                   # CLI-интерфейс
├── .env                          # хранит OPENROUTER_API_KEY
└── requirements.txt
```

---

## 📦 requirements.txt

```txt
openai>=1.30.0
chromadb>=0.5.0
pyyaml
python-dotenv
tqdm
```

---

## 📄 data/tables.yaml (пример)

```yaml
tables:
  - name: products
    description: Справочник товаров. Содержит информацию о номенклатуре и кодах.
    fields:
      - name: product_id
        type: int
        description: Уникальный идентификатор товара
      - name: product_name
        type: varchar
        description: Название товара

  - name: warehouses
    description: Справочник складов.
    fields:
      - name: warehouse_id
        type: int
        description: Уникальный идентификатор склада
      - name: warehouse_name
        type: varchar
        description: Название склада

  - name: stock_movements
    description: Факт движения товаров между складами.
    fields:
      - name: movement_id
        type: int
        description: Идентификатор операции
      - name: product_id
        type: int
        description: Идентификатор товара
      - name: warehouse_id
        type: int
        description: Идентификатор склада
      - name: movement_date
        type: datetime
        description: Дата перемещения
      - name: quantity
        type: float
        description: Количество перемещённого товара
```

---

## 📄 src/loader.py

```python
import yaml

def load_yaml_data(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    tables = data.get("tables", [])
    chunks = []
    for table in tables:
        text = f"Таблица {table['name']}: {table['description']}\n"
        for field in table["fields"]:
            text += f"- {field['name']} ({field['type']}): {field['description']}\n"
        chunks.append(text)
    return chunks
```

---

## 📄 src/embedder.py

```python
import chromadb
from chromadb.utils import embedding_functions

def create_chroma_db(chunks, persist_dir="embeddings"):
    client = chromadb.PersistentClient(path=persist_dir)
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=None,  # chroma возьмёт OPENAI_API_KEY из окружения, но мы используем OpenRouter → пропустим
        model_name="text-embedding-3-small"
    )
    collection = client.get_or_create_collection(
        name="tables", embedding_function=openai_ef
    )
    for i, chunk in enumerate(chunks):
        collection.add(documents=[chunk], ids=[str(i)])
    return collection
```

> ⚠️ Поскольку OpenRouter не предоставляет embeddings напрямую, для MVP можно использовать встроенный эмбеддер Chroma (он сам fallback-ит на `all-MiniLM-L6-v2`, если OpenAI embeddings недоступны).

---

## 📄 src/retriever.py

```python
def retrieve_context(query, collection, top_k=3):
    results = collection.query(query_texts=[query], n_results=top_k)
    return results["documents"][0]
```

---

## 📄 src/rag_agent.py

```python
from openai import OpenAI

def ask_rag(query, context, api_key):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    system_prompt = (
        "Ты — эксперт по DWH и складским данным. "
        "Используй приведённый контекст таблиц для ответа на вопрос. "
        "Отвечай понятно и структурированно.\n\n"
        f"Контекст:\n{context}\n"
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
    )

    return completion.choices[0].message.content
```

---

## 📄 src/main.py

```python
import os
from dotenv import load_dotenv
from loader import load_yaml_data
from embedder import create_chroma_db
from retriever import retrieve_context
from rag_agent import ask_rag

def main():
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")

    print("🔹 Загружаем данные...")
    chunks = load_yaml_data("data/tables.yaml")
    collection = create_chroma_db(chunks)

    while True:
        query = input("\n❓ Вопрос: ")
        if query.lower() in ["exit", "quit"]:
            break

        context = "\n\n".join(retrieve_context(query, collection))
        answer = ask_rag(query, context, api_key)

        print("\n💬 Ответ:")
        print(answer)

if __name__ == "__main__":
    main()
```

---

## 📄 .env

```env
OPENROUTER_API_KEY=sk-or-ваш-ключ
```

---

## ▶️ Запуск

```bash
pip install -r requirements.txt
python src/main.py
```

Примеры запросов:

```
❓ Какие поля есть в таблице stock_movements?
❓ Как связаны таблицы products и stock_movements?
❓ Напиши пример SQL-запроса, чтобы получить все движения по конкретному складу.
```

---

## ✅ Что это даст

* Ты получишь полностью рабочий **RAG-пайплайн** с YAML-данными;
* Можно расширить данные, добавить SQL-файлы, описания процедур;
* При желании заменить Chroma на Qdrant или FAISS.

✅ Рекомендую для твоего проекта

Поскольку ты строишь корпоративный RAG (и дальше будет интеграция с внутренними данными),
лучше использовать SentenceTransformer — он бесплатный, офлайн и устойчивый.

#### 📄 src/embedder.py (обновлённый)

```python
import chromadb
from chromadb.utils import embedding_functions

def create_chroma_db(chunks, persist_dir="embeddings"):
    client = chromadb.PersistentClient(path=persist_dir)
    sentence_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    collection = client.get_or_create_collection(
        name="tables", embedding_function=sentence_ef
    )
    for i, chunk in enumerate(chunks):
        collection.add(documents=[chunk], ids=[str(i)])
    return collection
```

🔹 Это создаст embeddings **локально**, без внешнего API,
что идеально подходит для офлайн / корпоративной среды.

