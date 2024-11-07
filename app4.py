from langchain.agents import initialize_agent
from langchain.agents.agent_toolkits import JsonToolkit
from langchain.tools.json.tool import JsonSpec
from langchain_ollama import ChatOllama
import json

# Chat model setup
llm = ChatOllama(
    model="gemma2",
    temperature=0.2
)

# Load JSON data
file = "./myJson.json"
with open(file, "r") as f:
    data = json.load(f)

# Define the JSON spec for the agent
json_spec = JsonSpec(dict_=data)
toolkit = JsonToolkit(spec=json_spec)

# Initialize agent
agent = initialize_agent(
    agent="zero-shot-react-description",
    tools=toolkit.get_tools(),
    llm=llm,
    verbose=True
)

# Instructions for LLM on JSON structure (you can explain JSON format in detail)
json_structure_instruction = """
The JSON file contains information about test suites and their execution details. Here is the structure to understand:

- The top-level key, "suites", is an array of test suites.
  - Each suite has:
    - "name": the suite’s name (e.g., "Domestic - Negative Flows").
    - "startTime": the suite's start time.
    - "tag": a label/tag for the suite.
    - "specName": the specification file associated with this suite.
    - "tests": an array of individual tests in the suite.

- Each test contains:
    - "name": the name of the test (e.g., "Login Flow").
    - "startTime": the start time of the test.
    - "orgName": the organization name.
    - "result": the test result (e.g., "passed" or "failed").
    - "duration": the time taken to execute the test in milliseconds.
    - "steps": an array of steps within the test.

- Each step includes:
    - "context": the description of the step (e.g., "Sign In Page Login Button").
    - "status": the result of the step (e.g., "passed" or "failed").
    - "duration": the time taken for this step in milliseconds.
    - "screenshot": any screenshot associated with the step (null if none).
    - "imgType": the type of image (e.g., "app").

- Additional information like "testVideo", "externalApiCalls", and "apiCalls" may also be present but are often empty or null.
"""

# Example queries that LLM can handle
print(agent.run(f"{json_structure_instruction} List all test case name we have"))
# print(agent.run(f"{json_structure_instruction} Summarize the failed test cases"))
# print(agent.run(f"{json_structure_instruction} Provide details for 'Test 2'"))
