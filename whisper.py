import subprocess
import time
import atexit
import requests
import os
import aiohttp
class WhisperModel:
    """
    A simple class to start and manage a vLLM server process.
    """
    def __init__(self, model_name="distil-whisper/distil-small.en", memory_util="0.2"):
        # Start the vLLM server process
        self.model_name = model_name
        print("INFO: LOADING WHISPER MODEL USING VLLM!")
        
    async def transcribe(self, audio_file_path=None, url="http://localhost:2500/v1/audio/transcriptions"):
        """
        Transcribes an audio file by making an asynchronous request to the vLLM server.
        """
        time1 = time.time()        
        # Prepare the form data for the aiohttp request
        data = aiohttp.FormData()
        data.add_field('model', self.model_name)
        data.add_field('response_format', 'json')
        
        with open(audio_file_path, 'rb') as audio_file:
            data.add_field(
                'file',
                audio_file,
                filename=os.path.basename(audio_file_path),
                content_type='audio/wav'
            )

            # Use an aiohttp ClientSession for the asynchronous request
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data) as response:
                    # Check for a successful response (200-299 status code)
                    response.raise_for_status()
                    
                    # Await the JSON response, as this is an async operation
                    transcription = await response.json()
                    
                    print(f"Transcription: {transcription['text']}")
                    print(f"Time took for transcription: {time.time() - time1}")
                    
                    return transcription['text']
