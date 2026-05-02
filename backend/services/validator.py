import re

class QueryValidator:
    ELECTION_KEYWORDS = [
        "election", "vote", "voting", "candidate", "ballot", "poll",
        "democracy", "campaign", "registration", "voter", "president",
        "prime minister", "parliament", "congress", "senate", "mayor",
        "electoral", "nomination", "counting", "civic"
    ]

    DANGEROUS_PATTERNS = [
        r"ignore previous instructions",
        r"system prompt",
        r"bypass rules",
        r"act as",
        r"you are now",
        r"exec",
        r"eval"
    ]

    @classmethod
    def is_safe(cls, query: str) -> tuple[bool, str]:
        """
        Validates if the query is safe from prompt injection and relevant to elections.

        Args:
            query (str): The user input text to validate.

        Returns:
            tuple[bool, str]: A tuple containing a boolean (True if safe) and a string message.
        """
        query_lower = query.lower()

        # 1. Check for dangerous patterns (Basic Prompt Injection Protection)
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, query_lower):
                return False, "Query blocked for security reasons."

        # 2. Check for relevance (Must contain at least one election keyword)
        is_relevant = any(keyword in query_lower for keyword in cls.ELECTION_KEYWORDS)
        
        if not is_relevant:
            return False, "I can help only with election-related topics. Please ask about election processes, voting, or timelines."

        return True, ""
