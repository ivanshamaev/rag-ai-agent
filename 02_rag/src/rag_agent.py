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
