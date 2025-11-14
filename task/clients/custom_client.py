import json
import aiohttp
import requests

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT, API_KEY
from task.models.message import Message
from task.models.role import Role

class CustomDialClient(BaseClient):
    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        # Используем короткое имя модели для endpoint
        self.model_name = deployment_name
        self._endpoint = f"{DIAL_ENDPOINT}/openai/deployments/{self.model_name}/chat/completions"

    def get_completion(self, messages: list[Message]) -> Message:
        headers = {
            "api-key": API_KEY,  # маленькими!
            "Content-Type": "application/json"
        }
        request_data = {
            "model": self.model_name,  # добавляем model
            "messages": [msg.to_dict() for msg in messages]
        }
        # --- Печать сообщения, отправляемого к модели ---
        print("\n--- MESSAGE TO MODEL (get_completion) ---")
        print(json.dumps(request_data, indent=2, ensure_ascii=False))
        print("--- END MESSAGE ---\n")
        response = requests.post(self._endpoint, headers=headers, json=request_data)
        print(f"Response: {response.text}")
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        resp_json = response.json()
        choices = resp_json.get("choices", [])
        if not choices or "message" not in choices[0]:
            raise Exception("No choices in response found")
        content = choices[0]["message"]["content"]
        print(f"AI: {content}")
        return Message(role=Role.AI, content=content)

    async def stream_completion(self, messages: list[Message]) -> Message:
        headers = {
            "api-key": API_KEY,  # маленькими!
            "Content-Type": "application/json"
        }
        request_data = {
            "model": self.model_name,  # добавляем model
            "stream": True,
            "messages": [msg.to_dict() for msg in messages]
        }
        # --- Печать сообщения, отправляемого к модели ---
        print("\n--- MESSAGE TO MODEL (stream_completion) ---")
        print(json.dumps(request_data, indent=2, ensure_ascii=False))
        print("--- END MESSAGE ---\n")
        contents = []
        async with aiohttp.ClientSession() as session:
            async with session.post(self._endpoint, headers=headers, json=request_data) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    print(f"Response: {text}")
                    raise Exception(f"HTTP {resp.status}: {text}")
                async for line in resp.content:
                    chunk = line.decode("utf-8").strip()
                    if not chunk or not chunk.startswith("data: "):
                        continue
                    data = chunk[len("data: "):]
                    if data == "[DONE]":
                        break
                    snippet = self._get_content_snippet(data)
                    print(snippet, end="", flush=True)
                    contents.append(snippet)
        full_content = "".join(contents)
        return Message(role=Role.AI, content=full_content)

    def _get_content_snippet(self, data: str) -> str:
        try:
            chunk_json = json.loads(data)
            choices = chunk_json.get("choices", [])
            if choices and "delta" in choices[0]:
                return choices[0]["delta"].get("content", "")
            return ""
        except Exception as e:
            print(f"Error parsing chunk: {e}")
            return ""