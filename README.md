
# LangGraph Feedback Classifier Chatbot

This project is a **feedback-classifying chatbot** that uses **LangGraph**, **LangChain**, and **Gemini 2.0 Flash (Google GenAI)** to identify whether user input is *positive* or *negative*, and respond accordingly.

---

## 🧠 Features

- Classifies messages as either:
  - `"positive"` – sends a friendly reply.
  - `"negative"` – stores a response for both user and boss in `issue.txt`.
- Uses structured output parsing with `Pydantic`.
- Employs a LangGraph stateful flow to direct logic.

---

## 🛠 Requirements

- Python 3.8+
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [LangChain](https://www.langchain.com/)
- `GOOGLE_API_KEY` from [Google AI Studio](https://makersuite.google.com/)

Install dependencies:

```bash
pip install langgraph langchain pydantic
```

---

## 🚀 Running the Project

1. **Set the environment variable**:
   ```bash
   export GOOGLE_API_KEY="your_google_api_key"
   ```

2. **Run the chatbot**:
   ```bash
   python chatbot.py
   ```

3. **Interact**:
   ```
   Message: I really like your service!
   Assistant: Thank you! We're glad you enjoyed it.
   ```

4. **Exit**:
   ```
   Message: exit
   Bye
   ```

---

## 📂 File Outputs

- When a **negative** message is received, the chatbot:
  - Responds to the user.
  - Extracts a `boss_message` and saves it in `issue.txt`.

---

## 🧩 Project Structure

```
chatbot.py        # Main script
issue.txt         # Stores boss messages
README.md         
```

---

## 🧪 Example Flow

```
User: Why i charged extra? here is billing id 12345.
→ Classifier: negative
→ Router → negative_agent
→ Writes to issue.txt
→ Responds: I received a complaint from a customer regarding an extra charge on billing ID 12345. I need to investigate this issue to determine the cause of the extra charge and resolve it for the customer. Please provide me with the necessary information, including the details of the billing and any relevant customer interactions, so I can address this matter effectively.
```

---

## 📜 License

[MIT License](./LICENSE.md)
