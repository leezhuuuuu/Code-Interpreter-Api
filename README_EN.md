# Code Interpreter API 🚀

[English](https://github.com/leezhuuuuu/Code-Interpreter-Api/blob/main/README_EN.md) | [中文](https://github.com/leezhuuuuu/Code-Interpreter-Api/blob/main/README.md)

[![](https://img.shields.io/github/license/leezhuuuuu/Code-Interpreter-Api.svg)](LICENSE)
![](https://img.shields.io/github/stars/leezhuuuuu/Code-Interpreter-Api.svg)
![](https://img.shields.io/github/forks/leezhuuuuu/Code-Interpreter-Api.svg)
![](https://img.shields.io/docker/pulls/leezhuuu/code_interpreter.svg)

## Overview 🌟

Code Interpreter API is a project that integrates a scheduling center with a sandbox environment, dedicated to creating the world's best code interpreter. It aims to provide a secure and reliable API interface for remotely running code and obtaining execution results, accelerating the development of various AI Agents. This project innovatively combines Docker container technology to achieve secure isolated execution of Python code. Additionally, the project supports storing generated image data in a PostgreSQL database and accessing it through API endpoints, offering rich data processing and storage capabilities.
You can access a demo built with Fastgpt [here](https://fastgpt.leez.tech/chat/share?shareId=emvjwl8hgqu4pj314k7yakpp).

## Project Status 📊

You can view the real-time running status, performance metrics, and availability information of this project by visiting our [status monitoring page](https://status.leez.tech/).

## Tech Stack 🛠️

- **Backend Framework**: Flask (Python)
- **Database**: PostgreSQL
- **Containerization**: Docker
- **ORM**: SQLAlchemy
- **Concurrency Handling**: threading, Queue
- **Authentication**: Bearer Token
- **External Requests**: requests
- **Code Isolation**: subprocess

## Features 🌈

- **Multi-language Support**: Currently mainly supports Python code execution.
- **Image Processing**: Supports converting code-generated image data to Base64 format and storing it in the database.
- **Docker Container Isolation**: Each code execution request runs in an isolated Docker container, ensuring security and resource isolation.
- **PostgreSQL Database Integration**: Image data can be stored in the database and accessed via RESTful API.
- **Authentication**: Optional Bearer token authentication to ensure secure access.
- **Environment Variables**: Configurable through environment variables.
- **Error Handling**: Comprehensive error handling and timeout management.

## Running Environment 🖥️

- Python 3.8 and above
- Docker
- PostgreSQL

## Quick Start 🚀

### 1. Clone the Project

```bash
git clone https://github.com/leezhuuuuu/Code-Interpreter-Api.git
cd Code-Interpreter-Api
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configuration File

The project uses `config.yaml` as the configuration file. Ensure the file contains the following configurations:

- **Domain**: For accessing stored images.
- **Docker Image**: Specify the Docker image used for running code.
- **Port Range**: Specify port range for Docker containers.
- **PostgreSQL Configuration**: Including database name, username, password, host, and port.
- **Resource Limits**: Specify memory and CPU limits for Docker containers.
- **Timeout**: Specify timeout for code execution.

### 4. Get Docker Image

Ensure Docker is installed. Then, you can choose one of the following two methods to get the Docker image:

#### Method 1: Build Custom Image

Run `build.py`, which will automatically generate a `requirements.txt` file based on the configuration file and build a custom image. You can customize the container environment dependencies according to your needs:

```bash
python3 build.py
```

#### Method 2: Pull Pre-built Image

If you don't want to build the image, you can directly pull the pre-built image from Docker Hub:

```bash
docker pull leezhuuu/code_interpreter:latest
```

### 5. Start the Project

Use the following command to start the project:

```bash
python3 center.py
```

This command will automatically start the Flask application and run it on the configured scheduling center port.

## Usage Guide 📖

### 1. Run Code

Access the `/runcode` endpoint via POST or GET request to run specified code. The request data should include the following fields:

- **languageType**: The language type of the code (currently only supports Python).
- **variables**: Optional, variables to be passed to the code.
- **code**: The code to be executed.

### 2. Access Images

Access the `/image/<filename>` endpoint via GET request to retrieve image data stored in the database.

## API Endpoints 🌐

### `POST /runcode`

#### Request

```json
{
  "languageType": "python",
  "variables": {},
  "code": "print('Hello, World!')"
}
```

#### Response

```json
{
  "output": "Hello, World!\n"
}
```
[![Run in Hoppscotch](https://hopp.sh/badge.svg)](https://hopp.sh/r/hqyKw95KDVnl)

### `GET /runcode`

#### Request

```
/runcode?languageType=python&variables={}&code=print('Hello, World!')
```

#### Response

```json
{
  "output": "Hello, World!\n"
}
```
[![Run in Hoppscotch](https://hopp.sh/badge.svg)](https://hopp.sh/r/UEkwk6u6Howq)

### `POST /runcode` Complex Example

#### Request

```json
{
  "languageType": "python",
  "variables": {},
  "code": "import matplotlib.pyplot as plt\nimport numpy as np\n\n# Define vertices of the triangle\nvertices = np.array([[0, 0], [1, 0], [0.5, np.sqrt(3)/2], [0, 0]])\n\n# Create a new figure\nplt.figure()\n\n# Plot the triangle\nplt.plot(vertices[:, 0], vertices[:, 1], 'b-')\n\n# Set axis limits\nplt.xlim(-0.1, 1.1)\nplt.ylim(-0.1, 1.1)\n\n# Save the plot as triangle.png\nplt.savefig('triangle.png')\nplt.close()"
}
```

#### Response

```json
{
  "images": {
    "triangle.png": "https://code.leez.tech/image/cec3bee5-c45b-47c5-814f-7dc90831450e_triangle.png"
  },
  "output": ""
}
```
[![Run in Hoppscotch](https://hopp.sh/badge.svg)](https://hopp.sh/r/8c2Q1nPhuTg3)

## Error Handling 🚨

The application returns appropriate HTTP status codes and error messages for different scenarios:

- **400 Bad Request**: Invalid JSON or parameters.
- **401 Unauthorized**: Missing or invalid token.
- **405 Method Not Allowed**: Invalid HTTP method.
- **504 Gateway Timeout**: Request timeout.

## Docker Integration 🐳

The application uses Docker to run code in an isolated environment. You can choose to build a custom image or pull a pre-built image.

## PostgreSQL Integration 🐘

Images generated during code execution are stored in the PostgreSQL database. Database connection details are configured in `config.yaml`.

## Concurrency Management 🔄

The application uses threads to handle multiple concurrent requests and uses semaphores to control the number of concurrent requests.

## Testing 🧪

### Concurrency Testing

The application includes a concurrency test script `concurrent_test.py` that can be run to verify concurrent functionality:

```bash
python3 concurrent_test.py
```

## License 📄

This project is licensed under the GNU License. See the `LICENSE` file for details.

## Contributing 🤝

Contributions are welcome! Please submit issues or pull requests.

## Author ✍️

- leezhuuuuu

## Acknowledgements 🙏

- Flask
- Docker
- PostgreSQL
- SQLAlchemy

## GitHub Star History

[![Star History Chart](https://api.star-history.com/svg?repos=leezhuuuuu/Code-Interpreter-Api&type=Date)](https://star-history.com/#leezhuuuuu/Code-Interpreter-Api&Date)