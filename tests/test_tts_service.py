from unittest.mock import MagicMock, patch

from frontend.utils.tts_service import generate_speech


@patch("frontend.utils.tts_service.texttospeech.TextToSpeechClient")
def test_generate_speech_success(mock_client_class: MagicMock) -> None:
    """
    Test successful audio generation.
    """
    mock_client = MagicMock()
    mock_response = MagicMock()

    # Simulate realistic mp3 payload size
    mock_response.audio_content = b"fake_audio_bytes" * 100
    mock_client.synthesize_speech.return_value = mock_response
    mock_client_class.return_value = mock_client

    audio = generate_speech("Hello, world!", "USA")

    assert audio == mock_response.audio_content
    assert mock_client.synthesize_speech.called


@patch("frontend.utils.tts_service.texttospeech.TextToSpeechClient")
def test_generate_speech_failure(mock_client_class: MagicMock) -> None:
    """
    Test that failure returns None instead of crashing.
    """
    mock_client = MagicMock()
    mock_client.synthesize_speech.side_effect = Exception("TTS API Failed")
    mock_client_class.return_value = mock_client

    audio = generate_speech("Test text", "USA")

    # Ensure it returns None for the UI to handle, no crash
    assert audio is None


def test_generate_speech_markdown_cleaning() -> None:
    """
    Verify markdown characters are cleaned to prevent TTS speaking symbols.
    """
    with patch(
        "frontend.utils.tts_service.texttospeech.TextToSpeechClient"
    ) as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        test_input = "**Bold** and _Italic_ with # Header"
        generate_speech(test_input, "USA")

        # Verify the text passed to SynthesisInput was cleaned
        call_kwargs = mock_client.synthesize_speech.call_args.kwargs
        synthesis_input = call_kwargs["input"]

        assert synthesis_input.text == "Bold and Italic with Header"  # Markers removed


@patch("frontend.utils.tts_service.texttospeech.TextToSpeechClient")
def test_get_tts_client_adc_failure(mock_client_class: MagicMock) -> None:
    """Test that it clears dummy path and falls back if ADC fails."""
    import os
    with patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": r"C:\full\path\to\key.json"}):
        mock_client_class.side_effect = [Exception("ADC fail"), MagicMock()]
        with patch("os.path.exists", return_value=True):
            with patch("frontend.utils.tts_service.texttospeech.TextToSpeechClient.from_service_account_file") as mock_from_file:
                from frontend.utils.tts_service import _get_tts_client
                _get_tts_client()
                assert "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ
                mock_from_file.assert_called_once()


@patch("frontend.utils.tts_service.texttospeech.TextToSpeechClient")
def test_get_tts_client_total_failure(mock_client_class: MagicMock) -> None:
    """Test when both ADC and local file fail."""
    mock_client_class.side_effect = Exception("ADC fail")
    with patch("os.path.exists", return_value=False):
        from frontend.utils.tts_service import _get_tts_client
        client = _get_tts_client()
        assert client is None


@patch("frontend.utils.tts_service._get_tts_client")
def test_generate_speech_no_client(mock_get_client: MagicMock) -> None:
    """Test generate_speech when client cannot be initialized."""
    mock_get_client.return_value = None
    assert generate_speech("test", "USA") is None
