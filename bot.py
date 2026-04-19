import os
import requests
import yt_dlp
import tempfile
import shutil

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

keyboard = [
    ["📥 Invia file"],
    ["📖 Guida", "🆘 Supporto"]
]
markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Benvenuto!\n\n"
        "📥 Invia un link TikTok / Instagram / YouTube\n"
        "⚡ Ricevi il file qui",
        reply_markup=markup
    )

class SilentLogger:
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass

def scarica_video_temp(url):
    temp_dir = tempfile.mkdtemp()

    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{temp_dir}/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'logger': SilentLogger()
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)

    return file_path, temp_dir

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text in ["📖 Guida"]:
        await update.message.reply_text("Invia un link e ricevi il video.")
        return

    if text in ["🆘 Supporto"]:
        await update.message.reply_text("Supporto: @tuonome")
        return

    if text == "📥 Invia file":
        await update.message.reply_text("📎 Mandami un link")
        return

    await update.message.reply_text("⏳ Scarico...")

    file_path = None
    temp_dir = None

    try:
        if "tiktok.com" in text:
            api = f"https://tikwm.com/api/?url={text}"
            r = requests.get(api).json()
            video_url = r["data"]["play"]
            await update.message.reply_video(video_url)

        elif "instagram.com" in text or "youtube.com" in text or "youtu.be" in text:
            file_path, temp_dir = scarica_video_temp(text)

            with open(file_path, "rb") as f:
                await update.message.reply_video(f)

    except:
        await update.message.reply_text("⚠️ Contenuto non disponibile")

    finally:
        try:
            if file_path: os.remove(file_path)
            if temp_dir: shutil.rmtree(temp_dir)
        except:
            pass

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot avviato...")
app.run_polling()
