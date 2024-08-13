from flask import Flask, request, jsonify, Response, render_template_string
import subprocess
import sys
import threading
import time
import requests
from functools import wraps
import urllib.parse
import re
import json
import base64
import os
import glob

app = Flask(__name__)

# 从环境变量中读取配置，如果未设置则使用默认值
OUTPUT_BASE64 = os.getenv('OUTPUT_BASE64', 'True').lower() == 'true'
AUTH_TOKEN = os.getenv('AUTH_TOKEN', '')
# HOST = os.getenv('HOST', '127.0.0.1')
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))
TIMEOUT = int(os.getenv('TIMEOUT', 30))
REMOVE_PYTHON_CODE_BLOCK = os.getenv('REMOVE_PYTHON_CODE_BLOCK', 'True').lower() == 'true'

# 配置变量，决定是否启用单元测试，默认启用
ENABLE_UNIT_TESTS = False

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if AUTH_TOKEN:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Authorization header is missing or invalid'}), 401
            token = auth_header.split('Bearer ')[1]
            if token != AUTH_TOKEN:
                return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

def extract_code(code):
    if REMOVE_PYTHON_CODE_BLOCK:
        match = re.search(r'```python\s*(.*?)\s*```', code, re.DOTALL)
        if match:
            return match.group(1)
    return code

def run_code(language, code, variables, timeout):
    try:
        # 根据语言类型选择解释器
        if language == 'python':
            # 提取代码中的有效部分
            code = extract_code(code)
            # 将变量注入到代码环境中
            var_definitions = '\n'.join(f"{key} = {value}" for key, value in variables.items())
            code_with_vars = f"{var_definitions}\n{code}"
            # 使用subprocess运行代码
            result = subprocess.run([sys.executable, '-c', code_with_vars], capture_output=True, text=True, timeout=timeout)
            return result.stdout, result.stderr
        else:
            return None, "Unsupported language"
    except subprocess.TimeoutExpired:
        return None, "Code execution timed out"
    except Exception as e:
        return None, str(e)

def convert_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

def unescape_string(s):
    return s.encode('utf-8').decode('unicode_escape')

@app.route('/runcode', methods=['POST', 'GET'])
@auth_required
def run_code_endpoint():
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400
        language = data.get('languageType', 'python')
        variables = data.get('variables', {})
        code = data.get('code', '')
    elif request.method == 'GET':
        query_string = request.query_string.decode('utf-8')
        print("Query String:",query_string)
        # 检查query_string中是否有"+"
        if '+' in query_string:
            # query_string的+替换为空格
            query_string = re.sub(r'\+', ' ', query_string)
            print("Query String:",query_string)

        # 如果没有+，则直接输出query_string
        else:
            print("Query String:",query_string)


        # 使用正则表达式提取参数
        language_match = re.search(r'languageType=("?)([^"&]+)\1', query_string)
        variables_match = re.search(r'variables=("?)([^"&]+)\1', query_string)
        code_match = re.search(r'code=("?)([^"&]+)\1', query_string)
        print("code_match:",code_match)
        if not language_match or not variables_match or not code_match:
            return jsonify({'error': 'Invalid parameters'}), 400
        

        
        language = urllib.parse.unquote(language_match.group(2))
        variables = urllib.parse.unquote(variables_match.group(2))
        code = urllib.parse.unquote(code_match.group(2))
        print("code:",code)
        
        # 处理转义字符
        language = unescape_string(language)
        variables = unescape_string(variables)
        code = unescape_string(code)
        print("code:",code)
        
        try:
            variables = json.loads(variables)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid variables format'}), 400
        
        # 打印解析后的JSON参数
        print("Parsed JSON Parameters:")
        print(json.dumps({
            'languageType': language,
            'variables': variables,
            'code': code
        }, indent=4))
    else:
        return jsonify({'error': 'Unsupported HTTP method'}), 405

    # 运行代码
    stdout, stderr = run_code(language, code, variables, TIMEOUT)

    if stderr:
        return jsonify({'error': stderr}), 400
    else:
        # 查找当前目录中的所有图片文件
        image_files = glob.glob('*.png') + glob.glob('*.jpg') + glob.glob('*.jpeg') + glob.glob('*.gif')
        
        if image_files:
            image_data = {}
            for image_path in image_files:
                encoded_image = convert_image_to_base64(image_path)
                image_data[image_path] = encoded_image
                os.remove(image_path)  # 删除生成的图片文件

            if not OUTPUT_BASE64:
                # 如果 OUTPUT_BASE64 不是 True，则输出原始图片
                html_content = ''.join([f'<img src="{image_path}" alt="{image_path}" />' for image_path in image_data.keys()])
                return Response(html_content, mimetype='text/html')

            else:
                return jsonify({'output': stdout, 'images': image_data}), 200
        else:
            return jsonify({'output': stdout}), 200

@app.route('/', methods=['GET'])
def welcome_page():
    return render_template_string('<h1>欢迎使用lee\'s code-interpreter</h1>')

def run_test_case(test_case):
    url = f'http://{HOST}:{PORT}/runcode'
    if test_case['method'] == 'GET':
        params = {
            'languageType': test_case['language'],
            'variables': test_case['variables'],
            'code': test_case['code']
        }
        headers = {'Authorization': f'Bearer {AUTH_TOKEN}'} if AUTH_TOKEN else {}
        print("Request Params:")
        print(params)

        response = requests.get(url, params=params, headers=headers)
    elif test_case['method'] == 'POST':
        data = {
            'languageType': test_case['language'],
            'variables': test_case['variables'],
            'code': test_case['code']
        }
        headers = {'Authorization': f'Bearer {AUTH_TOKEN}'} if AUTH_TOKEN else {}
        print("Request Data:")
        print(data)

        response = requests.post(url, json=data, headers=headers)
    else:
        raise ValueError("Unsupported HTTP method in test case")

    # 打印返回JSON
    print("Response JSON:")
    print(response.json())

def test_run_code_endpoint():
    test_cases = [
        {
            'method': 'GET',
            'language': 'python',
            'variables': str({}),
            'code': "print('Hello, World!')"
        },
        {
            'method': 'GET',
            'language': '"python"',
            'variables': str({}),
            'code': '"print(\'Hello, World!\')"'
        },
        {
            'method': 'GET',
            'language': 'python',
            'variables': str({}),
            'code': "print('Hello%20World')"
        },
        {
            'method': 'POST',
            'language': 'python',
            'variables': {},
            'code': "print(5 ** 11)"
        },
        {
            'method': 'POST',
            'language': 'python',
            'variables': {'m': 7, 'n': 4},
            'code': "print(m * n)"
        },
        {
            'method': 'POST',
            'language': 'python',
            'variables': {},
            'code': "```python\nprint('Hello from code block!')\n```"
        }
    ]

    for test_case in test_cases:
        run_test_case(test_case)

if __name__ == '__main__':
    # 启动Flask应用
    threading.Thread(target=app.run, kwargs={'host': HOST, 'port': PORT, 'debug': False}).start()

    # 等待Flask应用启动
    time.sleep(1)

    # 运行单元测试
    if ENABLE_UNIT_TESTS:
        test_run_code_endpoint()
        print("All tests executed!")