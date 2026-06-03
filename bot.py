import os
from datetime import datetime, timedelta
import calendar
import json
import gspread
from zoneinfo import ZoneInfo
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

from datetime import datetime

def kemaskini_status(
    permohonan_id,
    status_baru,
    pegawai=None
):

    semua_data = sheet.get_all_records()

    for index, row in enumerate(semua_data, start=2):

        if str(row["ID"]) == str(permohonan_id):

            sheet.update_cell(
                index,
                10,
                status_baru
            )

            if pegawai:

                sheet.update_cell(
                    index,
                    11,
                    pegawai
                )

                sheet.update_cell(
                    index,
                    12,
                    datetime.now(
                        ZoneInfo("Asia/Kuala_Lumpur")
                    ).strftime("%d/%m/%Y %H:%M")
                )

            return True

    return False

def dapatkan_permohonan(permohonan_id):

    semua_data = sheet.get_all_records()

    for row in semua_data:

        if str(row["ID"]) == str(permohonan_id):
            return row

    return None

def status_laptop():

    semua_data = sheet.get_all_records()

    status = {
        "G1": "🟢 Tersedia",
        "G2": "🟢 Tersedia",
        "G3": "🟢 Tersedia",
        "G4": "🟢 Tersedia",
        "G5": "🟢 Tersedia",
        "G6": "🟢 Tersedia",
        "G7": "🟢 Tersedia",
        "G8": "🟢 Tersedia"
    }

    for row in semua_data:

        laptop = row["Laptop"]

        if row["Status"] == "Menunggu Kelulusan":

            status[laptop] = "🟡 Menunggu Kelulusan"

        elif row["Status"] == "Diluluskan":

            status[laptop] = (
                f"🔴 Dipinjam sehingga "
                f"{row['Tarikh Pulang']}"
            )

    return status

def semak_ketersediaan_laptop(
    laptop,
    tarikh_mula_baru,
    tarikh_pulang_baru
):

    semua_data = sheet.get_all_records()

    for row in semua_data:

        if row["Laptop"] != laptop:
            continue

        if row["Status"] not in ["Menunggu Kelulusan", "Diluluskan"]:
            continue

        mula_lama = datetime.strptime(
            row["Tarikh Pinjam"],
            "%d/%m/%Y"
        )

        pulang_lama = datetime.strptime(
            row["Tarikh Pulang"],
            "%d/%m/%Y"
        )

        if (
            tarikh_mula_baru <= pulang_lama and
            tarikh_pulang_baru >= mula_lama
        ):
            return False

    return True

def simpan_permohonan(data):

    next_id = len(sheet.get_all_values())

    sheet.insert_row([
        next_id,
        data["nama"],
        data["telegram_id"],
        data["laptop"],
        data["tarikh_permohonan"],
        data["tarikh_mula"],
        data["bil_hari"],
        data["tarikh_pulang"],
        data["catatan"],
        "Menunggu Kelulusan",
        "",
        ""
    ], 2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text(
            "❌ Anda tidak mempunyai akses kepada sistem ini."
        )
        return

    keyboard = [
        ["📥 Mohon Pinjaman"],
        ["📊 Status Laptop", "📜 Rekod Pinjaman Saya"]
    ]

    if user_id == APPROVER_ID:
        keyboard.append(["📝 Tindakan GPK"])

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
            f"📅 Tarikh Mula Pinjaman: {context.user_data['tarikh_mula']}\n\n📆 Pilih tempoh pinjaman:",
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
            f"📆 Tempoh dipilih: {bil_hari} hari\n\n📝 Sila masukkan tujuan / catatan pinjaman jika ada: (Contoh: PDP, tidak ada mouse)"
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
                f"📆 Tempoh dipilih: {bil_hari} hari\n\n📝 Sila masukkan tujuan / catatan pinjaman jika ada: (Contoh: PDP, tidak ada mouse)"
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
            f"📅 Tarikh Mula Pinjam : {context.user_data['tarikh_mula']}\n"
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

        tersedia = semak_ketersediaan_laptop(
            context.user_data["laptop"],
            tarikh_mula,
            tarikh_pulang
        )

        if not tersedia:

            await update.message.reply_text(
                f"❌ Laptop {context.user_data['laptop']} "
                "telah ditempah atau sedang dipinjam "
                "dalam tempoh tersebut.\n\n"
                "Sila pilih tarikh lain atau laptop lain."
            )

            return

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
            "📋 Status: Maklumkan pada GPK untuk mengesahkan pinjaman sebelum atau selepas mengambil laptop. "
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

        status = status_laptop()

        mesej = (
            "💻 STATUS LAPTOP\n\n"
            f"G1 : {status['G1']}\n"
            f"G2 : {status['G2']}\n"
            f"G3 : {status['G3']}\n"
            f"G4 : {status['G4']}\n"
            f"G5 : {status['G5']}\n"
            f"G6 : {status['G6']}\n"
            f"G7 : {status['G7']}\n"
            f"G8 : {status['G8']}"
        )

        await update.message.reply_text(mesej)

    elif text == "📜 Rekod Pinjaman Saya":

        semua_data = sheet.get_all_records()
        semua_data.reverse()

        rekod_pengguna = []

        for row in semua_data:

            if str(row["Telegram ID"]) == str(user_id):

                status = row["Status"]

                if status == "Diluluskan":
                    ikon = "✅"

                elif status == "Ditolak":
                    ikon = "❌"

                else:
                    ikon = "🟡"

                rekod_pengguna.append(
                    f"#{row['ID']} | {row['Laptop']}\n"
                    f"📅 {row['Tarikh Pinjam']} → {row['Tarikh Pulang']}\n"
                    f"📝 {row['Catatan']}\n"
                    f"{ikon} {status}\n"
                )

        if not rekod_pengguna:

            await update.message.reply_text(
                "📭 Anda belum mempunyai sebarang rekod pinjaman."
            )

        else:

            await update.message.reply_text(
                "📜 REKOD PINJAMAN ANDA\n\n"
                + "\n".join(rekod_pengguna)
            )

    elif text == "📝 Tindakan GPK":

        if user_id == APPROVER_ID:

            semua_data = sheet.get_all_records()

            keyboard = []

            for row in semua_data:

                if row["Status"] == "Menunggu Kelulusan":

                    keyboard.append([
                        InlineKeyboardButton(
                            f"#{row['ID']} - {row['Nama']} ({row['Laptop']})",
                            callback_data=f"permohonan_{row['ID']}"
                        )
                    ])

            if not keyboard:

                await update.message.reply_text(
                    "✅ Tiada permohonan yang menunggu kelulusan."
                )

            else:

                await update.message.reply_text(
                    "📋 Pilih Permohonan:",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    data = query.data

    user_id = query.from_user.id

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

        

    elif data.startswith("permohonan_"):

        permohonan_id = int(
            data.replace("permohonan_", "")
        )

        semua_data = sheet.get_all_records()

        for row in semua_data:

            if str(row["ID"]) == str(permohonan_id):

                keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "✅ Lulus",
                            callback_data=f"approve_{permohonan_id}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "❌ Tolak",
                            callback_data=f"reject_{permohonan_id}"
                        )
                    ]
                ])

                await query.message.reply_text(
                    f"📋 PERMOHONAN #{row['ID']}\n\n"
                    f"👤 Nama : {row['Nama']}\n"
                    f"💻 Laptop : {row['Laptop']}\n"
                    f"📅 Tarikh Pinjam : {row['Tarikh Pinjam']}\n"
                    f"📆 Tempoh : {row['Tempoh Hari']} Hari\n"
                    f"📅 Tarikh Pulang : {row['Tarikh Pulang']}\n\n"
                    f"📝 Catatan :\n{row['Catatan']}\n\n"
                    f"📋 Status : {row['Status']}",
                    reply_markup=keyboard
                )

                break   

    elif data.startswith("approve_"):

        permohonan_id = int(
            data.replace("approve_", "")
        )

        berjaya = kemaskini_status(
            permohonan_id,
            "Diluluskan",
            AUTHORIZED_USERS[user_id]
        )

        if berjaya:

            rekod = dapatkan_permohonan(
                permohonan_id
            )

            await context.bot.send_message(
                chat_id=int(rekod["Telegram ID"]),
                text=(
                    "🎉 Permohonan pinjaman laptop telah diluluskan.\n\n"
                    f"💻 Laptop: {rekod['Laptop']}\n"
                    f"📅 Tarikh Pinjam: {rekod['Tarikh Pinjam']}\n"
                    f"📅 Tarikh Pulang: {rekod['Tarikh Pulang']}"
                )
            )

            await query.edit_message_text(
                f"✅ Permohonan #{permohonan_id} telah diluluskan."
            )

        else:

            await query.edit_message_text(
                "❌ Gagal mengemaskini status."
            )

    elif data.startswith("reject_"):

        permohonan_id = int(
            data.replace("reject_", "")
        )

        berjaya = kemaskini_status(
            permohonan_id,
            "Ditolak",
            AUTHORIZED_USERS[user_id]
        )

        if berjaya:

            rekod = dapatkan_permohonan(
                permohonan_id
            )

            await context.bot.send_message(
                chat_id=int(rekod["Telegram ID"]),
                text=(
                    "❌ Permohonan pinjaman laptop tidak diluluskan.\n\n"
                    f"💻 Laptop: {rekod['Laptop']}\n"
                    f"📅 Tarikh Pinjam: {rekod['Tarikh Pinjam']}"
                )
            )

            await query.edit_message_text(
                f"❌ Permohonan #{permohonan_id} telah ditolak."
            )

        else:
    
            await query.edit_message_text(
                "❌ Gagal mengemaskini status."
            )

    

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_callback))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
