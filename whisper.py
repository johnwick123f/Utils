import requests
import os
import time

def transcribe(audio_file_path=None, url="http://localhost:2500/v1/audio/transcriptions"):
    time1 = time.time()
    data = {'model': 'distil-whisper/distil-small.en','response_format': 'json'}
    with open(audio_file_path, 'rb') as audio_file:
        files = {
            'file': (os.path.basename(audio_file_path), audio_file, 'audio/wav')
        }

        response = requests.post(url, files=files, data=data)

        # 6. Check for a successful response
        response.raise_for_status()  # This will raise an HTTPError for bad responses (4xx or 5xx)

        transcription = response.json()
        print(f"Transcription: {transcription['text']}")
        print(f"Time took for transcription: {time.time() - time1}")
        return transcription['text']
