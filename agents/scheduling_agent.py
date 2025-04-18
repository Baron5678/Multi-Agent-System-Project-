import json
import logging
from camel.agents import ChatAgent
from services.deepseek_api import DeepSeekModel
from core.data_models import SchedulingRequest, Schedule


class SchedulingAgent:
    """
    Builds and ranks a meeting schedule from all inputs.
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

    def build_schedule(self, req: SchedulingRequest) -> Schedule:
        """
        Run the agent with the full SchedulingRequest and return a Schedule.
        """
        payload = req.model_dump_json()
        resp = self.step(payload)
        text = resp.content.strip()

        try:
            obj = json.loads(text)
        except json.JSONDecodeError:
            obj = json.loads(self._extract_json(text))

        return Schedule(**obj)

    def _extract_json(self, text: str) -> str:
        start = text.find('{')
        end = text.rfind('}') + 1
        if start < 0 or end <= start:
            logging.error("No JSON object found in agent output.")
            raise ValueError("Agent output did not contain valid JSON.")
        return text[start:end]