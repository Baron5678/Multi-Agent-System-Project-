import json

import logging

from camel.agents import ChatAgent

from services.deepseek_api import DeepSeekModel

from core.data_models import UserPreferences


class UserAgent:
    """

    Extracts and structures founder preferences.

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

    def get_preferences(self, user_input: str) -> UserPreferences:

        """

        Run the agent on raw founder input and return validated UserPreferences.

        Assumes the agent outputs a single JSON object.

        """

        resp = self.step(user_input)

        text = resp.content.strip()

        try:

            data = json.loads(text)

        except json.JSONDecodeError:

            data = json.loads(self._extract_json(text))

        return UserPreferences(**data)

    def _extract_json(self, text: str) -> str:

        """

        Pull out the first {...} JSON object in the text.

        """

        start = text.find('{')

        end = text.rfind('}') + 1

        if start < 0 or end <= start:
            logging.error("No JSON object found in agent output.")

            raise ValueError("Agent output did not contain valid JSON.")

        return text[start:end]

