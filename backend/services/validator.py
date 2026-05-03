import logging
import re
from typing import List, Tuple

logger = logging.getLogger(__name__)


class QueryValidator:
    """
    Validator service to ensure user queries are safe and relevant.
    """

    ELECTION_KEYWORDS: List[str] = [
        "election",
        "vote",
        "voting",
        "candidate",
        "ballot",
        "poll",
        "democracy",
        "campaign",
        "registration",
        "voter",
        "president",
        "prime minister",
        "parliament",
        "congress",
        "senate",
        "mayor",
        "electoral",
        "nomination",
        "counting",
        "civic",
    ]

    DANGEROUS_PATTERNS: List[str] = [
        r"ignore previous instructions",
        r"system prompt",
        r"bypass rules",
        r"act as",
        r"you are now",
        r"exec",
        r"eval",
    ]

    @classmethod
    def is_safe(cls, query: str) -> Tuple[bool, str]:
        """
        Validates if the query is safe from prompt injection and relevant to elections.

        Args:
            query (str): The user input text to validate.

        Returns:
            Tuple[bool, str]: (True, "") if safe, (False, "reason") otherwise.
        """
        query_lower = query.lower()

        # 1. Check for dangerous patterns (Basic Prompt Injection Protection)
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, query_lower):
                logger.warning(f"Dangerous pattern detected: {pattern}")
                return False, "Query blocked for security reasons."

        # 2. Check for relevance (Must contain at least one election keyword)
        is_relevant = any(keyword in query_lower for keyword in cls.ELECTION_KEYWORDS)

        if not is_relevant:
            logger.info("Query rejected: Not election-related.")
            return (
                False,
                "I can help only with election-related topics. "
                "Please ask about election processes, voting, or timelines.",
            )

        logger.debug("Query validation passed.")
        return True, ""
