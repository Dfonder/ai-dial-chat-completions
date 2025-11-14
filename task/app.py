import asyncio

from task.clients.custom_client import CustomDialClient
from task.constants import DEFAULT_SYSTEM_PROMPT
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role

async def start(stream: bool) -> None:
    deployment_name = "gpt-4"
    custom_client = CustomDialClient(deployment_name=deployment_name)
    conversation = Conversation()
    system_prompt = input(f"System prompt (Enter for default): ").strip()
    if not system_prompt:
        system_prompt = DEFAULT_SYSTEM_PROMPT
    conversation.add_message(Message(role=Role.SYSTEM, content=system_prompt))
    print("Type 'exit' to quit.")
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == "exit":
            print("Exiting chat.")
            break
        conversation.add_message(Message(role=Role.USER, content=user_input))
        if stream:
            print("AI (stream): ", end="", flush=True)
            response_msg = await custom_client.stream_completion(conversation.messages)
            response = response_msg.content
            print()
            #print(response)  # Выводим весь ответ
        else:
            response_msg = custom_client.get_completion(conversation.messages)
            response = response_msg.content
            print(f"AI: {response}")
        conversation.add_message(Message(role=Role.AI, content=response))

if __name__ == "__main__":
    asyncio.run(start(stream=True))  # или False для обычного режима