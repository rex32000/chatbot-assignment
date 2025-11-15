import os
from typing import Dict, List
from google import genai
from google.genai import types
from pydantic import BaseModel

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

KNOWLEDGE_BASE = """
Use this knowledge base to answer questions:

Product: A booking simulator for a restaurant.

Features:
- The user can book a table for a specific number of people at a specific time.
- The user can cancel a booking.
- The user can view the booking details.
- The user can view the table details.

Rules:
- Confirm the booking details with the user before confirming the booking.
- If the user cancels the booking, confirm the cancellation with the user before cancelling the booking.
- If the user views/lists the booking details, show the booking details to the user as per session id.
- Perform validatory checks and give appropriate answers if the data is not available, say that you are not sure about the answer.
- If user asks questions apart from the ones in the knowledge base, say that you are not sure about the answer and ask the user to stick to the knowledge base politely.
- The restaurant is open from 10:00 AM to 10:00 PM.

Additional knowledge:
- The restaurant is located in the heart of the city Ahmedabad.
- Ahmedabad is in Gujarat, India.
- Weather in Ahmedabad is sunny and warm.
- Best snack in Ahmedabad is fafda.
- Best place to visit in Ahmedabad is the Sabarmati Ashram.
"""

CHAT_HISTORY: Dict[str, List[Dict]] = {}


class ChatRequest(BaseModel):
    session_id: str
    user_message: str


def generate_reply(history):

    # Format messages for Gemini API
    contents = []
    for h in history:
        contents.append({
            "role": h["role"],
            "parts": [{"text": h["text"]}]
        })

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=KNOWLEDGE_BASE
        )
    )

    return response.text
