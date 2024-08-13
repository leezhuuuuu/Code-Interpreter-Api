import aiohttp
import asyncio

async def post_request(session, url, headers, json_data):
    async with session.post(url, headers=headers, json=json_data) as response:
        response_text = await response.text()
        print(response_text)
        return response_text

async def main(concurrent_requests):
    url = 'http://127.0.0.1:8000/runcode'
    headers = {
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer 114514',
        'Accept': '*/*',
        'Host': '127.0.0.1:8000',
        'Connection': 'keep-alive'
    }
    json_data = {
        "languageType": "python",
        "variables": {},
        "code": "```python\nimport time\nprint('Hello from code block!')\ntime.sleep(3)\n```"
    }

    async with aiohttp.ClientSession() as session:
        tasks = [post_request(session, url, headers, json_data) for _ in range(concurrent_requests)]
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    concurrent_requests = 5  # 设置并发数
    asyncio.run(main(concurrent_requests))
