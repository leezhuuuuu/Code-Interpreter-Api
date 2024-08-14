import json
import requests

# API endpoint
API_ENDPOINT = "https://api.openai.com/v1/chat/completions"
# Your API key
API_KEY = 'sk-xxxxxx'
# Model to use
MODEL = 'gpt-4o'

def run_program(code):
    """Run a given Python program and return the output"""
    try:
        # Prepare the request payload
        payload = {
            "languageType": "python",
            "variables": {},
            "code": code
        }
        
        # Send the request to the code execution endpoint
        response = requests.post("https://code.leez.tech/runcode", json=payload)
        
        # Parse the response
        response_json = response.json()
        result = {}
        if "output" in response_json:
            result["output"] = response_json["output"]
        if "images" in response_json:
            result["images"] = response_json["images"]
        
        # Print the response from https://code.leez.tech/runcode
        print("Response from https://code.leez.tech/runcode:")
        print(json.dumps(response_json, indent=4))
        
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})

def run_conversation(user_prompt):
    messages = [
        {
            "role": "system",
            "content": "You are a programming assistant. Use the run_program function to execute code and provide the results."
        },
        {
            "role": "user",
            "content": user_prompt,
        }
    ]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "run_program",
                "description": "Run a given Python program and return the output",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The Python code to execute",
                        }
                    },
                    "required": ["code"],
                },
            },
        }
    ]
    request_json = {
        "model": MODEL,
        "messages": messages,
        "tools": tools,
        "tool_choice": "auto",
        "max_tokens": 4096
    }

    # Print the request JSON
    print("Request JSON:")
    print(json.dumps(request_json, indent=4))

    # Send the request to the API
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    response = requests.post(API_ENDPOINT, headers=headers, data=json.dumps(request_json))

    # Print the response JSON
    print("Response JSON:")
    response_json = response.json()
    print(json.dumps(response_json, indent=4))

    response_message = response_json['choices'][0]['message']
    tool_calls = response_message.get('tool_calls', [])
    if tool_calls:
        available_functions = {
            "run_program": run_program,
        }
        messages.append(response_message)
        for tool_call in tool_calls:
            function_name = tool_call['function']['name']
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call['function']['arguments'])
            function_response = function_to_call(
                code=function_args.get("code")
            )
            messages.append(
                {
                    "tool_call_id": tool_call['id'],
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )
        second_request_json = {
            "model": MODEL,
            "messages": messages
        }

        # Print the second request JSON
        print("Second Request JSON:")
        print(json.dumps(second_request_json, indent=4))

        # Send the second request to the API
        second_response = requests.post(API_ENDPOINT, headers=headers, data=json.dumps(second_request_json))

        # Print the second response JSON
        print("Second Response JSON:")
        second_response_json = second_response.json()
        print(json.dumps(second_response_json, indent=4))

        return second_response_json['choices'][0]['message']['content']

# user_prompt = "计算9的11次方，并用中文输出结果。"
user_prompt = "使用python生成一个三角形图片"
print(run_conversation(user_prompt))