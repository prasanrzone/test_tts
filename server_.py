import sounddevice as sd
import numpy as np
import whisper
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import asyncio
import time

app = FastAPI()

micTimeout = 600
chunk_duration = 15  # Duration of each chunk in seconds
samplerate = 22050

# Load the model once when the server starts
model = whisper.load_model("small.en")

def record_audio_chunk(duration, samplerate=22050):
    print("Recording...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float32')
    sd.wait()
    print("Recording complete")
    return audio

def recognize_from_whisper(audio_chunk, samplerate=22050):
    # Ensure audio_chunk is in the correct format (float32 or float64 numpy array)
    audio_chunk = audio_chunk.flatten()  # Flatten the array if needed
    audio_chunk = audio_chunk.astype(np.float32)  # Ensure float32 format
    
    # Use Whisper to transcribe the audio
    result = model.transcribe(audio_chunk)
    return result["text"]

@app.get("/")
async def get():
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>WebSocket</title>
        </head>
        <body>
            <h1>WebSocket Voice Recognition</h1>
            <button onclick="startRecording()">Start Recording</button>
            <div id="transcription"></div>
            <script>
                var ws = new WebSocket("ws://localhost:8000/ws");
                
                ws.onmessage = function(event) {
                    var messages = document.getElementById('transcription');
                    var message = document.createElement('div');
                    message.textContent = event.data;
                    messages.appendChild(message);
                };

                function startRecording() {
                    ws.send('start');
                }
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            if data == "start":
                end_time = time.time() + micTimeout
                while time.time() < end_time:
                    audio_chunk = record_audio_chunk(chunk_duration, samplerate)
                    text = recognize_from_whisper(audio_chunk)
                    await websocket.send_text(text)
                    await asyncio.sleep(0) 
    except Exception as e:
        print(f"WebSocket disconnected: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
