import os
from datetime import datetime
import calendar
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("BOT_TOKEN")

APPROVER_ID = 522707506

AUTHORIZED_USERS = {
    522707506: "Muhammad Asyraf"
}

def build_calendar():

    today = datetime.now()

    year = today.year
    month = today.month

    cal = calendar.monthcalendar(year, month)

    keyboard = []

    keyboard.append([
        InlineKeyboardButton(
            f"📅 {today.strftime('%B %Y')}",
            callback_data="ignore"
        )
    ])

    for week in cal:

        row = []

        for day in week:

            if day == 0:
                row.append(
                    InlineKeyboardButton(" ", callback_data="ignore")
                )

            elif day == today.day:

                row.append(
                    InlineKeyboardButton(
                        f"🔵{day}",
                        callback_data=f"date_{day}"
                    )
                )

            else:

                row.append(
                    InlineKeyboardButton(
                        str(day),
                        callback_data=f"date_{day}"
                    )
                )

        keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)

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

        await update.message.reply_text(
            "📅 Pilih Tarikh:",
            reply_markup=build_calendar()
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

    elif text in ["1 Hari", "3 Hari", "5 Hari", "7 Hari", "14 Hari"]:

    bil_hari = int(text.split()[0])

    context.user_data["bil_hari"] = bil_hari

    await update.message.reply_text(
        f"📆 Tempoh dipilih: {bil_hari} hari\n\n📝 Sila masukkan tujuan / catatan pinjaman:"
    )

elif text == "✏️ Lain-lain":

    context.user_data["awaiting_days"] = True

    await update.message.reply_text(
        "Masukkan bilangan hari pinjaman:"
    )

elif context.user_data.get("awaiting_days"):

    try:

        bil_hari = int(text)

        context.user_data["bil_hari"] = bil_hari
        context.user_data["awaiting_days"] = False

        await update.message.reply_text(
            f"📆 Tempoh dipilih: {bil_hari} hari\n\n📝 Sila masukkan tujuan / catatan pinjaman:"
        )

    except ValueError:

        await update.message.reply_text(
            "❌ Sila masukkan nombor sahaja."
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


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    data = query.data

    if data == "ignore":
        return

    if data.startswith("date_"):

        day = int(data.replace("date_", ""))

        today = datetime.now()

        selected_date = datetime(
            today.year,
            today.month,
            day
        )

        context.user_data["tarikh_mula"] = selected_date.strftime("%d/%m/%Y")

        keyboard = [
            ["1 Hari", "3 Hari", "5 Hari"],
            ["7 Hari", "14 Hari"],
            ["✏️ Lain-lain"],
            ["❌ Batal"]
        ]

        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )

        await query.message.reply_text(
            f"✅ Tarikh dipilih: {context.user_data['tarikh_mula']}\n\n📆 Pilih tempoh pinjaman:",
            reply_markup=reply_markup
        )


app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_callback))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
