# Orpheus-TTS-Local

A lightweight client for running [Orpheus TTS](https://huggingface.co/canopylabs/orpheus-3b-0.1-ft) locally using LM Studio API.

## Features

- 🎧 High-quality Text-to-Speech using the Orpheus TTS model
- 💻 Completely local - no cloud API keys needed
- 🔊 Multiple voice options (tara, leah, jess, leo, dan, mia, zac, zoe)
- 💾 Save audio to WAV files
- 🌐 Web interface for easy text-to-speech generation

## Quick Setup

1. Install [LM Studio](https://lmstudio.ai/) 
2. Download the [Orpheus TTS model (orpheus-3b-0.1-ft-q4_k_m.gguf)](https://huggingface.co/isaiahbjork/orpheus-3b-0.1-ft-Q4_K_M-GGUF) in LM Studio
3. Load the Orpheus model in LM Studio
4. Start the local server in LM Studio (default: http://127.0.0.1:1234)
5. Install dependencies:
   ```
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
6. Run the script:
   ```
   python gguf_orpheus.py --text "Hello, this is a test" --voice tara
   ```

## Web Interface

A web interface is available for easier interaction with the Orpheus TTS model:

1. Make sure LM Studio is running with the Orpheus model loaded
2. Start the web server:
   ```
   python server.py
   ```
3. Open your browser and navigate to http://localhost:5001 (or the port shown in the terminal)
4. Select a voice, enter your text, and click "Generate Speech"

The web interface allows you to:
- Select from all available voices
- Enter text to convert to speech
- Stream the generated audio directly in your browser

### Troubleshooting

If you encounter issues with the web interface:

1. Make sure LM Studio is running with the Orpheus model loaded
2. Check that the server is running and note the port number shown in the terminal
3. If you see "Address already in use" errors, the server will automatically try the next available port
4. The client will automatically try to connect to ports 5001-5005 to find the server
5. Run the test script to diagnose common issues:
   ```
   python test_server.py
   ```

## Usage

```
python gguf_orpheus.py --text "Your text here" --voice tara --output "output.wav"
```

### Options

- `--text`: The text to convert to speech
- `--voice`: The voice to use (default: tara)
- `--output`: Output WAV file path (default: auto-generated filename)
- `--list-voices`: Show available voices
- `--temperature`: Temperature for generation (default: 0.6)
- `--top_p`: Top-p sampling parameter (default: 0.9)
- `--repetition_penalty`: Repetition penalty (default: 1.1)

## Available Voices

- tara - Best overall voice for general use (default)
- leah
- jess
- leo
- dan
- mia
- zac
- zoe

## Emotion
You can add emotion to the speech by adding the following tags:
```xml
<giggle>
<laugh>
<chuckle>
<sigh>
<cough>
<sniffle>
<groan>
<yawn>
<gasp>
```

## License

Apache 2.0
