import yaml
import subprocess
import os

# 读取配置文件，指定编码为 utf-8
with open('config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)

DEPENDENCIES = config['dependencies']
INTERPRETER_IMAGE = config['interpreter_image']
# 从配置文件中读取代理设置
HTTP_PROXY = config.get('http_proxy', '')
HTTPS_PROXY = config.get('https_proxy', '')

# 动态生成 requirements.txt
def generate_requirements(dependencies):
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        for dep in dependencies:
            f.write(f"{dep}\n")

generate_requirements(DEPENDENCIES)
print("Generated requirements.txt with specified dependencies.")

# 构建 Docker 镜像
def build_docker_image(image_name):
    build_command = [
        "docker", "build",
        "--build-arg", f"HTTP_PROXY={HTTP_PROXY}",
        "--build-arg", f"HTTPS_PROXY={HTTPS_PROXY}",
        "-t", image_name,
        "."
    ]
    
    # 设置环境变量
    env = os.environ.copy()
    if HTTP_PROXY:
        env['HTTP_PROXY'] = HTTP_PROXY
    if HTTPS_PROXY:
        env['HTTPS_PROXY'] = HTTPS_PROXY
    
    subprocess.run(build_command, check=True, env=env)
    print(f"Built Docker image {image_name}")

build_docker_image(INTERPRETER_IMAGE)
