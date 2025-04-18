# core/message_router.py

from typing import Any, Dict
from camel.messages import BaseMessage


class MessageRouter:
    def __init__(self, agents: Dict[str, Any]):
        self.agents = agents

    def send(self, sender: str, receiver: str, content: str) -> str:
        msg = BaseMessage(role_name=sender, content=content)
        response = self.agents[receiver].step(msg)
        return response.content

    def broadcast(self, sender: str, receivers: list[str], content: str) -> Dict[str, str]:
        results: Dict[str, str] = {}
        for name in receivers:
            results[name] = self.send(sender, name, content)
        return results

