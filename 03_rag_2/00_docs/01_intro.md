## 🚀 Цель апгрейда

Добавить новые источники знаний для RAG, чтобы агент мог отвечать не только:

* какие поля есть в таблице,
  но и:
* как таблицы связаны,
* как формируются факты и измерения,
* что делают SQL-процедуры,
* где используется конкретное поле,
* как написать запрос на нужный отчёт.

---

## 🧩 Новая структура проекта

```
rag_dwh_agent/
├── data/
│   ├── metadata/
│   │   ├── tables.yaml              # описание таблиц и полей
│   │   ├── relations.yaml           # связи между таблицами
│   │   └── domains.yaml             # описание бизнес-домена
│   ├── sql/
│   │   ├── fact_stock_load.sql      # процедура загрузки фактов
│   │   ├── dim_products_load.sql    # процедура загрузки измерения
│   │   └── views/
│   │       └── v_stock_summary.sql  # представление отчёта
│   └── glossary.yaml                # бизнес-термины и их определения
├── embeddings/
├── src/
│   ├── loader.py
│   ├── embedder.py
│   ├── retriever.py
│   ├── rag_agent.py
│   └── main.py
└── requirements.txt
```

---

## 🧠 1. `tables.yaml` — метаданные таблиц

```yaml
tables:
  - name: dim_products
    description: Справочник товаров.
    fields:
      - name: product_id
        type: int
        description: Уникальный идентификатор товара
      - name: product_name
        type: varchar
        description: Название товара
      - name: product_group
        type: varchar
        description: Группа товаров
  - name: fact_stock_movements
    description: Факт движения товаров по складам.
    fields:
      - name: movement_id
        type: int
        description: Идентификатор операции
      - name: product_id
        type: int
        description: Ключ на dim_products
      - name: warehouse_id
        type: int
        description: Ключ на dim_warehouses
      - name: quantity
        type: decimal
        description: Количество единиц
      - name: movement_type
        type: varchar
        description: Тип движения: 'IN', 'OUT', 'TRANSFER'
```

---

## 🔗 2. `relations.yaml` — связи между таблицами

```yaml
relations:
  - from_table: fact_stock_movements
    to_table: dim_products
    type: many-to-one
    join_condition: fact_stock_movements.product_id = dim_products.product_id

  - from_table: fact_stock_movements
    to_table: dim_warehouses
    type: many-to-one
    join_condition: fact_stock_movements.warehouse_id = dim_warehouses.warehouse_id
```

---

## 📊 3. `domains.yaml` — описание бизнес-домена

```yaml
domain:
  name: warehouse_management
  description: >
    Домен отвечает за движение товаров по складам, учёт остатков,
    перемещения между складами и поступления от поставщиков.
  kpis:
    - name: stock_turnover
      description: Оборот товара на складе, рассчитывается как отношение объёма продаж к среднему остатку.
    - name: warehouse_utilization
      description: Заполненность склада в процентах.
```

---

## 🧱 4. SQL-процедуры (`sql/fact_stock_load.sql`)

```sql
CREATE PROCEDURE load_fact_stock_movements AS
BEGIN
    INSERT INTO fact_stock_movements (movement_id, product_id, warehouse_id, quantity, movement_type)
    SELECT 
        src.movement_id,
        src.product_id,
        src.warehouse_id,
        src.quantity,
        CASE
            WHEN src.quantity > 0 THEN 'IN'
            WHEN src.quantity < 0 THEN 'OUT'
            ELSE 'TRANSFER'
        END
    FROM staging.stock_movements src;
END;
```

---

## 📘 5. `glossary.yaml` — словарь бизнес-терминов

```yaml
terms:
  - term: SKU
    definition: Уникальный код товара (Stock Keeping Unit)
  - term: DWH
    definition: Хранилище данных (Data Warehouse)
  - term: ETL
    definition: Процесс загрузки данных: Extract, Transform, Load
```

---

## 🧩 Обновим `loader.py`

Теперь он объединяет всё в единый текстовый корпус для RAG.

```python
import yaml, os, glob

def load_yaml_data(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_text_files(directory):
    texts = []
    for path in glob.glob(os.path.join(directory, "**/*.sql"), recursive=True):
        with open(path, "r", encoding="utf-8") as f:
            texts.append(f"-- Файл {os.path.basename(path)}\n" + f.read())
    return texts

def build_corpus(base_path="data"):
    corpus = []

    # Таблицы
    tables_yaml = load_yaml_data(os.path.join(base_path, "metadata/tables.yaml"))
    for table in tables_yaml.get("tables", []):
        text = f"Таблица {table['name']}: {table['description']}\n"
        for f in table["fields"]:
            text += f"- {f['name']} ({f['type']}): {f['description']}\n"
        corpus.append(text)

    # Связи
    relations_yaml = load_yaml_data(os.path.join(base_path, "metadata/relations.yaml"))
    for rel in relations_yaml.get("relations", []):
        corpus.append(
            f"Связь: {rel['from_table']} -> {rel['to_table']} по {rel['join_condition']} ({rel['type']})"
        )

    # Домен
    domain_yaml = load_yaml_data(os.path.join(base_path, "metadata/domains.yaml"))
    corpus.append(
        f"Домен: {domain_yaml['domain']['name']} — {domain_yaml['domain']['description']}"
    )

    # Термины
    glossary = load_yaml_data(os.path.join(base_path, "glossary.yaml"))
    for term in glossary.get("terms", []):
        corpus.append(f"Термин {term['term']}: {term['definition']}")

    # SQL-файлы
    sql_texts = load_text_files(os.path.join(base_path, "sql"))
    corpus.extend(sql_texts)

    return corpus
```

---

## ⚙️ Использование в `main.py`

Заменяем строку:

```python
chunks = load_yaml_data("data/tables.yaml")
```

на:

```python
from loader import build_corpus
chunks = build_corpus("data")
```

---

## 💬 Теперь RAG может отвечать на вопросы вроде:

```
❓ Что делает процедура load_fact_stock_movements?
❓ Как связаны таблицы dim_products и fact_stock_movements?
❓ Что такое KPI stock_turnover?
❓ Из какой таблицы берётся поле warehouse_id?
❓ Напиши SQL-запрос, который покажет оборот товара по складам.
```

---

## 💡 Следующий шаг (если хочешь развивать дальше)

Можно добавить **“semantic search” по типу контента**, например:

* искать только по SQL-кодам,
* искать только по описаниям таблиц,
* или комбинировать источники с весами (SQL = 0.7, YAML = 0.3).


## 🧠 Проверка вручную

Ты можешь протестировать файл командой:

```bash
python -c "import yaml; print(yaml.safe_load(open('data/metadata/tables.yaml')))"
python -c "import yaml; print(yaml.safe_load(open('data/glossary.yaml')))"
```

