import yaml
import subprocess

# 读取配置文件，指定编码为 utf-8
with open('config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)

DEPENDENCIES = config['dependencies']
INTERPRETER_IMAGE = config['interpreter_image']

# 动态生成 requirements.txt
def generate_requirements(dependencies):
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        for dep in dependencies:
            f.write(f"{dep}\n")

generate_requirements(DEPENDENCIES)
print("Generated requirements.txt with specified dependencies.")

# 构建 Docker 镜像
def build_docker_image(image_name):
    build_command = ["docker", "build", "-t", image_name, "."]
    subprocess.run(build_command, check=True)
    print(f"Built Docker image {image_name}")

build_docker_image(INTERPRETER_IMAGE)


