# Code Interpreter API

[English](https://github.com/leezhuuuuu/Code-Interpreter-Api/blob/main/README.md) | [中文](https://github.com/leezhuuuuu/Code-Interpreter-Api/blob/main/README_CN.md)

## Overview

The Code Interpreter API is a Flask-based application designed to provide an API interface for remotely running code and obtaining execution results. This project uses Docker containers for isolation, ensuring secure execution of Python code. Additionally, it supports storing generated image data in a PostgreSQL database and accessing it through an API endpoint.

## Technology Stack

- **Backend Framework**: Flask (Python)
- **Database**: PostgreSQL
- **Containerization**: Docker
- **ORM**: SQLAlchemy
- **Concurrency Handling**: threading, Queue
- **Authentication**: Bearer Token
- **External Requests**: requests
- **Code Isolation**: subprocess

## Features

- **Multi-language Support**: Currently primarily supports Python code execution.
- **Image Processing**: Supports converting code-generated image data to Base64 format and storing it in the database.
- **Docker Container Isolation**: Each code execution request runs in an independent Docker container, ensuring security and resource isolation.
- **PostgreSQL Database Integration**: Image data can be stored in the database and accessed via a RESTful API.
- **Authentication**: Optional Bearer token authentication to ensure secure access.
- **Environment Variables**: Configurable via environment variables.
- **Error Handling**: Comprehensive error handling and timeout management.

## Runtime Environment

- Python 3.8 or above
- Docker
- PostgreSQL

## Quick Start

### 1. Clone the Project

```bash
git clone https://github.com/leezhuuuuu/Code-Interpreter-Api.git
cd Code-Interpreter-Api
```

### 2. Configuration File

The project uses `config.yaml` as the configuration file. Ensure this file contains the following configurations:

- **Domain**: Used for accessing stored images.
- **Docker Image**: Specifies the Docker image used to run the code.
- **Port Range**: Specifies the port range for Docker containers.
- **PostgreSQL Configuration**: Includes database name, username, password, host, and port.
- **Resource Limits**: Specifies memory and CPU limits for Docker containers.
- **Timeout**: Specifies the timeout for code execution.

### 3. Install Dependencies

Make sure Docker is installed. Then, you can choose either of the following methods to obtain the Docker image:

#### Method 1: Build a Custom Image

Run `build.py`, which will automatically generate the `requirements.txt` file and build a custom image based on the configuration file, allowing customization of the container environment dependencies:

```bash
python build.py
```

#### Method 2: Pull a Pre-built Image

If you do not wish to build the image, you can directly pull a pre-built image from Docker Hub:

```bash
docker pull leezhuuu/code_interpreter:latest
```

### 4. Start the Project

Use the following command to start the project:

```bash
python center.py
```

This command will automatically start the Flask application and run it on the configured scheduler center port.

## Usage Guide

### 1. Run Code

You can run specified code by sending a POST or GET request to the `/runcode` endpoint. The request data should include the following fields:

- **languageType**: The language type of the code (currently only supports Python).
- **variables**: Optional, variables to pass to the code.
- **code**: The code to execute.

### 2. Access Images

You can retrieve image data stored in the database by sending a GET request to the `/image/<filename>` endpoint.

## API Endpoints

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

## Error Handling

The application returns appropriate HTTP status codes and error messages for different scenarios:

- **400 Bad Request**: Invalid JSON or parameters.
- **401 Unauthorized**: Missing or invalid token.
- **405 Method Not Allowed**: Invalid HTTP method.
- **504 Gateway Timeout**: Request timed out.

## Docker Integration

The application uses Docker to run code in isolated environments. You can choose to build a custom image or pull a pre-built image.

## PostgreSQL Integration

Image data generated during code execution is stored in a PostgreSQL database. The database connection details are configured in `config.yaml`.

## Concurrency Management

The application uses threads to handle multiple concurrent requests and uses semaphores to control the number of concurrent requests.

## Testing

The application includes a test suite that can be run to verify functionality:

```bash
python concurrent_test.py
```

## License

This project is under the GNU License. See the `LICENSE` file for more information.

## Contributing

Contributions are welcome! Please submit issues or pull requests.

## Authors

- leezhuuuuu

## Acknowledgments

- Flask
- Docker
- PostgreSQL
- SQLAlchemy
