import yaml
import subprocess
import uuid
from flask import Flask, request, jsonify, redirect, url_for
from queue import Queue
import requests
import threading
import time
import os
import atexit
import base64
import signal
from sqlalchemy import create_engine, Column, String, LargeBinary, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import OperationalError, IntegrityError
import psycopg2
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

# 读取配置文件，指定编码为 utf-8
with open('config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)

DOMAIN = config['domain']
INTERPRETER_IMAGE = config['interpreter_image']
PORT_START = config['interpreter_port_range']['start']
PORT_END = config['interpreter_port_range']['end']
DEPENDENCIES = config['dependencies']
RESOURCE_LIMITS = config.get('resource_limits', {})
MEMORY_LIMIT = RESOURCE_LIMITS.get('memory')
CPU_LIMIT = RESOURCE_LIMITS.get('cpus')
POSTGRES = config['postgres']
TIMEOUT = config.get('timeout', 30)  # 默认超时时间为30秒
TIMEOUT_SECONDS = config.get('timeout_seconds', 60)  # 从配置中读取超时时间
SCHEDULER_PORT = config['scheduler_port']  # 自定义调度中心端口
HOST = config.get('host', '0.0.0.0')  # 自定义 host 地址

# 容器管理
containers = []
ports = list(range(PORT_START, PORT_END + 1))
lock = threading.Lock()
request_queue = Queue()
result_dict = {}  # 用于存储结果的字典
current_container_index = 0
semaphore = threading.Semaphore(len(ports))  # 控制并发请求的信号量

# 检查 PostgreSQL 容器是否存在
POSTGRES_CONTAINER_NAME = "postgres_code_interpreter"
POSTGRES_VOLUME_NAME = "postgres_code_interpreter_volume"

def is_postgres_container_running():
    result = subprocess.run(["docker", "ps", "-a", "--filter", f"name={POSTGRES_CONTAINER_NAME}", "--format", "{{.Names}}"], capture_output=True, text=True)
    return POSTGRES_CONTAINER_NAME in result.stdout.strip().split('\n')

def wait_for_postgres_ready():
    retry_attempts = 10
    retry_delay = 5  # seconds
    for attempt in range(retry_attempts):
        try:
            conn = psycopg2.connect(
                dbname=POSTGRES['db'],
                user=POSTGRES['user'],
                password=POSTGRES['password'],
                host=POSTGRES['host'],
                port=POSTGRES['port']
            )
            conn.close()
            print("PostgreSQL is ready")
            return True
        except psycopg2.OperationalError as e:
            print(f"Waiting for PostgreSQL to be ready: {e}")
            time.sleep(retry_delay)
    return False

if not is_postgres_container_running():
    subprocess.run([
        "docker", "run", "--name", POSTGRES_CONTAINER_NAME, "-d",
        "-e", f"POSTGRES_USER={POSTGRES['user']}",
        "-e", f"POSTGRES_PASSWORD={POSTGRES['password']}",
        "-e", f"POSTGRES_DB={POSTGRES['db']}",
        "-v", f"{POSTGRES_VOLUME_NAME}:/var/lib/postgresql/data",
        "-p", f"{POSTGRES['port']}:5432",
        "postgres"
    ], check=True)

    if not wait_for_postgres_ready():
        print("Failed to connect to PostgreSQL after multiple attempts.")
        exit(1)

# PostgreSQL 配置
DATABASE_URL = f"postgresql://{POSTGRES['user']}:{POSTGRES['password']}@{POSTGRES['host']}:{POSTGRES['port']}/{POSTGRES['db']}"
engine = None
Base = declarative_base()
Session = None
session = None

def init_db():
    global engine, Session, session
    retry_attempts = 5
    retry_delay = 5  # seconds
    for attempt in range(retry_attempts):
        try:
            engine = create_engine(DATABASE_URL)
            Session = sessionmaker(bind=engine)
            session = Session()
            Base.metadata.create_all(engine)  # 确保数据库模式已创建
            print("Database connection successful")
            break
        except OperationalError as e:
            print(f"Database connection failed: {e}")
            if attempt < retry_attempts - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Failed to connect to the database after multiple attempts.")
                raise

class Image(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String, unique=True, nullable=False)
    data = Column(LargeBinary, nullable=False)

init_db()

# 启动代码解释器容器
def start_container(port):
    container_name = f"code_interpreter_docker_{uuid.uuid4()}"
    run_command = [
        "docker", "run", "--name", container_name, "-d", "-p", f"{HOST}:{port}:5000"
    ]
    if MEMORY_LIMIT:
        run_command.extend(["--memory", MEMORY_LIMIT])
    if CPU_LIMIT:
        run_command.extend(["--cpus", CPU_LIMIT])
    run_command.append(INTERPRETER_IMAGE)
    
    subprocess.run(run_command, check=True)
    print(f"Started container {container_name} on port {port}")
    return container_name, port

def stop_container(container_name):
    subprocess.run(["docker", "stop", container_name])
    subprocess.run(["docker", "rm", container_name])
    print(f"Stopped and removed container {container_name}")

def start_containers():
    for port in ports:
        container_name, port = start_container(port)
        containers.append((container_name, port))

def stop_containers():
    for container_name, _ in containers:
        stop_container(container_name)

@app.route('/runcode', methods=['POST', 'GET'])
def run_code():
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400
    elif request.method == 'GET':
        query_string = request.query_string.decode('utf-8')
        data = {'query_string': query_string}
    else:
        return jsonify({'error': 'Invalid request method'}), 405

    request_id = str(uuid.uuid4())  # 生成一个唯一的请求ID
    request_queue.put((request_id, data))

    start_time = time.time()
    while time.time() - start_time < 10:  # 最多等待10秒
        if request_id in result_dict:
            output = result_dict.pop(request_id)
            # 处理返回结果，替换 base64 数据为链接
            if 'images' in output:
                try:
                    output = process_images(output)
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
            return jsonify(output), 200

        time.sleep(0.1)

    return jsonify({'error': 'Request timed out'}), 504

def process_images(output):
    images = output['images']
    for filename, base64_data in images.items():
        image_data = base64.b64decode(base64_data)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        image_record = Image(filename=unique_filename, data=image_data)
        try:
            session.add(image_record)
            session.commit()
        except IntegrityError as e:
            session.rollback()
            print(f"Database error: {e}")
            continue
        if DOMAIN:
            images[filename] = f"https://{DOMAIN}/image/{unique_filename}"
        else:
            images[filename] = f"http://{HOST}:{SCHEDULER_PORT}/image/{unique_filename}"
    return output

@app.route('/image/<filename>', methods=['GET'])
def serve_image(filename):
    image_record = session.query(Image).filter_by(filename=filename).first()
    if image_record:
        return image_record.data, 200, {'Content-Type': 'image/png'}
    return jsonify({'error': 'Image not found'}), 404

def handle_requests():
    global current_container_index
    while True:
        request_id, data = request_queue.get()
        if data is None:
            break

        semaphore.acquire()  # 获取信号量，确保不超过并发限制

        with lock:
            container_name, port = containers[current_container_index]
            current_container_index = (current_container_index + 1) % len(containers)

        try:
            if 'query_string' in data:
                response = requests.get(f"http://{HOST}:{port}/runcode?{data['query_string']}", timeout=TIMEOUT_SECONDS)
            else:
                response = requests.post(f"http://{HOST}:{port}/runcode", json=data, timeout=TIMEOUT_SECONDS)
            output = response.json()
        except requests.exceptions.Timeout:
            output = {'error': 'Code execution timed out'}
        except Exception as e:
            output = {'error': str(e)}
        
        result_dict[request_id] = output  # 将结果放入结果字典

        request_queue.task_done()
        print(f"Finished processing request {request_id}: {output}")

        # 异步重置容器
        reset_container(container_name, port)

def reset_container(container_name, port):
    threading.Thread(target=_reset_container, args=(container_name, port)).start()

def _reset_container(container_name, port):
    print(f"Resetting container {container_name}")
    stop_container(container_name)
    new_container_name, _ = start_container(port)
    with lock:
        for i, (name, p) in enumerate(containers):
            if name == container_name:
                containers[i] = (new_container_name, port)
                break
    semaphore.release()  # 释放信号量

def signal_handler(signal, frame):
    print('Stopping containers and exiting program...')
    stop_containers()
    if session:
        session.close()
    engine.dispose()
    os._exit(0)

signal.signal(signal.SIGINT, signal_handler)

# 启动多个工作线程来处理请求
for _ in range(len(ports)):
    threading.Thread(target=handle_requests).start()

start_containers()
atexit.register(stop_containers)

@app.route('/')
def index():
    return redirect("https://github.com/leezhuuuuu/Code-Interpreter-Api")

# Swagger 配置
SWAGGER_URL = '/doc'  # Swagger UI 的 URL
API_URL = '/static/swagger.yaml'  # Swagger 配置文件的 URL

# 创建 Swagger UI 蓝图
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={  # Swagger UI 配置
        'app_name': "Code Interpreter API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

if __name__ == '__main__':
    app.run(host=HOST, port=SCHEDULER_PORT, threaded=True)  # 使用自定义 host 和调度中心端口