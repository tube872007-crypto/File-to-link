import telebot
import os

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

WORKER_URL = "https://your-worker-url"

@bot.message_handler(content_types=['document', 'video', 'audio', 'photo'])
def handle_file(message):
    if message.document:
        file_info = bot.get_file(message.document.file_id)
        file_name = message.document.file_name
        file_size = message.document.file_size
    elif message.video:
        file_info = bot.get_file(message.video.file_id)
        file_name = "video.mp4"
        file_size = message.video.file_size
    elif message.audio:
        file_info = bot.get_file(message.audio.file_id)
        file_name = "audio.mp3"
        file_size = message.audio.file_size
    else:
        photo = message.photo[-1]
        file_info = bot.get_file(photo.file_id)
        file_name = "photo.jpg"
        file_size = photo.file_size

    file_size_mb = file_size / (1024 * 1024)

    download_url = f"{WORKER_URL}/dl/{file_info.file_path}"
    stream_url = f"{WORKER_URL}/stream/{file_info.file_path}"

    bot.reply_to(message, f"""
✅ Links Generated Successfully!

📁 File: {file_name}
📊 Size: {file_size_mb:.2f} MB

⬇️ Download:
{download_url}

🎬 Stream:
{stream_url}
""")

bot.infinity_polling()
