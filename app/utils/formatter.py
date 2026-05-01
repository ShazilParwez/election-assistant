def format_response(content: str) -> str:
    """
    Ensures the response is cleanly formatted.
    In a real system, this might convert markdown to specific JSON structures,
    or ensure required sections are present.
    """
    if not content:
        return ""
        
    # Strip leading/trailing whitespace
    content = content.strip()
    
    # Ensure standard line endings
    content = content.replace("\r\n", "\n")
    
    return content
