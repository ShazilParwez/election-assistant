import streamlit as st

def get_base_styles(font_size: int) -> str:
    """
    Generates the base CSS styles for the application.
    
    Args:
        font_size (int): The user-defined font size.
        
    Returns:
        str: HTML string containing the <style> block.
    """
    return f"""
    <style>
    :root {{
        font-size: {font_size}px;
    }}
    body, .stApp {{
        background-color: #0E1117;
        color: #FAFAFA;
        font-size: {font_size}px !important;
    }}
    /* Accessibility: Focus Styles */
    button:focus, input:focus, [role="button"]:focus {{
        outline: 3px solid #00FFCC !important;
        outline-offset: 2px;
    }}
    </style>
    """

def get_high_contrast_styles() -> str:
    """
    Generates high-contrast CSS overrides for improved accessibility.
    
    Returns:
        str: HTML string containing the <style> block.
    """
    return """
    <style>
    body, .stApp {
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }
    .stMarkdown, p, span, div, h1, h2, h3, h4, h5, h6, label {
        color: #FFFFFF !important;
    }
    .stButton>button {
        background-color: #000000 !important;
        color: #FFFF00 !important;
        border: 2px solid #FFFF00 !important;
    }
    /* Ensure high contrast focus remains visible */
    button:focus, input:focus {
        outline: 3px solid #FFFF00 !important;
        outline-offset: 4px;
    }
    </style>
    """
