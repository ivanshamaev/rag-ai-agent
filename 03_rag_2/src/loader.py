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
