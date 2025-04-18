import json
import logging
from camel.agents import ChatAgent
from services.deepseek_api import DeepSeekModel
from core.data_models import Coordinates, CommuteInfo


class CommuteAgent:
    """
    Calculates travel time and distance between two coordinates.
    """

    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        backend = DeepSeekModel.create_deepseek_model()
        self.agent = ChatAgent(
            system_message=self.system_prompt,
            model=backend
        )

    def step(self, content: str):
        resp = self.agent.step(content)
        return resp.msg

    def calculate_commute(self, origin: Coordinates, destination: Coordinates) -> CommuteInfo:
        """
        Use the agent to calculate travel time and distance.
        """
        payload = {
            "origin": {"latitude": origin.latitude, "longitude": origin.longitude},
            "destination": {"latitude": destination.latitude, "longitude": destination.longitude}
        }
        resp = self.step(json.dumps(payload))
        text = resp.content.strip()

        try:
            obj = json.loads(text)
        except json.JSONDecodeError:
            obj = json.loads(self._extract_json(text))

        return CommuteInfo(**obj)

    def _extract_json(self, text: str) -> str:
        start = text.find('{')
        end = text.rfind('}') + 1
        if start < 0 or end <= start:
            logging.error("No JSON object found in agent output.")
            raise ValueError("Agent output did not contain valid JSON.")
        return text[start:end]

