import os
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("BOT_TOKEN")

APPROVER_ID = 522707506

AUTHORIZED_USERS = {
    522707506: "Muhammad Asyraf"
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text(
            "❌ Anda tidak mempunyai akses kepada sistem ini."
        )
        return

    keyboard = [
        ["📥 Mohon Pinjaman"],
        ["📊 Status Laptop", "📜 Rekod Saya"]
    ]

    if user_id == APPROVER_ID:
        keyboard.append(["👨‍💼 Kelulusan Permohonan"])

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "💻 Tracker Pinjaman Laptop SK Labu Besar\n\nSila pilih menu:",
        reply_markup=reply_markup
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):


user_id = update.effective_user.id

if user_id not in AUTHORIZED_USERS:
    return

text = update.message.text

if text == "📥 Mohon Pinjaman":

    keyboard = [
        ["G1", "G2", "G3", "G4"],
        ["G5", "G6", "G7", "G8"],
        ["❌ Batal"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "💻 Pilih Laptop:",
        reply_markup=reply_markup
    )

elif text in ["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8"]:

    context.user_data["laptop"] = text

    keyboard = [
        ["📍 Hari Ini"],
        ["📆 Pilih Tarikh Lain"],
        ["❌ Batal"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        f"✅ Laptop dipilih: {text}\n\n📅 Tarikh Mula Pinjaman:",
        reply_markup=reply_markup
    )

elif text == "📍 Hari Ini":

    context.user_data["tarikh_mula"] = datetime.now().strftime("%d/%m/%Y")

    await update.message.reply_text(
        f"📅 Tarikh Mula: {context.user_data['tarikh_mula']}\n\n📆 Berapa hari pinjaman diperlukan?"
    )

elif text == "📆 Pilih Tarikh Lain":

    context.user_data["awaiting_date"] = True

    await update.message.reply_text(
        "Sila masukkan tarikh dalam format:\n\nDD/MM/YYYY\n\nContoh: 10/06/2026"
    )

elif context.user_data.get("awaiting_date"):

    try:

        datetime.strptime(text, "%d/%m/%Y")

        context.user_data["tarikh_mula"] = text
        context.user_data["awaiting_date"] = False

        await update.message.reply_text(
            f"📅 Tarikh Mula: {text}\n\n📆 Berapa hari pinjaman diperlukan?"
        )

    except ValueError:

        await update.message.reply_text(
            "❌ Format tarikh tidak sah.\n\nContoh: 10/06/2026"
        )

elif text == "❌ Batal":

    await start(update, context)

elif text == "📊 Status Laptop":

    await update.message.reply_text(
        "Fungsi Status Laptop akan dibina seterusnya."
    )

elif text == "📜 Rekod Saya":

    await update.message.reply_text(
        "Fungsi Rekod Saya akan dibina seterusnya."
    )

elif text == "👨‍💼 Kelulusan Permohonan":

    if user_id == APPROVER_ID:

        await update.message.reply_text(
            "Fungsi Kelulusan akan dibina seterusnya."
        )



app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
