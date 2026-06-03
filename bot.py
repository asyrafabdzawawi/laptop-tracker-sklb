import os
from datetime import datetime, timedelta
import calendar
import json
import gspread
from google.oauth2.service_account import Credentials
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

SPREADSHEET_ID = "1h9dhCZRjwVVnwO46XiTUs77m5cyfSH60L-UgFRJlybA"

creds_dict = json.loads(os.getenv("GOOGLE_CREDENTIALS"))

creds = Credentials.from_service_account_info(
    creds_dict,
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
)

client = gspread.authorize(creds)

sheet = client.open_by_key(SPREADSHEET_ID).worksheet("permohonan")

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

def simpan_permohonan(data):

    next_id = len(sheet.get_all_values())

    sheet.append_row([
        next_id,
        data["nama"],
        data["telegram_id"],
        data["laptop"],
        data["tarikh_permohonan"],
        data["tarikh_mula"],
        data["bil_hari"],
        data["tarikh_pulang"],
        data["catatan"],
        "Menunggu"
    ])

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

        await update.message.reply_text(
            f"📅 Tarikh Mula: {context.user_data['tarikh_mula']}\n\n📆 Pilih tempoh pinjaman:",
            reply_markup=reply_markup
        )

    elif text == "📆 Pilih Tarikh Lain":

        await update.message.reply_text(
            "📅 Pilih Tarikh:",
            reply_markup=build_calendar()
        )

    elif text in ["1 Hari", "3 Hari", "5 Hari", "7 Hari", "14 Hari"]:

        bil_hari = int(text.split()[0])

        context.user_data["bil_hari"] = bil_hari

        await update.message.reply_text(
            f"📆 Tempoh dipilih: {bil_hari} hari\n\n📝 Sila masukkan tujuan / catatan pinjaman:"
        )

        context.user_data["awaiting_catatan"] = True

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

            context.user_data["awaiting_catatan"] = True

        except ValueError:

            await update.message.reply_text(
                "❌ Sila masukkan nombor sahaja."
            )

    elif context.user_data.get("awaiting_catatan"):

        context.user_data["catatan"] = text
        context.user_data["awaiting_catatan"] = False

        keyboard = [
            ["✅ Hantar Permohonan"],
            ["✏️ Ubah"],
            ["❌ Batal"]
        ]

        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )

        await update.message.reply_text(
            f"📋 SEMAKAN PERMOHONAN\n\n"
            f"💻 Laptop : {context.user_data['laptop']}\n"
            f"📅 Tarikh Mula : {context.user_data['tarikh_mula']}\n"
            f"📆 Tempoh : {context.user_data['bil_hari']} Hari\n\n"
            f"📝 Catatan :\n{context.user_data['catatan']}",
            reply_markup=reply_markup
        )

    elif text == "✅ Hantar Permohonan":

        tarikh_permohonan = datetime.now()

        tarikh_mula = datetime.strptime(
            context.user_data["tarikh_mula"],
            "%d/%m/%Y"
        )

        tarikh_pulang = tarikh_mula + timedelta(
            days=context.user_data["bil_hari"]
        )

        simpan_permohonan({
            "nama": AUTHORIZED_USERS[user_id],
            "telegram_id": user_id,
            "laptop": context.user_data["laptop"],
            "tarikh_permohonan": tarikh_permohonan.strftime("%d/%m/%Y"),
            "tarikh_mula": context.user_data["tarikh_mula"],
            "bil_hari": context.user_data["bil_hari"],
            "tarikh_pulang": tarikh_pulang.strftime("%d/%m/%Y"),
            "catatan": context.user_data["catatan"]
        })

        await update.message.reply_text(
            "✅ Permohonan berjaya dihantar.\n\n"
            "📋 Status: Menunggu Kelulusan Pegawai Pengesah"
        )

        context.user_data.clear()

        await start(update, context)

    elif text == "✏️ Ubah":

        context.user_data.clear()

        await update.message.reply_text(
            "✏️ Sila buat permohonan semula."
        )

        await start(update, context)

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

            semua_data = sheet.get_all_records()

            permohonan_menunggu = []

            for row in semua_data:

                if row["Status"] == "Menunggu":

                    permohonan_menunggu.append(
                        f"#{row['ID']} - {row['Nama']} ({row['Laptop']})"
                    )

            if not permohonan_menunggu:

                await update.message.reply_text(
                    "✅ Tiada permohonan yang menunggu kelulusan."
                )

            else:

                await update.message.reply_text(
                    "📋 Permohonan Menunggu Kelulusan\n\n"
                    + "\n".join(permohonan_menunggu)
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
