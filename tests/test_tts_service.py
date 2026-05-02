import pytest
from unittest.mock import patch, MagicMock
from utils.tts_service import generate_speech
import os

@patch('utils.tts_service.texttospeech.TextToSpeechClient')
def test_generate_speech_success(mock_client_class):
    """Test successful audio generation."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    
    # Simulate realistic mp3 payload size
    mock_response.audio_content = b"fake_audio_bytes" * 100 
    mock_client.synthesize_speech.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    audio = generate_speech("Hello, world!", "USA")
    
    assert audio == mock_response.audio_content
    assert mock_client.synthesize_speech.called

@patch('utils.tts_service.texttospeech.TextToSpeechClient')
def test_generate_speech_failure(mock_client_class):
    """Test that failure returns None instead of crashing."""
    mock_client = MagicMock()
    mock_client.synthesize_speech.side_effect = Exception("TTS API Failed")
    mock_client_class.return_value = mock_client
    
    audio = generate_speech("Test text", "USA")
    
    # Ensure it returns None for the UI to handle, no crash
    assert audio is None

def test_generate_speech_markdown_cleaning():
    """Verify markdown characters are cleaned to prevent TTS speaking symbols."""
    with patch('utils.tts_service.texttospeech.TextToSpeechClient') as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        test_input = "**Bold** and _Italic_ with # Header"
        generate_speech(test_input, "USA")
        
        # Verify the text passed to SynthesisInput was cleaned
        call_kwargs = mock_client.synthesize_speech.call_args.kwargs
        synthesis_input = call_kwargs['input']
        
        assert synthesis_input.text == "Bold and Italic with Header" # Markers removed
