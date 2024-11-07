from langchain_ollama import ChatOllama
import json
import re  # Import the 're' module for regular expressions

# Initialize the Ollama model
llm = ChatOllama(
    model="gemma2",
    temperature=0.2
)

file = "./myJson.json"
with open(file, "r") as f:
    data = json.load(f)

# Define the JSON structure as a prompt context
json_structure_description = """
The JSON file contains information about test suites and their execution details. Here is the structure to understand:

- The top-level key, "suites", is an array of test suites.
  - Each suite has:
    - "name": the suite's name (e.g., "Domestic - Negative Flows").
    - "startTime": the suite's start time.
    - "tag": a label/tag for the suite.
    - "specName": the specification file associated with this suite.
    - "tests": an array of individual tests in the suite.

- Each test contains:
    - "name": the name of the test (e.g., "Login Flow").
    - "startTime": the start time of the test.
    - "orgName": the organization name.
    - "result": the test result (e.g., "passed" or "failed"),Consider the test case which has Retrying word in it's result as flaky test case.
    - "duration": the time taken to execute the test in milliseconds.
    - "steps": an array of steps within the test.

- Each step includes:
    - "context": the description of the step (e.g., "Sign In Page Login Button").
    - "status": the result of the step (e.g., "passed" or "failed").
    - "duration": the time taken for this step in milliseconds.
    - "screenshot": any screenshot associated with the step (null if none).
    - "imgType": the type of image (e.g., "app").

- Additional information like "testVideo", "externalApiCalls", and "apiCalls" may also be present but are often empty or null.
Remember a suite is not a test case. Suite is a collection of multiple test cases.For your reference I am providing sample json structure.
The JSON file includes multiple test suites, each containing:

name: The name of the test suite.
startTime: The start time of the suite.
tag: A tag categorizing the suite.
specName: The file path for the test spec.
tests: A list of test cases, each with:
  name: The name of the test.
  startTime: Start time of the test case.
  orgName: Organization name associated with the test.
  esult: Result of the test (e.g., passed or failed).
  duration: Time taken to execute the test.
  steps: A list of steps within the test, where each step has:
    context: Description of the step.
    status: Outcome of the step (e.g., passed, failed).
    duration: Duration for the step.
    screenshot: Path to the screenshot, if available.
    imgType: Type of image (e.g., app).
  testVideo: Link to the test video, if available.
  externalApiCalls and apiCalls: Lists of API call details if any are present.
"""

def generate_code_for_query(query: str) -> str:
    prompt = f"""
    {json_structure_description}
    Based on the JSON structure provided, write a complete Python function named `get_result` to answer the following query using the JSON data. 

    Requirements:
    - The code must be wrapped within a function.
    - The function should accept a single parameter, `json_data`, which represents the JSON data and keep default value as json_data for the parameter.
    - **Do not include** any imports, comments, explanations, or additional content outside the function.
    - Your response should contain **only the Python function code** with the logic wrapped within the function.

    Query: "{query}"

    Python Code:
    """

    # Generate Python code based on the structured prompt
    messages = [
        {"role": "system", "content": "You are an assistant that generates Python code to process JSON data based on its structure."},
        {"role": "user", "content": prompt}
    ]

    code_response = llm.invoke(messages)
    print("code response",code_response)
    return re.sub(r"```(?:python)?|```", "", code_response.content).strip()

def execute_generated_code(code: str, data: dict) -> str:
    local_vars = {"json_data": data}  # Pass data as json_data to match function signature
    try:
        # Execute the generated function code to define it in the environment
        exec(code, {}, local_vars)

        # Extract the function name from the code if needed, then call it
        function_name = list(local_vars.keys())[1]  # The second key is the function name

        # Call the function with the JSON data and return the result
        result = local_vars[function_name](data)
    except Exception as e:
        result = f"Error executing code: {e}"
    return result

def custom_json_query_agent(query: str):
    print(f"User Query: {query}")
    code = generate_code_for_query(query)
    print(f"Generated Python Code:\n{code}")
    result = execute_generated_code(code, data)
    print(f"Execution Result:\n{result}")
    return result

# Example query
# custom_json_query_agent("how many flaky test cases are there")


def process_query(query:str):

    print(f"User Query: {query}")
    result = custom_json_query_agent(query)

    print(f"Agent Response: {result}")

    system_prompt = f"""You are an QA automation engineer who is working on a project that involves analyzing test results from JSON data.
    You have been given the user query and the data that is extracted fron JSON file.
    Your task is to analyze data and provide the response to the user query.While summarizing """
    

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"user_query: {query}, data: {result}"}
    ]

    response = llm.invoke(messages)
    print("Agent Response:", response.content)

process_query("Summarize the failed test cases")

