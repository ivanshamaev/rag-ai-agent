### 🔹 1. Зарегистрируйся на платформе OpenAI

Перейди на 👉 [https://platform.openai.com](https://platform.openai.com)

Войдите с аккаунтом (можно через Google / Microsoft / email).

---

### 🔹 2. Получи API key

1. После входа перейди на страницу ключей:
   👉 [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Нажми **“Create new secret key”**
3. Скопируй токен — **он отображается только один раз!**

> ⚠️ Сразу запиши ключ в `.env` или в переменную окружения:
>
> ```bash
> export OPENAI_API_KEY="sk-..."
> ```

---

### 🔹 3. Бесплатный лимит

* После регистрации новый аккаунт **получает пробный кредит (обычно $5)**, которого хватает на тестирование.
* Если кредиты закончились — можно добавить карту, но при этом **никакие деньги не спишутся**, пока не превысишь бесплатный лимит.

---

### 🔹 4. Пример использования в Python

```python
from openai import OpenAI

client = OpenAI(api_key="sk-...")  # или возьми из переменной окружения

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Привет! Что ты умеешь?"}]
)

print(response.choices[0].message.content)
```

---

### 🔹 5. Альтернатива без токена

Если ты **не хочешь привязывать карту** или хочешь просто протестировать идею RAG, то можно:

* использовать **OpenRouter** ([https://openrouter.ai](https://openrouter.ai)) — там можно выбрать модель GPT-3.5/4 и получить бесплатные кредиты;
* или **ApiFreeLLM** — полностью бесплатный REST endpoint без токена (для тестов).

