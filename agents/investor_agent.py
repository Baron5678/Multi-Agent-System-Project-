import json
import logging
from typing import List
from camel.agents import ChatAgent
from services.deepseek_api import DeepSeekModel
from core.data_models import InvestorProfile, UserPreferences


class InvestorAgent:
    """
    Fetches and filters investor profiles based on user preferences.
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

    def get_investors(self, prefs: UserPreferences) -> List[InvestorProfile]:
        """
        Run the agent with preferences JSON and return a list of InvestorProfile.
        """
        payload = prefs.model_dump_json()
        resp = self.step(payload)
        text = resp.content.strip()

        try:
            arr = json.loads(text)
        except json.JSONDecodeError:
            arr = json.loads(self._extract_json(text))

        investors: List[InvestorProfile] = []
        for item in arr:
            try:
                investors.append(InvestorProfile(**item))
            except Exception as e:
                logging.error(f"Failed to parse InvestorProfile: {e}")
        return investors

    def _extract_json(self, text: str) -> str:
        """
        Pull out the first [...] JSON array in the text.
        """
        start = text.find('[')
        end = text.rfind(']') + 1
        if start < 0 or end <= start:
            logging.error("No JSON array found in agent output.")
            raise ValueError("Agent output did not contain valid JSON array.")
        return text[start:end]