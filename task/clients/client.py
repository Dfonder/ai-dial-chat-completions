from aidial_client import Dial, AsyncDial

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT, API_KEY
from task.models.message import Message
from task.models.role import Role

class DialClient(BaseClient):

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        self.client = Dial(
            base_url=DIAL_ENDPOINT,
            api_key=API_KEY
        )
        self.async_client = AsyncDial(
            base_url=DIAL_ENDPOINT,
            api_key=API_KEY
        )
        self.deployment_name = deployment_name

    def get_completion(self, messages: list[Message]) -> Message:
        messages_dict = [m.to_dict() for m in messages]
        response = self.client.chat.completions.create(
            messages=messages_dict,
            deployment_name=self.deployment_name
        )
        choices = getattr(response, "choices", None)
        if not choices or len(choices) == 0:
            raise Exception("No choices in response found")
        content = choices[0].message.content
        print(f"AI: {content}")
        return Message(role=Role.AI, content=content)

    async def stream_completion(self, messages: list[Message]) -> Message:
        messages_dict = [m.to_dict() for m in messages]
        response = await self.async_client.chat.completions.create(
            messages=messages_dict,
            deployment_name=self.deployment_name,
            stream=True
        )
        choices = getattr(response, "choices", None)
        if not choices or len(choices) == 0:
            raise Exception("No choices in response found")
        content = choices[0].message.content
        print(content, end="", flush=True)
        print()
        return Message(role=Role.AI, content=content)