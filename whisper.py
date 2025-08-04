import subprocess
import time
import atexit
import requests
import os

class WhisperModel:
    """
    A simple class to start and manage a vLLM server process.
    """
    def __init__(self, model_name="distil-whisper/distil-small.en", memory_util="0.2"):
        # Start the vLLM server process
        self.model_name = model_name
        self.process = subprocess.Popen(
            ["vllm", "serve", model_name, "--task", "transcription",
             "--host", "0.0.0.0", "--port", "2500", "--gpu-memory-utilization", memory_util],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False
        )

        #atexit.register(self.shutdown)

    def shutdown(self):
        """
        Manually shuts down the vLLM server process.
        This method must be called explicitly to stop the server.
        """
        if self.process and self.process.poll() is None:
            print("Shutting down vLLM server...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            print("vLLM server has been shut down.")
        
    async def transcribe(self, audio_file_path=None, url="http://localhost:2500/v1/audio/transcriptions"):
        time1 = time.time()
        data = {'model': self.model_name, 'response_format': 'json'}
        with open(audio_file_path, 'rb') as audio_file:
            files = {
                'file': (os.path.basename(audio_file_path), audio_file, 'audio/wav')
            }

            response = requests.post(url, files=files, data=data)

            response.raise_for_status()  # This will raise an HTTPError for bad responses (4xx or 5xx)

            transcription = response.json()
            print(f"Transcription: {transcription['text']}")
            print(f"Time took for transcription: {time.time() - time1}")
            return transcription['text']
