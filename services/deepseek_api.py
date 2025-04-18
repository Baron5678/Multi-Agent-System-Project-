import logging
from config import API_KEY
from camel.models import ModelFactory, BaseModelBackend
from camel.types import ModelPlatformType


class DeepSeekModel:
    deepseek_model: BaseModelBackend = None

    @classmethod
    def create_deepseek_model(cls) -> BaseModelBackend:
        if not cls.deepseek_model:
            cls.deepseek_model = ModelFactory.create(
                model_platform=ModelPlatformType.DEEPSEEK,
                # Use the DeepSeek chat alias which maps to DeepSeek-V3
                model_type="deepseek-chat",
                model_config_dict={
                    "temperature": 0.5,
                    # Specify max_tokens to override the 4K default
                    "max_tokens": 1024
                },
                api_key=API_KEY
            )
        else:
            logging.warning("Model already initialized, returning existing instance")
        return cls.deepseek_model