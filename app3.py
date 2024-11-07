from langchain_ollama import ChatOllama
import ollama
import json
from langchain.agents import tool, initialize_agent
from langchain_community.agent_toolkits.load_tools import load_tools

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
def list_failed_test_cases(input_text: str) -> str:
    """Summarizes the failed test cases"""
    failed_test_cases = []
    failed_test_cases_count = 0
    # Loop through each suite and test to extract failed test cases
    for suite in data.get("suites", []):
        for test in suite.get("tests", []):
            if test.get("result") == "failed":
                failed_test_cases_count += 1
                failed_test_cases.append(test.get("name"))

    # Print out all failed test cases
    # return "\n".join(failed_test_cases)
    return f"Total failed test cases: {failed_test_cases_count}\n" + "\n".join(failed_test_cases)

@tool
def list_passed_test_cases(input_text: str) -> str:
    """Summarizes the passed test cases"""
    passed_test_cases = []
    passed_test_cases_count = 0
    # Loop through each suite and test to extract passed test cases
    for suite in data.get("suites", []):
        for test in suite.get("tests", []):
            if test.get("result") == "passed":
                passed_test_cases_count += 1
                passed_test_cases.append(test.get("name"))

    # Print out all passed test cases
    # return "\n".join(passed_test_cases)
    return f"Total passed test cases: {passed_test_cases_count}\n" + "\n".join(passed_test_cases)
tools = [list_all_test_cases, list_failed_test_cases , list_passed_test_cases]

agent = initialize_agent(
    llm=llm,
    tools=tools,
    verbose=True
)

print(agent.run("how many passes test cases are there?"))
print(agent.run("how many failed test cases are there?"))
print(agent.run("list all test cases"))
