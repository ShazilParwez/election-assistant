import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class LLMInterface(ABC):
    """
    Abstract Base Class defining the contract for Language Model services.
    """

    @abstractmethod
    def get_response(self, user_query: str) -> str:
        """
        Generate an AI response for a given user query.

        Args:
            user_query (str): The specific question or prompt provided by the user.

        Returns:
            str: The AI-generated response text.
        """
        pass
