import json
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

ADMIN_ID = 5422329001
CHANNEL_ID = "@yangi_multfilmlar_uzz"  # <<< Siz bergan kanal qo‘shildi!

VIDEOS_FILE = "videos.json"

# Videolarni fayldan yuklaymiz
try:
    with open(VIDEOS_FILE, "r") as f:
        VIDEOS = json.load(f)
except FileNotFoundError:
    VIDEOS = {}

TEMP = {}  # {admin_id: file_id}


# ⚡️ FUNKSIYA: Obunani tekshirish
async def check_subscription(user_id, context):
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📣 Kanalga obuna bo‘lish", url="https://t.me/yangi_multfilmlar_uzz")],
        [InlineKeyboardButton("🔄 Obunani tekshirish", callback_data="check_sub")]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        " 🥳 MULTFILM botiga xush kelibsiz!\n"
        "📌 Botdan foydalanish uchun kanalimizga obuna bo‘ling.",
        reply_markup=markup
    )


# 🔘 Obunani tekshirish tugmasi
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    is_subscribed = await check_subscription(user_id, context)

    if is_subscribed:
        await query.edit_message_text("✅ Obuna tasdiqlandi!\n\n Endi 🥳 Multfilmilm kodini yuboring.")
    else:
        keyboard = [
            [InlineKeyboardButton("📣 Kanalga obuna bo‘lish", url="https://t.me/yangi_multfilmlar_uzz")],
            [InlineKeyboardButton("🔄 Qayta tekshirish", callback_data="check_sub")]
        ]
        await query.edit_message_text(
            "❗ Siz hali kanalga obuna bo‘lmagansiz!\n\n👇 Avval obuna bo‘ling:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


# Video qabul qilish (faqat admin)
async def video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id != ADMIN_ID:
        return await update.message.reply_text("❗ faqat kod yuboring.")

    if update.message.video:
        TEMP[user_id] = update.message.video.file_id
        await update.message.reply_text("🔢 Ushbu video uchun kod yozing:")
    else:
        await update.message.reply_text("❗ Faqat video yuboring.")


# Kodni qabul qilish
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    code = update.message.text.strip()

    # ❗ OBUNA TEKSHIRISH
    is_subscribed = await check_subscription(user_id, context)
    if not is_subscribed:
        keyboard = [
            [InlineKeyboardButton("📣 Kanalga obuna bo‘lish", url="https://t.me/yangi_multfilmlar_uzz")],
            [InlineKeyboardButton("🔄 Obunani tekshirish", callback_data="check_sub")]
        ]
        return await update.message.reply_text(
            "❗ Botdan foydalanish uchun kanalga obuna bo‘ling!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # Admin video yuborganidan keyin kod kiritsa
    if user_id == ADMIN_ID and user_id in TEMP:
        VIDEOS[code] = TEMP[user_id]
        del TEMP[user_id]

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
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.VIDEO, video_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
