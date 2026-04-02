import os
from pyrogram import Client
from fastapi import FastAPI, Request
import uvicorn

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not API_ID or not API_HASH:
    raise RuntimeError("Missing API_ID or API_HASH")

app = FastAPI()

client = Client(
    "userbot_session",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_event("startup")
async def startup():
    await client.start()

@app.on_event("shutdown")
async def shutdown():
    await client.stop()

@app.post("/")
async def process(req: Request):
    data = await req.json()

    file_id = data["file_id"]
    chat_id = data["chat_id"]
    file_name = data["file_name"]

    try:
        # Download large file (NO LIMIT)
        file_path = await client.download_media(file_id, file_name)

        # Send back to user (or upload to cloud here)
        await client.send_document(chat_id, file_path)

        return {"status": "success"}

    except Exception as e:
        await client.send_message(chat_id, f"❌ Error: {str(e)}")
        return {"status": "error"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
