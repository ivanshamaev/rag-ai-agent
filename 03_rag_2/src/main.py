import os
from dotenv import load_dotenv
from loader import load_yaml_data
from embedder import create_chroma_db
from retriever import retrieve_context
from rag_agent import ask_rag
from loader import build_corpus

def main():
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")

    print("🔹 Загружаем данные...")
    chunks = build_corpus("data")
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
