import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import APIKeyHeader
from langchain_experimental.agents import create_json_agent
from langchain_ollama import ChatOllama
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory
import redis

from pydantic import BaseModel
import ollama


# Environment variable setup for Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# FastAPI setup
app = FastAPI()
api_key_header = APIKeyHeader(name="X-API-Key")

# Chat model setup
llm = ChatOllama(
    model="gemma2",
    temperature=0.2
)

# Redis message history
redis_client = redis.from_url(REDIS_URL)

def get_memory(session_id: str):
    return RedisChatMessageHistory(url=REDIS_URL, ttl=600, session_id=session_id)

# Define a Pydantic model for the request body
class QueryRequest(BaseModel):
    json_url: str
    user_message: str
    session_id: str

@app.post("/query")
async def query_json(
    request: QueryRequest,
    api_key: str = Depends(api_key_header),
):
    # Validate API key (add your API key validation logic here)
    if api_key != "your_secure_api_key":
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Create a validation prompt for the LLM
    validation_prompt = (
        f"Determine if the following question is related to querying JSON data: "
        f"\"{request.user_message}\". Respond with 'yes' if it is relevant, or 'no' if it is not."
    )

    # Get the LLM's response for validation
    user_messages = [{"role": "user", "content": validation_prompt}]
    validation_response = ollama.chat(model="gemma2", messages=user_messages)

    # Check LLM's validation response
    if "yes" not in validation_response['message']['content'].lower():
        raise HTTPException(
            status_code=400,
            detail="The question is not relevant to JSON data. Please ask a question about retrieving or analyzing JSON data."
        )

    # Create the agent with memory
    message_history = get_memory(request.session_id)
    agent = create_json_agent(
        llm,
        request.json_url,
        verbose=True,
        allow_dangerous_code=True,
    )

    agent_with_chat_history = RunnableWithMessageHistory(
        agent,
        lambda session_id: message_history,
        input_messages_key="input",
        history_messages_key="chat_history"
    )

    response = agent_with_chat_history.invoke(
        {"input": request.user_message},
        config={"configurable": {"session_id": request.session_id}
    })

    print(response)

    return {"response": response}

