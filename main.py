import os
import uuid
import cloudinary
import cloudinary.uploader
from fastapi import FastAPI, Request
import telebot

# ================= CONFIG =================
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET")
)

bot = telebot.TeleBot(TOKEN)
app = FastAPI()

if not WEBHOOK_URL:
    raise RuntimeError("WEBHOOK_URL not set")

# ================= WEBHOOK =================
@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    update = telebot.types.Update.de_json(data)
    bot.process_new_updates([update])
    return {"ok": True}

# ================= FILE UPLOAD =================
def upload_to_cloud(file_bytes, filename):
    try:
        result = cloudinary.uploader.upload(
            file_bytes,
            resource_type="auto",
            public_id=str(uuid.uuid4())
        )
        return result["secure_url"]
    except Exception as e:
        return None

# ================= HANDLE FILE =================
def handle_file(message, file_id, filename="file"):
    try:
        file_info = bot.get_file(file_id)
        file_data = bot.download_file(file_info.file_path)

        link = upload_to_cloud(file_data, filename)

        if link:
            bot.reply_to(
                message,
                f"✅ File uploaded successfully!\n\n🔗 Download Link:\n{link}"
            )
        else:
            bot.reply_to(message, "❌ Upload failed. Try again.")

    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {str(e)}")

# ================= HANDLERS =================
@bot.message_handler(content_types=['document'])
def doc_handler(message):
    handle_file(message, message.document.file_id, message.document.file_name)

@bot.message_handler(content_types=['photo'])
def photo_handler(message):
    file_id = message.photo[-1].file_id
    handle_file(message, file_id, "photo.jpg")

@bot.message_handler(content_types=['video'])
def video_handler(message):
    handle_file(message, message.video.file_id, "video.mp4")

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(
        msg,
        "🚀 Send any file to get a permanent download link!\n\n"
        "☁️ Powered by Cloud Storage"
    )

# ================= STARTUP =================
@app.on_event("startup")
def setup():
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
