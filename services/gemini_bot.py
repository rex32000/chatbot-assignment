import os
from typing import Dict, List
from google import genai
from google.genai import types
from pydantic import BaseModel
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# Use langchain's built-in HuggingFace embeddings (free, local)
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

KB_TEXT = """
Use this knowledge base to answer questions:

Product: A booking simulator for a restaurant.

Features:
- The user can book a table for a specific number of people at a specific time.
- The user can cancel a booking.

Rules:
- Confirm the booking details with the user before confirming the booking.
- If the user cancels the booking, confirm the cancellation with the user before cancelling the booking.
- Perform validatory checks and give appropriate answers if the data is not available, say that you are not sure about the answer.
- If user asks about the booking details, check it from the message history and give the answer if it is available else say that you are not sure about the answer.
- If user asks questions apart from the ones in the knowledge base, say that you are not sure about the answer and ask the user to stick to the knowledge base politely.
- The restaurant is open from 10:00 AM to 10:00 PM.

Additional knowledge:
- The restaurant is located in the heart of the city Ahmedabad.
- Ahmedabad is in Gujarat, India.
- Weather in Ahmedabad is sunny and warm.
- Best snack in Ahmedabad is fafda.
- Best place to visit in Ahmedabad is the Sabarmati Ashram.
"""


splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
docs = splitter.split_text(KB_TEXT)

vector_store = FAISS.from_texts(docs, embedding_model)
print("FAISS vector store initialized")

GUARDRAIL_INSTRUCTION = """
You are a content safety guardrail. Check if a user message is:
1. Safe and appropriate (no harmful, illegal, or inappropriate content)
2. Relevant to restaurant bookings or information about Ahmedabad

Respond with ONLY one word: "APPROVED" or "REJECTED"
"""

def check_with_guardrail(user_message):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[{"role": "user", "parts": [{"text": user_message}]}],
            config=types.GenerateContentConfig(system_instruction=GUARDRAIL_INSTRUCTION)
        )
        return response.text.strip().upper() == "APPROVED"
    except Exception as e:
        print(f"Warning: Guardrail check failed: {str(e)}")
        return True

CHAT_HISTORY: Dict[str, List[Dict]] = {}

class ChatRequest(BaseModel):
    session_id: str
    user_message: str


def retrieve_relevant_docs(query, k=3):
    results = vector_store.similarity_search(query, k=k)
    return "\n".join([r.page_content for r in results])


def generate_reply(user_query, history):    
    if not check_with_guardrail(user_query):
        return "I'm sorry, I cannot process that request. Please ask about restaurant bookings or information about Ahmedabad."
    
    context = retrieve_relevant_docs(user_query)
    
    system_instruction = f"You are a helpful assistant for a restaurant booking system.\n\nUse the following context:\n{context}"
    
    contents = []
    for turn in history:
        contents.append({
            "role": turn["role"],
            "parts": [{"text": turn["text"]}]
        })
    
    contents.append({
        "role": "user",
        "parts": [{"text": user_query}]
    })
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=contents,
        config=types.GenerateContentConfig(system_instruction=system_instruction)
    )
    
    return response.text
