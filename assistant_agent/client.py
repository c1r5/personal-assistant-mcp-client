from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai.types import UserContent
import logging


APP_NAME = "Personal Assistant"

logger = logging.getLogger(__name__)

class AssistantClient:
    def __init__(self, agent: Agent, user_id: str):
        self.__runner = InMemoryRunner(app_name=APP_NAME, agent=agent)
        self.__user_id = user_id

    async def start_session(self):
        logger.info("Starting session")
        self.session = await self.__runner.session_service.create_session(app_name=APP_NAME, user_id=self.__user_id)

    async def stop_session(self):
        logger.info("Stopping session")
        await self.__runner.session_service.delete_session(app_name=APP_NAME, session_id=self.session.id, user_id=self.__user_id)

    async def request(self, message: str):
        try:
            logger.info("Requesting response")
            async for response in self.__runner.run_async(user_id=self.__user_id, session_id=self.session.id, new_message=UserContent(message)):
                if not response.is_final_response():
                    continue

                if response.content is None:
                    logger.warning("Não foi possivel gerar a resposta")
                    continue

                if response.content.parts is None or []: # type: ignore
                    logger.warning("Não foi possivel obter o conteudo da resposta")
                    yield "Não foi possivel obter o conteudo da resposta"
                    continue

                yield '\n'.join([part.text for part in response.content.parts])   # type: ignore
        except Exception as e:
            logger.error("Um erro ocorreu ao tentar gerar resposta", exc_info=e)
