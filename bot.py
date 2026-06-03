import os
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

```
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
```

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

```
user_id = update.effective_user.id

if user_id not in AUTHORIZED_USERS:
    return

text = update.message.text

if text == "📥 Mohon Pinjaman":
    await update.message.reply_text(
        "💻 Pilih Laptop:\n\nG1, G2, G3, G4, G5, G6, G7 atau G8"
    )

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
```

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
