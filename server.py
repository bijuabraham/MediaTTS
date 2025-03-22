import os
import sys
import time
import threading
import queue
import traceback
from flask import Flask, request, Response, send_file, render_template, jsonify
from flask_cors import CORS
import requests

# Import gguf_orpheus with error handling
try:
    import gguf_orpheus
    ORPHEUS_IMPORT_ERROR = None
except ImportError as e:
    ORPHEUS_IMPORT_ERROR = str(e)
    print(f"Error importing gguf_orpheus: {e}")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Check if LM Studio is running
def check_lm_studio():
    try:
        response = requests.get("http://127.0.0.1:1234/v1/models", timeout=2)
        return response.status_code == 200
    except:
        return False

@app.route('/')
def index():
    return send_file('client.html')

@app.route('/status', methods=['GET'])
def status():
    """Endpoint to check server status"""
    status_info = {
        "server": "running",
        "lm_studio": check_lm_studio(),
        "orpheus_import_error": ORPHEUS_IMPORT_ERROR
    }
    return jsonify(status_info)

@app.route('/tts', methods=['GET'])
def text_to_speech():
    # Check for import errors
    if ORPHEUS_IMPORT_ERROR:
        return f"Error: Could not import gguf_orpheus module: {ORPHEUS_IMPORT_ERROR}", 500
    
    # Check if LM Studio is running
    if not check_lm_studio():
        return "Error: LM Studio API is not running at http://127.0.0.1:1234", 503
    
    prompt = request.args.get('prompt', '')
    voice = request.args.get('voice', gguf_orpheus.DEFAULT_VOICE)
    
    if not prompt:
        return "No prompt provided", 400
    
    try:
        # Create a temporary file to store the audio
        import tempfile
        import wave
        import io
        
        # Generate a temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_path = temp_file.name
        
        print(f"Generating speech for: '{prompt}' using voice: {voice}")
        
        # Generate tokens from the API
        token_gen = gguf_orpheus.generate_tokens_from_api(
            prompt=prompt,
            voice=voice
        )
        
        if token_gen is None:
            return "Failed to generate tokens from LM Studio API", 500
        
        # Use the existing function to generate audio and save to file
        audio_segments = []
        segment_count = 0
        
        # Open a WAV file for writing
        with wave.open(temp_path, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(24000)  # 24kHz
            
            # Process tokens and convert to audio
            for segment in gguf_orpheus.tokens_decoder_sync(token_gen):
                if segment is not None:
                    # Ensure segment is bytes
                    if not isinstance(segment, bytes):
                        print(f"Warning: Segment is not bytes, type: {type(segment)}")
                        continue
                    
                    # Write segment to WAV file
                    wav_file.writeframes(segment)
                    segment_count += 1
        
        print(f"Generated {segment_count} audio segments")
        
        if segment_count == 0:
            # Clean up the temporary file
            os.unlink(temp_path)
            return "No audio segments were generated", 500
        
        # Return the WAV file
        return send_file(
            temp_path,
            mimetype='audio/wav',
            as_attachment=False,
            download_name='speech.wav',
            conditional=False
        )
        
    except Exception as e:
        error_msg = f"Error generating audio: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return error_msg, 500

if __name__ == '__main__':
    # Try different ports if the default is in use
    default_port = 5001  # Changed from 5000 to avoid conflict with AirPlay on macOS
    
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', default_port))
    max_port_attempts = 5
    
    # Print server status
    print(f"\n=== Orpheus TTS Web Server ===")
    
    if ORPHEUS_IMPORT_ERROR:
        print(f"WARNING: Error importing gguf_orpheus module: {ORPHEUS_IMPORT_ERROR}")
        print("The server will run but TTS functionality will not work.")
    
    if not check_lm_studio():
        print("WARNING: LM Studio API is not running at http://127.0.0.1:1234")
        print("Please start LM Studio and load the Orpheus model.")
    else:
        print("LM Studio API is running and ready.")
    
    # Try to start the server on different ports if needed
    for attempt in range(max_port_attempts):
        try:
            current_port = port + attempt
            print(f"Starting server on http://localhost:{current_port}")
            print("\nPress Ctrl+C to stop the server.")
            app.run(host='0.0.0.0', port=current_port, threaded=True)
            break  # If we get here, the server started successfully
        except OSError as e:
            if "Address already in use" in str(e) and attempt < max_port_attempts - 1:
                print(f"Port {current_port} is already in use, trying port {current_port + 1}...")
            else:
                raise  # Re-raise the exception if we've tried all ports or it's a different error
