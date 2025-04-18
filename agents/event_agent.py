import json
import logging
from typing import List
from camel.agents import ChatAgent
from services.deepseek_api import DeepSeekModel
from core.data_models import Event, UserPreferences


class EventAgent:
    """
    Fetches and filters event data based on user preferences.
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

    def get_events(self, prefs: UserPreferences) -> List[Event]:
        """
        Run the agent with preferences JSON and return a list of Event models.
        """
        payload = prefs.model_dump_json()
        resp = self.step(payload)
        text = resp.content.strip()

        try:
            arr = json.loads(text)
        except json.JSONDecodeError:
            arr = json.loads(self._extract_json(text))

        events: List[Event] = []
        for item in arr:
            try:
                events.append(Event(**item))
            except Exception as e:
                logging.error(f"Failed to parse Event: {e}")
        return events

    def _extract_json(self, text: str) -> str:
        start = text.find('[')
        end = text.rfind(']') + 1
        if start < 0 or end <= start:
            logging.error("No JSON array found in agent output.")
            raise ValueError("Agent output did not contain valid JSON array.")
        return text[start:end]