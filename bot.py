import os
import telebot
import requests

TOKEN = os.getenv("BOT_TOKEN")
USERBOT_URL = os.getenv("USERBOT_URL")

if not TOKEN or not USERBOT_URL:
    raise RuntimeError("Missing BOT_TOKEN or USERBOT_URL")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "🚀 Send any file (even 2GB+) to get a link!")

@bot.message_handler(content_types=['document', 'video', 'photo'])
def handle_file(message):
    file_id = None
    file_name = "file"

    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
    elif message.video:
        file_id = message.video.file_id
        file_name = "video.mp4"
    elif message.photo:
        file_id = message.photo[-1].file_id
        file_name = "photo.jpg"

    bot.reply_to(message, "⏳ Processing... Please wait")

    try:
        requests.post(USERBOT_URL, json={
            "file_id": file_id,
            "chat_id": message.chat.id,
            "file_name": file_name
        }, timeout=10)
    except:
        bot.reply_to(message, "❌ Failed to connect to server")

bot.infinity_polling()
