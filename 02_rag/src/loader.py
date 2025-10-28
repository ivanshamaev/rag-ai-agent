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
