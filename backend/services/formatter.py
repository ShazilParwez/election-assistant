import logging
from typing import Dict

logger = logging.getLogger(__name__)


def parse_and_format_response(raw_text: str) -> Dict[str, str]:
    """
    Parses raw AI text into strictly required formatted blocks.

    Args:
        raw_text (str): The raw response text from the LLM.

    Returns:
        Dict[str, str]: A dictionary containing title, summary, and detailed sections.
    """
    if not raw_text or not raw_text.strip():
        logger.warning("Empty raw_text provided to formatter.")
        return {
            "title": "Election Insight",
            "summary": "No information returned.",
            "detailed": "The server did not return any valid information.",
        }

    lines = raw_text.split("\n")
    title = "Election Insight"

    if lines and lines[0].strip().startswith("#"):
        title = lines[0].replace("#", "").strip()
        lines = lines[1:]

    content = "\n".join(lines).strip()

    # Split into a short summary and detailed body for progressive disclosure
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

    if paragraphs:
        summary = paragraphs[0]
        # Ensure summary is strictly a short 2-3 lines fallback
        if len(summary) > 300:
            summary = summary[:297] + "..."
        detailed = (
            "\n\n".join(paragraphs[1:])
            if len(paragraphs) > 1
            else "No further details available."
        )
    else:
        summary = "Overview of the requested topic."
        detailed = content

    logger.debug("Successfully formatted response text.")
    return {
        "title": title,
        "summary": summary,
        "detailed": detailed,
    }


def get_fallback_response() -> Dict[str, str]:
    """
    Returns a safe fallback response for when the API is unreachable.

    Returns:
        Dict[str, str]: Structured fallback content.
    """
    return {
        "title": "Basic Election Guide (Fallback Mode)",
        "summary": "The server is currently unavailable. "
        "Here is a quick guide to election basics.",
        "detailed": (
            "1. Registration: Ensure you are registered to vote.\n"
            "2. Identification: Check local ID requirements.\n"
            "3. Locations: Find your polling station in advance."
        ),
    }
