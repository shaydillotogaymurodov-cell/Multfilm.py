import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

ADMIN_ID = 5422329001
VIDEOS_FILE = "videos.json"

# Videolarni fayldan yuklaymiz
try:
    with open(VIDEOS_FILE, "r") as f:
        VIDEOS = json.load(f)
except FileNotFoundError:
    VIDEOS = {}

TEMP = {}  # {admin_id: file_id}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        " MULTFILM botiga xush kelibsiz!\n"
        
        "🥳 Multfilm kodini yuboring, men video chiqaraman.\n\n"
    )

async def video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id != ADMIN_ID:
        return await update.message.reply_text("❗ Iltimos . Faqat kod yuboring.")

    if update.message.video:
        TEMP[user_id] = update.message.video.file_id
        await update.message.reply_text("🔢 Ushbu video uchun kod yozing:")
    else:
        await update.message.reply_text("❗ Faqat video yuboring.")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    code = update.message.text.strip()

    # Admin video yuborganidan keyin kod kiritsa
    if user_id == ADMIN_ID and user_id in TEMP:
        VIDEOS[code] = TEMP[user_id]
        del TEMP[user_id]

        # Faylga saqlaymiz
        with open(VIDEOS_FILE, "w") as f:
            json.dump(VIDEOS, f)

        return await update.message.reply_text(f"✅ Video '{code}' kodi bilan saqlandi!")

    # Foydalanuvchi kod yuborsa → video chiqaramiz
    if code in VIDEOS:
        return await update.message.reply_video(VIDEOS[code])

    return await update.message.reply_text("❗ Bunday kodli video topilmadi.")

def main():
    app = Application.builder().token("8599607394:AAHLU7vH9bQSi_y_xZhA1yZYEqdAmL1iw_4").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, video_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
