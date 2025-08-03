import requests
import os
import time
import os
import asyncio
import time
from typing import List, Dict, Any
from cerebras.cloud.sdk import AsyncCerebras # Correctly importing the async client

class GroqLLM:
    """
    An asynchronous client for a text generation model using the AsyncCerebras SDK.
    """
    def __init__(self):
        api_key = os.getenv("CEREBRAS_API_KEY", "your-api-key-here")
        if not api_key:
            raise ValueError("CEREBRAS_API_KEY environment variable not set.")
        api_key = "csk-5j55r4yext62d4pvvdwpt533tmepd29638dkn9y5hxy64fjf"

        self.client = AsyncCerebras(api_key=api_key)
        self.chat_history: List[Dict[str, str]] = []
        print("Llama4Scout model initialized with AsyncCerebras client.")

    async def generate_text(self, prompt: str, system_message: str = None, reset: str = "True") -> str:
        """
        Asynchronously generates text based on a given prompt and chat history
        by awaiting the non-blocking API call.
        """
        system_message_content = system_message or (
            "Speak concisely in 3 sentences. Be entertaining but fun. Only speak strictly in english language no matter what. "
            "Use proper grammar and use words like um, haha, oh, uh, uhm, ooh often. Do not use special characters except punctuation."
        )

        if reset == "True":
            self.chat_history = []
            print("Chat history reset.")

        messages: List[Dict[str, str]] = []
        
        if system_message_content:
            messages.append({"role": "system", "content": system_message_content})

        messages.append({"role": "user", "content": prompt})

        self.chat_history.extend(messages)
        time1 = time.time()

        try:
            response = await self.client.chat.completions.create(
                messages=self.chat_history,
                model="llama-4-scout-17b-16e-instruct",
            )

            if response.choices and response.choices[0].message and response.choices[0].message.content:
                generated_content = response.choices[0].message.content
                self.chat_history.append({"role": "assistant", "content": generated_content})
                print(f"Latency for llm inference: {time.time() - time1:.2f} seconds")
                return generated_content
            else:
                return "No content generated from the model."
        except Exception as e:
            print(f"An error occurred during text generation: {e}")
            return f"Error: Could not generate text. {e}"
