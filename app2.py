from langchain.agents import create_json_agent
from langchain.agents.agent_toolkits import JsonToolkit
from langchain.tools.json.tool import JsonSpec
import json
from langchain_ollama import ChatOllama
from langchain.tools import tool
import ollama
from langchain.agents import initialize_agent


# Chat model setup
llm = ChatOllama(
    model="gemma2",
    temperature=0.2
)
file = "./myJson.json"
with open(file, "r") as f:
    data = json.load(f)

@tool
def list_all_test_cases(input_text: str) -> str:
    """returns all test cases present in the file"""
    test_case_names = []

    # Loop through each suite and test to extract test case names
    for suite in data.get("suites", []):
        for test in suite.get("tests", []):
            test_case_names.append(test.get("name"))

    # Print out all test case names
    return "\n".join(test_case_names)

@tool
def summarize_failed_test_cases(input_text: str) -> str:
    """Summarizes the failed test cases"""
    failed_test_cases = []

    # Loop through each suite and test to extract failed test cases
    for suite in data.get("suites", []):
        for test in suite.get("tests", []):
            if test.get("result") == "failed":
                failed_test_cases.append(test.get("name"))

    # Print out all failed test cases
    return "\n".join(failed_test_cases)

# spec = JsonSpec(dict_={"test_case_data": data["test_case_data"]})
# toolkit = JsonToolkit(spec=spec)
tools = [list_all_test_cases , summarize_failed_test_cases]

agent = initialize_agent(
    agent='zero-shot-react-description',
    tools=tools,
    llm=llm,
    verbose=True
)

print(agent.run("summarize the failed test cases"))