import os
import telebot
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CLOUD_NAME = os.getenv("CLOUD_NAME")
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

bot = telebot.TeleBot(BOT_TOKEN)

# Cloudinary upload URL
CLOUDINARY_URL = f"https://api.cloudinary.com/v1_1/{CLOUD_NAME}/auto/upload"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🚀 Send any file to get a download link!")

@bot.message_handler(content_types=['document', 'video', 'audio', 'photo'])
def handle_file(message):
    try:
        # Get file info
        file_info = bot.get_file(message.document.file_id if message.document else
                                 message.video.file_id if message.video else
                                 message.audio.file_id if message.audio else
                                 message.photo[-1].file_id)

        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
        file_data = requests.get(file_url).content

        # Upload to Cloudinary
        response = requests.post(
            CLOUDINARY_URL,
            files={"file": file_data},
            data={
                "api_key": API_KEY,
                "api_secret": API_SECRET
            }
        )

        result = response.json()

        if "secure_url" in result:
            bot.reply_to(message, f"✅ Download Link:\n{result['secure_url']}")
        else:
            bot.reply_to(message, "❌ Upload failed!")

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

print("Bot is running...")
bot.infinity_polling()
