from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from services.gemini_bot import generate_reply, ChatRequest, CHAT_HISTORY

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(req: ChatRequest):
    try:
        session = req.session_id
        user_message = req.user_message

        if not session or not user_message:
            raise HTTPException(status_code=400, detail={
                "status": "error",
                "detail": "Session ID and user message are required",
                "error_code": "INVALID_REQUEST"
            })

        if session not in CHAT_HISTORY:
            CHAT_HISTORY[session] = []

        CHAT_HISTORY[session].append({
            "role": "user",
            "text": user_message
        })

        reply = generate_reply(user_message, CHAT_HISTORY[session])

        CHAT_HISTORY[session].append({
            "role": "model",
            "text": reply
        })

        return {
            "status": "success",
            "reply": reply
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "detail": str(e)
        })
