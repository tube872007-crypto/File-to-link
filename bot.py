import telebot
import os

# 🔑 Get token from Railway
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN not set!")

bot = telebot.TeleBot(TOKEN)

# 🌐 Your Cloudflare Worker URL (REPLACE THIS)
WORKER_URL = "fille-to-link.tube872007.workers.dev"


# 👋 Start command
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "👋 Send me any file and I'll give you download & stream links 🚀"
    )


# 📁 Handle files
@bot.message_handler(content_types=['document', 'video', 'audio', 'photo', 'voice', 'video_note'])
def handle_file(message):
    try:
        # 📦 Detect file type
        if message.document:
            file_info = bot.get_file(message.document.file_id)
            file_name = message.document.file_name or "file"
            file_size = message.document.file_size

        elif message.video:
            file_info = bot.get_file(message.video.file_id)
            file_name = "video.mp4"
            file_size = message.video.file_size

        elif message.audio:
            file_info = bot.get_file(message.audio.file_id)
            file_name = message.audio.file_name or "audio.mp3"
            file_size = message.audio.file_size

        elif message.photo:
            photo = message.photo[-1]
            file_info = bot.get_file(photo.file_id)
            file_name = "photo.jpg"
            file_size = photo.file_size

        elif message.voice:
            file_info = bot.get_file(message.voice.file_id)
            file_name = "voice.ogg"
            file_size = message.voice.file_size

        else:
            file_info = bot.get_file(message.video_note.file_id)
            file_name = "video_note.mp4"
            file_size = message.video_note.file_size

        # 📏 Convert size
        file_size_mb = file_size / (1024 * 1024)

        # 🔗 Generate links using Worker
        download_url = f"{WORKER_URL}/dl/{file_info.file_path}"
        stream_url = f"{WORKER_URL}/stream/{file_info.file_path}"

        # 📩 Reply message
        response = (
            f"✅ Links Generated Successfully!\n\n"
            f"📁 File: {file_name}\n"
            f"📊 Size: {file_size_mb:.2f} MB\n\n"
            f"⬇️ Download:\n{download_url}\n\n"
            f"🎬 Stream:\n{stream_url}"
        )

        bot.reply_to(message, response)

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")


# 🚀 Run bot
if __name__ == "__main__":
    print("🚀 Bot is running...")
    bot.infinity_polling(skip_pending=True)
