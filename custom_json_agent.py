from langchain.agents import initialize_agent
from langchain.tools import tool
from code_generator_agent import generate_code_for_query  # Function to generate tool code
import json
from langchain_ollama import ChatOllama

# Load JSON data
file = "./myJson.json"
with open(file, "r") as f:
    data = json.load(f)
    json_data = data  # Save a copy of the data for the generated tool

# Initialize list to store tools
tools = []

def process_query(query: str):
    """
    Processes the user query by generating a tool dynamically and adding it to the agent.
    """
    # Step 1: Generate Python code for the tool based on the user query
    generated_code = generate_code_for_query(query)
    print(f"Generated Code:\n{generated_code}")  # Optional: print code for debugging

     # Step 2: Execute the generated code to define the function as-is
    local_vars = {}
    try:
        # Execute generated code, binding 'data' to 'json_data' for the generated function's use
        exec(generated_code, {"json_data": data}, local_vars)
    except Exception as e:
        print("Error during code execution:", e)
        return
    

    
    # Step 3: Extract the generated `get_result` function
    get_result_function = local_vars["get_result"]

    # step 4: Execute the generated function to get the result
    try:
        result = get_result_function(json)
        print("Result from the generated function:", result)
    except Exception as e:
        print("Error executing the generated function:", e)
        return
    
    # Step 5: Register the generated function as a LangChain tool
    tool_decorator = tool(get_result_function(json_data))
    tools.append(tool_decorator)  # Add the decorated tool to tools list

    # Step 6: Reinitialize the agent with the updated tools list
    llm = ChatOllama(model="gemma2", temperature=0.2)
    agent = initialize_agent(
        agent="zero-shot-react-description", 
        tools=tools, llm=llm, 
        verbose=True
    )

    # Debug data structure right before running query
    print("Data structure provided to the tool:", type(data))

    # Run the query with the agent and return the response
    try:
        response = agent.run(query)
        print("Agent Response:", response)
    except TypeError as e:
        print("TypeError encountered while processing query:", e)

# Example of using process_query
process_query("Summarize the failed test cases")
