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
{
    "suites": [
        {
            "name": "Suite 1",
            "startTime":"start time of suite",
            "tag": "org name",
            "specName": "spec name",
            "tests": [
                {
                   "name": "Test case name",
                   "startTime": "start time of test case",
                   "orgName": "org name",
                   "result": "test case result",
                   "duration": "duration of test case",
                    "steps": [
                          {
                            "context": "step context",
                            "status": "step status(passed/failed)",
                            "duration": "step duration",
                            "screenshot": "screenshot path",
                            "imgType": "image type"
                          }
                     ],
                     "testVideo": "test video link",
                     "externalApiCalls": [],
                     "apiCalls": [],
                     "error": "error message"
                }
            ]
        }
    ]
}
- The top-level key, "suites", is an array of test suites.
  - Each suite has:i
    - "name": the suite's name (e.g., "Domestic - Negative Flows").
    - "startTime": the suite's start time.
    - "tag": a label/tag for the suite.
    - "specName": the specification file associated with this suite.
    - "tests": an array of individual tests in the suite.

- Each test contains:
    - "name": the name of the test (e.g., "Login Flow").The test case name appended with suffix Retry 1, Retry 2, Retry 3 etc if retries are attempted for the test case..
    - "startTime": the start time of the test.
    - "orgName": the organization name.
    - "result": the test result (e.g., "passed" or "failed"),Consider the test case which has Retrying word in it's result as flaky test case.
    - "duration": the time taken to execute the test in milliseconds.
    - "steps": an array of steps within the test.
    - "error":this is the error message for test case failure(we will have this key for only failed test cases and flaky test cases) 

- Each step includes:
    - "context": the description of the step (e.g., "Sign In Page Login Button").
    - "status": the result of the step (e.g., "passed" or "failed").
    - "duration": the time taken for this step in milliseconds.
    - "screenshot": any screenshot associated with the step (null if none).
    - "imgType": the type of image (e.g., "app").

- Additional information like "testVideo", "externalApiCalls",error message and "apiCalls" may also be present but are often empty or null.
Remember a suite is not a test case. Suite is a collection of multiple test cases.
For summary based questions extract as detailed information as needed (e.g.,suite name, orgName,result, error message,failed step context from array of steps(error message and failed step context is available only for failed and flaky test cases)...etc) of test case.
Count Retries for Each Test Case:

For each unique test case, determine the number of retries.
Test cases are organized by suite, and each retry attempt has a suffix indicating the retry number (e.g.,(Retry 1),(Retry 2)).
Store the retry count for each unique test case.

A test case is considered as failed test case if test case result has value failed.
A test case is considered as flaky if the test case result value has Retrying in it.Never consider a flaky test case as failed test case.
For your reference I am providing sample json structure.The JSON file contains an array of suites each suite contains an array of test cases inside it.

name: The name of the test suite.
startTime: The start time of the suite.
tag: A tag categorizing the suite.
specName: The file path for the test spec.
tests: A list of test cases, each with:
  name: The name of the test.
  startTime: Start time of the test case.
  orgName: Organization name associated with the test.
  result: Result of the test (e.g., passed or failed).
  duration: Time taken to execute the test.
  steps: A list of steps within the test, where each step has:
    context: Description of the step.
    status: Outcome of the step (e.g., passed, failed).
    duration: Duration for the step.
    screenshot: Path to the screenshot, if available.
    imgType: Type of image (e.g., app).
  testVideo: Link to the test video, if available.
  externalApiCalls and apiCalls: Lists of API call details if any are present.
  error:failure reason

Our JSON is an array of suites.Each suite contains suite details along and an array of test cases in it.
"""

def generate_code_for_query(query: str) -> str:
    prompt = f"""
    {json_structure_description}
    Based on the JSON structure provided, write a complete Python function named `get_result` to answer the following query using the JSON data. 
    For queries that include "how many and what are they, how many and why" type of questions, return total count along with details.
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

    system_prompt = f"""You are pro data analyzer. 
    Your task is to analyze the data and respond to user queries with clear, structured information.
    Based on the query follow given format if it's necessary.Otherwise use exact data.
   For summary based queries follow below format. 
   List each failed test case individually without grouping similar entries.
   Ensure your response follows the **exact same format** for each chunk. 
   Use data fields like suite name, test case name, orgName, error message, failed steps from the data if they exists in the data otherwise don't use.
   Use the example below as a template to display data you have and adhere to this structure consistently across all responses:

    Respond to the following summary-based query by only displaying the fields where data is provided.
    For each detail, include the information only if it is available; if any specific detail is missing, do not display that field in the response.
    Here is the format to follow:
    Test Case Name: [Test case name]
       Org Name: [Org name](Display only if orgName is available)
       Failure Reason: [Error message] (Display only if you have a specific error message and do not display if "result" is given instead)
       Failed Step: [Failed step description] (Display only if a failed step description is available)

    For queries that starts with 'how many', use provided data and generate response according to the user query in human understandable format.
    For queries that include how many and what, how many and why respond for "how many" first like give the count you have with you and give details for what/why from the data you have.
    Each response must strictly follow this format to ensure uniformity.  
    Respond in this exact format without adding any commentary, grouping, or summarizing. 
    List every test case with a failure explicitly, even if they share the same error message.
    Do not repeat or include the user's query, any raw data, or any information that does not match the user query. Again I remembering you that Answer concisely without repeating the question."""
    # Convert result to JSON and chunk it if it's too large
    
    #chunk_size = 1000  # Adjust based on LLM limits and performance
    response_parts = []
     # Determine chunking approach based on data type
    if isinstance(result, list):
        # If result is a list, process items in chunks
        print("DATA IN LIST")
        chunk_size = 10  # Adjust based on list length and LLM limits
        result_chunks = [result[i:i+chunk_size] for i in range(0, len(result), chunk_size)]
    elif isinstance(result, dict):
        print("DATA IN DICT")
        chunk_size = 10
        # If result is a dictionary, process each key-value pair
        result_chunks = []
        for k, v in result.items():
            if isinstance(v, list) and len(v) > chunk_size:
                # Chunk lists within the dictionary
                value_chunks = [v[i:i+chunk_size] for i in range(0, len(v), chunk_size)]
                for chunk in value_chunks:
                    result_chunks.append({k: chunk})
            elif isinstance(v, str) and len(v) > 500:
                # Split large strings within the dictionary
                value_chunks = [v[i:i+500] for i in range(0, len(v), 500)]
                for chunk in value_chunks:
                    result_chunks.append({k: chunk})
            else:
                # If value is manageable, add it as-is
                result_chunks.append({k: v})
        #result_chunks = [{k: v} for k, v in result.items()]
    elif isinstance(result, str):
        # If result is a large string, split it into manageable chunks
        print("DATA IN STRING")
        chunk_size = 1000  # Adjust based on LLM limits
        result_chunks = [result[i:i+chunk_size] for i in range(0, len(result), chunk_size)]
    else:
        # For any other type, treat as a single chunk (e.g., int, float)
        print("DATA IN ELSE")
        result_chunks = [str(result)]

    # Loop through each chunk and get LLM response
    print("RESULT CHUNKS",result_chunks)
    for chunk in result_chunks:
        print("PROCESSING CHUNK", chunk)
        system_prompt = system_prompt.format(query=query, chunk_data=chunk)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"user_query: {query}, data: {chunk}"}
        ]

        response = llm.invoke(messages)
        response_parts.append(response.content)

    # Combine responses from all chunks
    #final_response = "\n".join(response_parts)
    final_response = "\n".join(part.strip() for part in response_parts)
    print("Agent Combined Response:", final_response)


user_query = input("please ask your question:")
process_query(user_query)


