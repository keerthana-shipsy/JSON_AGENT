from langchain.agents import create_json_agent
from langchain.agents.agent_toolkits import JsonToolkit
from langchain.tools.json.tool import JsonSpec
import json
from langchain_ollama import ChatOllama
import ollama

# Chat model setup
llm = ChatOllama(
    model="gemma2",
    temperature=0.2
)

file = "./myJson.json"
with open(file, "r") as f1:
    data = json.load(f1)
    f1.close()

spec = JsonSpec(dict_={"test_case_data": data["test_case_data"]})
toolkit = JsonToolkit(spec=spec)

agent = create_json_agent(
    llm = llm,
    toolkit=toolkit,
    verbose=True,
    allow_dangerous_code=True,
    hanle_validation_error=True
)

print(agent.run("what are all the test cases present in the file?"))
