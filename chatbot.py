
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing_extensions import TypedDict



import os
from langchain.chat_models import init_chat_model

os.environ["GOOGLE_API_KEY"] = "AIzaSyDcFma_F_a0BT6s-GcoSKcAJtN5eTvoFvo"

llm = init_chat_model("google_genai:gemini-2.0-flash")



class MessageClassifier(BaseModel):
    message_type: Literal["positive", "negative"] = Field(
        ...,
        description="Classify if the message is positive or negative."
    )


class State(TypedDict):
    messages: Annotated[list, add_messages]
    message_type: str 


def classify_message(state: State):
    last_message = state["messages"][-1]
    classifier_llm = llm.with_structured_output(MessageClassifier)

    result = classifier_llm.invoke([
        {
            "role": "system",
            "content": """Classify the user message as either:
            - 'positive': if it is positive feedback.
            - 'negative': if it is negative feedback.
            """
        },
        {"role": "user", "content": last_message.content}
    ])
    return {"message_type": result.message_type}


def router(state: State):
    message_type = state.get("message_type", "positive")
    if message_type == "positive":
        return {"next": "positive"}

    return {"next": "negative"}


def positive_agent(state: State):
    last_message = state["messages"][-1]

    messages = [
        {"role": "system",
         "content": """ou are a helpful assistant. As the feedback is positive,
           provide a response to the user."""
         },
        {
            "role": "user",
            "content": last_message.content
        }
    ]
    reply = llm.invoke(messages)
    return {"messages": [{"role": "assistant", "content": reply.content}]}


def negative_agent(state: State):
    last_message = state["messages"][-1]

    messages = [
        {"role": "system",
         "content": """You are a helpful assistant. As the feedback is negative,
         you should create a response for the user to identify the issue.
         And you provide two messages: one for the user and one for the boss.
         Here is the format:
            user_message: <user_message>
            boss_message: <boss_message>
         """},
        {"role": "user", "content": last_message.content}
    ]

    reply = llm.invoke(messages)
    reply_text = reply.content.strip()

    # Extract boss_message only
    import re
    match = re.search(r"boss_message\s*:\s*(.+)", reply_text, re.IGNORECASE | re.DOTALL)
    boss_message = match.group(1).strip() if match else None

    print(f"Boss message: {boss_message}")

    # Save only the boss_message
    if boss_message:
        with open("issue.txt", "a") as f:
            f.write(boss_message + "\n")
    else:
        reply_text += "\n(Note: Boss message not found. Nothing was stored.)"

    # Return only the user message for the assistant to show
    user_match = re.search(r"user_message\s*:\s*(.+?)(?:\nboss_message|$)", reply_text, re.IGNORECASE | re.DOTALL)
    user_message = user_match.group(1).strip() if user_match else "Thank you for your feedback."

    return {"messages": [{"role": "assistant", "content": user_message}]}


graph_builder = StateGraph(State)

graph_builder.add_node("classifier", classify_message)
graph_builder.add_node("router", router)
graph_builder.add_node("positive", positive_agent)
graph_builder.add_node("negative", negative_agent)

graph_builder.add_edge(START, "classifier")
graph_builder.add_edge("classifier", "router")

graph_builder.add_conditional_edges(
    "router",
    lambda state: state.get("next"),
    {"positive": "positive", "negative": "negative"}
)

graph_builder.add_edge("positive", END)
graph_builder.add_edge("negative", END)

graph = graph_builder.compile()


def run_chatbot():
    state = {"messages": [], "message_type": None}

    while True:
        user_input = input("Message: ")
        if user_input == "exit":
            print("Bye")
            break

        state["messages"] = state.get("messages", []) + [
            {"role": "user", "content": user_input}
        ]

        state = graph.invoke(state)

        if state.get("messages") and len(state["messages"]) > 0:
            last_message = state["messages"][-1]
            print(f"Assistant: {last_message.content}")


if __name__ == "__main__":
    run_chatbot()