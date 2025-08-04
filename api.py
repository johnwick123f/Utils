import asyncio
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
import uvicorn
import threading
from fastapi.middleware.cors import CORSMiddleware
import uuid
import base64
from fastrtc import ReplyOnPause, Stream
from pyngrok import ngrok
try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    print("nest_asyncio not found. If you encounter event loop issues, consider installing it.")

# This is a dummy tts object since the original code did not provide an initialization.
class DummyTTS:
    audio_file = None
tts = DummyTTS()
args = None

def refine_text(text):
    text = text.replace("'", ",")
    text = text.replace("Im", "I,m")
    text = text.replace("-", ",")
    text = text.replace("what,s", "whats")
    text = text.replace("What,s", "Whats")
    text = text.replace("you,re", "youre")
    text = text.replace("I,d", "I'd")
    text = text.replace("you,d", "youd")
    return text

@asynccontextmanager
async def lifespan(app: FastAPI):
    global tts, args
    ## current does basically nothing, might need it in the future however
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/settings")
async def stream_audio(request: Request):
    """
    Streams raw audio bytes generated from the input prompt.
    """
    data = await request.json()
    voice_cloning_base64 = data['voice_cloning_file']
    voice_cloning_bytes = base64.b64decode(voice_cloning_base64)
    random_filename = f"{uuid.uuid4()}.wav"
    with open(random_filename, "wb") as f:
        f.write(voice_cloning_bytes)
    tts.audio_file = random_filename

# This is a dummy response function, as the original code did not provide one.
def response(text):
    print(f"Processing text: {text}")

def run_uvicorn(app, host, port):
    uvicorn.run(app, host=host, port=port, log_level="info")

def run_uvicorn_in_thread(app, host, port):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)

    loop.run_until_complete(server.serve())

def run_api(response_function=None, app=None, port=2200):
    # Use the dummy response function if none is provided.
    if response_function is None:
        response_function = response
    
    stream = Stream(
        handler=ReplyOnPause(response_function, can_interrupt=True),
        modality="audio",
        mode="send-receive"
    )
    stream.mount(app)
    uvicorn_thread = threading.Thread(target=run_uvicorn_in_thread, args=(app, "0.0.0.0", port))
    uvicorn_thread.daemon = True
    uvicorn_thread.start()
    ngrok.set_auth_token("2zpLPx35PmIlUiWYi0csyvtowok_4dMxCAz5U3nJ6mntbNrik")
    public_url = ngrok.connect(port)
    print(f"NGROK URL: {public_url}")
