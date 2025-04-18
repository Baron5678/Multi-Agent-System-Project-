import json
import logging
from camel.agents import ChatAgent
from services.deepseek_api import DeepSeekModel
from core.data_models import Coordinates


class GeolocationAgent:
    """
    Converts human-readable addresses to Coordinates.
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

    def get_coordinates(self, address: str) -> Coordinates:
        """
        Convert an address string into a Coordinates model.
        """
        resp = self.step(address)
        text = resp.content.strip()

        try:
            obj = json.loads(text)
        except json.JSONDecodeError:
            obj = json.loads(self._extract_json(text))

        return Coordinates(**obj)

    def _extract_json(self, text: str) -> str:
        start = text.find('{')
        end = text.rfind('}') + 1
        if start < 0 or end <= start:
            logging.error("No JSON object found in agent output.")
            raise ValueError("Agent output did not contain valid JSON.")
        return text[start:end]