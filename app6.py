from langchain.agents import initialize_agent
from langchain.tools import tool
from code_generator_agent import generate_code_for_query  # Function to generate tool code
import json
from langchain_ollama import ChatOllama
from langchain.agents import create_json_agent
from langchain.agents.agent_toolkits import JsonToolkit
from langchain.tools.json.tool import JsonSpec

# Load JSON data
file = "./myJson.json"
with open(file, "r") as f:
    data = json.load(f)

# Initialize list to store tools
tools = []

def process_query(query: str):
    """
    Processes the user query by generating a tool dynamically and adding it to the agent.
    """
    # Step 1: Generate Python code for the tool based on the user query
    generated_code = generate_code_for_query(query)
    print(f"Generated Code:\n{generated_code}")  # Optional: print code for debugging

    # Step 6: Reinitialize the agent with the updated tools list
    llm = ChatOllama(model="gemma2", temperature=0.2)
    spec = JsonSpec(dict_=data)
    toolkit = JsonToolkit(spec=spec)
    agent = initialize_agent(
        llm = llm,
        toolkit=toolkit,
        verbose=True,
        allow_dangerous_code=True,
        hanle_validation_error=True
    )

    # Run the query with the agent and return the response
    query = f"query from user : {query}, code gen ai: {generated_code}, use the code gen ai to get the result for user query and reponsd to user accordingly"
    try:
        response = agent.run(query)
        print("Agent Response:", response)
    except TypeError as e:
        print("TypeError encountered while processing query:", e)

# Example of using process_query
process_query("Summarize the failed test cases")
