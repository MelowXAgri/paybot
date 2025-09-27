# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo
)
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from database import UserRepository, QrisRepository, PromoRepository
from config import Config

import asyncio, random, pytz, aiohttp

from .button import (
    payment_markup,
    
)
from .price import PRICE, PERMANENT, PROMO_V1, get_qris_payment
from .subscriber import force_sub_channel, refresh_callback
from io import BytesIO

async def download_file(url: str) -> BytesIO:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            resp.raise_for_status()
            return BytesIO(await resp.read())


user_repository = UserRepository()
qris_repository = QrisRepository()
promo_repository = PromoRepository()
UTC = pytz.utc
TOS = """<blockquote>• Syarat Layanan {FORMAT_CHANNEL_NAME}
Dengan bergabung dalam grup ini, Anda menyetujui untuk mematuhi syarat layanan yang telah ditetapkan. Berikut adalah aturan dan pedoman yang harus diikuti oleh semua anggota.

1. Batasan Usia
Grup ini hanya diperuntukkan bagi individu yang berusia 18 tahun ke atas. Dengan bergabung, Anda mengonfirmasi bahwa Anda memenuhi persyaratan usia ini.

2. Konten yang Diizinkan
Grup ini dapat berisi konten dewasa yang hanya dapat diakses oleh anggota yang memenuhi syarat usia. Dilarang keras membagikan konten ilegal, diskriminatif, atau yang dapat merugikan orang lain.

3. Tanggung Jawab Anggota
Setiap anggota bertanggung jawab penuh atas konten yang mereka bagikan di grup. Anggota tidak diperbolehkan membagikan konten yang tidak sesuai dengan pedoman grup.

4. Penyalahgunaan
Penyalahgunaan grup, seperti spam, pelecehan, atau pelanggaran privasi, tidak akan ditoleransi. Anggota yang melanggar ketentuan ini akan dikenakan tindakan yang sesuai, termasuk penghapusan dari grup.

5. Perubahan Syarat
Syarat ini dapat diperbarui dari waktu ke waktu. Perubahan akan diumumkan dalam grup dan berlaku segera setelah diposting.

6. Hak Admin
Admin grup berhak menghapus anggota yang melanggar syarat atau kebijakan grup. Admin juga dapat menghapus konten yang dianggap tidak pantas.</blockquote>"""

""" Bot command started """
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    await user_repository.add_user(user_id)
    is_subscribed = await force_sub_channel(update, context)
    if not is_subscribed:
        keyboard = [
            [InlineKeyboardButton("JOIN CHANNEL", url=f"{Config.FORCE_SUB_CHANNEL_NAME}")],
            [InlineKeyboardButton("REFRESH", callback_data="refresh")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "Anda harus bergabung dengan channel kami terlebih dahulu untuk menggunakan bot ini!\n\n"
                "<blockquote>note:\njika sudah klik ' JOIN CHANNEL ' lalu klik ' REFRESH '</blockquote>"
            ),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        return
    caption = (
        f"Halo, {first_name} !\n\n"
        "Selamat datang di BOT GROUP VIP\n\n"
        "Contoh grup dan preview media: @livexrecord\n\n"
        "Berikut perintah yang tersedia:\n"
        "/order - Untuk join group VIP\n"
        "/promo - Untuk melihat promo yang tersedia\n\n"
        "Jangan ragu untuk menggunakan salah satu perintah ini untuk berinteraksi dengan bot\n\n"
        "<blockquote>Note: Global payment with Dollar $ , please contact support @Ibrawashere</blockquote>"
    )
    await update.message.reply_text(text=caption, parse_mode=ParseMode.HTML)

async def order_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await user_repository.add_user(user_id)
    is_subscribed = await force_sub_channel(update, context)
    if not is_subscribed:
        keyboard = [
            [InlineKeyboardButton("JOIN CHANNEL", url=f"{Config.FORCE_SUB_CHANNEL_NAME}")],
            [InlineKeyboardButton("REFRESH", callback_data="refresh")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "Anda harus bergabung dengan channel kami terlebih dahulu untuk menggunakan bot ini!\n\n"
                "<blockquote>note:\njika sudah klik ' JOIN CHANNEL ' lalu klik ' REFRESH '</blockquote>"
            ),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        return
    caption = (
        "<blockquote>"
        f"Halo {update.effective_user.first_name} Ingin order apa hari ini?\n\n"
        "Bot ini dibuat khusus untuk memudahkan kamu mendapatkan akses ke GROUP RECORD VIP kami yang berisi:\n\n"
        " • Ribuan koleksi video berkualitas\n"
        " • Update video terbaru setiap hari\n"
        " • Akses cepat dan mudah\n\n"
        "Silahkan gunakan tombol di bawah untuk mendapatkan akses VIP"
        "</blockquote>"
    )
    keyboard = [
        [InlineKeyboardButton("LIVE RECORD : PERBULAN", callback_data="live_temp_callback")],
        [InlineKeyboardButton("LIVE RECORD : HOST PILIHAN", callback_data="live_perm_v1")],
        [InlineKeyboardButton("LIVE RECORD : DATABASE", callback_data="live_perm_v2")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        text=caption,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )
    
async def tos_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await user_repository.add_user(user_id)
    channel = await context.bot.get_chat(Config.CHANNEL_TEMP)
    channel_name = channel.title
    await update.message.reply_text(
        text=TOS.format(FORMAT_CHANNEL_NAME=channel_name),
        parse_mode=ParseMode.HTML
    )
    
""" ADD COMMAND HANDLER """
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in Config.ADMIN_ID:
        return
    await user_repository.add_user(user_id)
    caption = (
        "Perintah untuk Admin:\n\n"
        "/broadcast - Broadcast ke pengguna BOT\n"
        "/vipbroadcast - Broadcast ke member VIP\n"
        "/broadcastpin - Broadcast dengan pin\n"
        "/vipbroadcastpin - Broadcast dengan pin ke member VIP\n"
        "/cekuser - Cek user VIP MONTHLY\n"
        "/addv1 - Tambah manual user VIP MONTHLY\n"
        "/addv2 - Tambah manual user HOST PILIHAN\n"
        "/addv3 - Tambah manual user DATABASE RECORD\n"
        "/promo [on|off] - Promo VIP"
    )
    await update.message.reply_text(text=caption)
    
async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in Config.ADMIN_ID:
        return
    await user_repository.add_user(user_id)
    if update.message.reply_to_message:
        msg = update.message.reply_to_message
        sent = 0
        async for user in user_repository.users.find():
            try:
                await context.bot.copy_message(
                    chat_id=int(user['user_id']),
                    from_chat_id=msg.chat.id,
                    message_id=msg.message_id,
                    caption=msg.caption,
                    caption_entities=msg.caption_entities,
                    reply_markup=msg.reply_markup
                )
                sent += 1
                await asyncio.sleep(0.5)
            except:
                pass
        total_user = await user_repository.users.count_documents({})
        await update.message.reply_text(f"Berhasil mengirim pesan ke {sent}/{total_user} pengguna.")
    else:
        await update.message.reply_text("Reply ke pesan yang ingin di-broadcast.")

async def vipbroadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in Config.ADMIN_ID:
        return
    await user_repository.add_user(user_id)
    if update.message.reply_to_message:
        msg = update.message.reply_to_message
        sent = 0
        async for user in user_repository.temp_user.find():
            try:
                await context.bot.copy_message(
                    chat_id=int(user['user_id']),
                    from_chat_id=msg.chat.id,
                    message_id=msg.message_id,
                    caption=msg.caption,
                    caption_entities=msg.caption_entities,
                    reply_markup=msg.reply_markup
                )
                sent += 1
                await asyncio.sleep(0.5)
            except:
                pass
        total_user = await user_repository.temp_user.count_documents({})
        await update.message.reply_text(f"Berhasil mengirim pesan ke {sent}/{total_user} member VIP.")
    else:
        await update.message.reply_text("Reply ke pesan yang ingin di-broadcast.")

async def broadcast_and_pin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in Config.ADMIN_ID:
        return
    await user_repository.add_user(user_id)
    if update.message.reply_to_message:
        msg = update.message.reply_to_message
        sent = 0
        async for user in user_repository.users.find():
            try:
                msg_to_pin = await context.bot.copy_message(
                    chat_id=int(user['user_id']),
                    from_chat_id=msg.chat.id,
                    message_id=msg.message_id,
                    caption=msg.caption,
                    caption_entities=msg.caption_entities,
                    reply_markup=msg.reply_markup
                )
                await context.bot.pin_chat_message(
                    chat_id=int(user['user_id']),
                    message_id=msg_to_pin.message_id,
                    disable_notification=False
                )
                sent += 1
                await asyncio.sleep(0.5)
            except:
                pass
        total_user = await user_repository.users.count_documents({})
        await update.message.reply_text(f"Berhasil mengirim pesan dan menyematkan ke {sent}/{total_user} pengguna.")
    else:
        await update.message.reply_text("Reply ke pesan yang ingin di-broadcast.")

async def vipbroadcast_and_pin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in Config.ADMIN_ID:
        return
    await user_repository.add_user(user_id)
    if update.message.reply_to_message:
        msg = update.message.reply_to_message
        sent = 0
        async for user in user_repository.temp_user.find():
            try:
                msg_to_pin = await context.bot.copy_message(
                    chat_id=int(user['user_id']),
                    from_chat_id=msg.chat.id,
                    message_id=msg.message_id,
                    caption=msg.caption,
                    caption_entities=msg.caption_entities,
                    reply_markup=msg.reply_markup
                )
                await context.bot.pin_chat_message(
                    chat_id=int(user['user_id']),
                    message_id=msg_to_pin.message_id,
                    disable_notification=False
                )
                sent += 1
                await asyncio.sleep(0.5)
            except:
                pass
        total_user = await user_repository.vip_temp_user.count_documents({})
        await update.message.reply_text(f"Berhasil mengirim pesan dan menyematkan ke {sent}/{total_user} member VIP.")
    else:
        await update.message.reply_text("Reply ke pesan yang ingin di-broadcast.")
    
async def cekuser_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in Config.ADMIN_ID:
        return
    await user_repository.add_user(user_id)
    now = datetime.now(UTC).astimezone(Config.TIMEZONE)
    time_ranges = {
        "< 1 minggu": (now, now + timedelta(weeks=1)),
        "1-2 minggu": (now + timedelta(weeks=1), now + timedelta(weeks=2)),
        "2-3 minggu": (now + timedelta(weeks=2), now + timedelta(weeks=3)),
        "3-4 minggu": (now + timedelta(weeks=3), now + timedelta(weeks=4)),
        "1-6 bulan": (now + timedelta(weeks=4), now + timedelta(weeks=24)),
        "6-12 bulan": (now + timedelta(weeks=24), now + timedelta(weeks=52)),
    }
    response = "Jumlah pengguna berdasarkan masa VIP:\n\n"
    for label, (start, end) in time_ranges.items():
        count = await user_repository.temp_user.count_documents({"expiry": {"$gte": start, "$lt": end}})
        response += f"{label}: {count} pengguna\n"
    vip_count = await user_repository.temp_user.count_documents({})
    host_pilihan_count = await user_repository.perm_v1.count_documents({})
    database_record_count = await user_repository.perm_v2.count_documents({})
    user_count = await user_repository.users.count_documents({})
    #filerecord_count = await db_bot_content.users.count_documents({})
    response += f"\n\nTotal pengguna VIP: {vip_count}\n\n"
    response += f"Total pengguna HOST PILIHAN: {host_pilihan_count}\n\n"
    response += f"Total pengguna DATABASE RECORD: {database_record_count}\n\n"
    #response += f"Total pengguna bot FileRecord : {filerecord_count}\n\n"
    response += f"Total pengguna bot: {user_count}"
    await update.message.reply_text(response)
    
async def add_v1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in Config.ADMIN_ID:
        return
    await user_repository.add_user(user_id)
    if len(context.args) != 2:
        await update.message.reply_text("Usage: /addv1 user_id jumlah_bulan")
        return
    try:
        user_id = int(context.args[0])
        months = int(context.args[1])
    except ValueError:
        await update.message.reply_text("Format salah. Pastikan user_id dan jumlah bulan adalah angka.")
        return
    user = await user_repository.temp_user.find_one({"user_id": user_id})
    now = datetime.now(UTC).astimezone(Config.TIMEZONE)
    if user:
        expiry = user["expiry"].astimezone(Config.TIMEZONE)
        new_expiry = expiry + timedelta(days=30 * months)
    else:
        new_expiry = now + timedelta(days=30 * months)
    await user_repository.temp_user.update_one(
        {"user_id": user_id},
        {"$set": {"expiry": new_expiry}},
        upsert=True
    )
    expiry_str = new_expiry.strftime("%d %B %Y, %H:%M %Z")
    await update.message.reply_text(f"User {user_id} telah ditambahkan/ diperpanjang VIP hingga {expiry_str}.")
    
async def add_host_pilihan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in Config.ADMIN_ID:
        return
    await user_repository.add_user(user_id)
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /addv2 user_id")
        return
    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Format salah. Pastikan user_id adalah angka.")
        return
    user = await user_repository.perm_v1.find_one({"user_id": user_id})
    if user:
        await update.message.reply_text("User sudah berlangganan!")
        return
    await user_repository.perm_v1.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id}},
        upsert=True
    )
    await update.message.reply_text(f"User {user_id} telah ditambahkan ke HOST PILIHAN.")

async def add_database_record(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in Config.ADMIN_ID:
        return
    await user_repository.add_user(user_id)
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /addv3 user_id")
        return
    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Format salah. Pastikan user_id adalah angka.")
        return
    user = await user_repository.perm_v2.find_one({"user_id": user_id})
    if user:
        await update.message.reply_text("User sudah berlangganan!")
        return
    await user_repository.perm_v2.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id}},
        upsert=True
    )
    await update.message.reply_text(f"User {user_id} telah ditambahkan ke DATABASE RECORD.")
    
async def promo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await user_repository.add_user(user_id)
    is_subscribed = await force_sub_channel(update, context)
    if not is_subscribed:
        keyboard = [
            [InlineKeyboardButton("JOIN CHANNEL", url=f"{Config.FORCE_SUB_CHANNEL_NAME}")],
            [InlineKeyboardButton("REFRESH", callback_data="refresh")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "Anda harus bergabung dengan channel kami terlebih dahulu untuk menggunakan bot ini!\n\n"
                "<blockquote>note:\njika sudah klik ' JOIN CHANNEL ' lalu klik ' REFRESH '</blockquote>"
            ),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        return
    if user_id in Config.ADMIN_ID:
        if len(context.args) == 1:
            promo_status = False
            if context.args[0] == "on":
                promo_status = True
            elif context.args[0] == "off":
                promo_status = False
            else:
                await update.message.reply_text("Usage:\n\n/promo [on/off]")
                return
            
            # Update status promo di database (menggunakan upsert jika dokumen tidak ada)
            await promo_repository.promo.update_one(
                {"_id": "promo_status"},
                {"$set": {"status": promo_status}},
                upsert=True
            )
            await update.message.reply_text(f"Status promo telah diubah menjadi: {context.args[0]}")
            return

    promo_status = await promo_repository.promo.find_one({"_id": "promo_status"})
    if not promo_status or not promo_status.get("status", False):
        await update.message.reply_text("Tidak ada promo yang berlangsung.")
        return
        
    keyboard = [
        [InlineKeyboardButton(f"{PROMO_V1['label']}", callback_data=f"promo_v1")],
        [InlineKeyboardButton(f"{PERMANENT['host_pilihan_v1']['price']['promo']['label']}", callback_data=f"promo_host_pilihan")],
        [InlineKeyboardButton(f"{PERMANENT['database_record_v2']['price']['promo']['label']}", callback_data=f"promo_database_record")],
        [InlineKeyboardButton("Kembali", callback_data="back_callback")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "PILIH PAKET PROMO\n\n"
        "<blockquote>"
        f"{PROMO_V1['label']}\n"
        "- TIDAK PERMANEN\n"
        "- UPDATE SETIAP HARI\n"
        f"- IDR : {PROMO_V1['price']['qris']}"
        "</blockquote>\n\n"
        "<blockquote>"
        f"{PERMANENT['host_pilihan_v1']['price']['promo']['label']}\n"
        "- PERMANEN\n"
        "- UPDATE SETIAP MINGGU\n"
        f"- IDR : {PERMANENT['host_pilihan_v1']['price']['promo']['price']}"
        "</blockquote>\n\n"
        "<blockquote>"
        f"{PERMANENT['database_record_v2']['price']['promo']['label']}\n"
        "- FILE 2019 - 2025\n"
        "- MEDIA RATUSAN RIBU\n"
        "- PERMANEN\n"
        "- UPDATE SETIAP HARI\n"
        f"- IDR : {PERMANENT['database_record_v2']['price']['promo']['price']}"
        "</blockquote>",
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

async def promo_v1_qris(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.callback_query.from_user.id
    username = update.callback_query.from_user.username
    if await qris_repository.qris.find_one({"user_id": user_id}):
        try:
            await update.callback_query.edit_message_text(
                text="Anda masih memiliki order yang sedang berlangsung.\n\nSilahkan batalkan order dengan perintah /cancel terlebih dahulu sebelum melakukan order baru."
            )
        except:
            pass
        return
    price = PROMO_V1['price']['qris']
    duration = 30
    while True:
        unique_code = random.randint(100, 999)
        total_price = price + unique_code
        existing_price = await qris_repository.qris.find_one({"price": total_price})
        if not existing_price:
            break
    qris_url, qris_code = get_qris_payment(total_price)
    qris_expired = datetime.now(UTC).astimezone(Config.TIMEZONE) + timedelta(minutes=10)
    try:
        await update.callback_query.delete_message()
    except:
        pass
    caption = (
        "Scan QRIS ini untuk pembayaran.\n\n"
        f"<b>Jumlah:</b> Rp {total_price}\n"
        f"<b>Expired:</b> {qris_expired.strftime('%H:%M:%S WIB')}\n\n"
        "QRIS akan kadaluarsa dalam 10 menit.\n\n\n"
        "<blockquote>"
        "Note: Jika sudah melakukan pembayaran , tunggu 1-5 menit , bot akan mengirimkan link."
        "</blockquote>"
    )
    keyboard = [
        [InlineKeyboardButton("CANCEL", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        img_bytes = await download_file(qris_url)
        msg = await update.callback_query.message.reply_photo(
            img_bytes,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        await qris_repository.add_qris(user_id, msg.id, duration, qris_code, qris_url, qris_expired.astimezone(UTC))
        context.job_queue.run_repeating(
            check_qris_payment, interval=60, first=30, user_id=user_id,
            data={
                "total_price": total_price, 
                "user_id": user_id, 
                "username": username, 
                "msg_id": msg.id, 
                "subscription": "monthly"
            }
        )
    except Exception as e:
        print(e)

async def promo_host_pilihan_qris(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.callback_query.from_user.id
    username = update.callback_query.from_user.username
    if await qris_repository.qris.find_one({"user_id": user_id}):
        try:
            await update.callback_query.edit_message_text(
                text="Anda masih memiliki order yang sedang berlangsung.\n\nSilahkan batalkan order dengan perintah /cancel terlebih dahulu sebelum melakukan order baru."
            )
        except:
            pass
        return
    price = PERMANENT['host_pilihan_v1']['price']['promo']['price']
    duration = 0
    while True:
        unique_code = random.randint(100, 999)
        total_price = price + unique_code
        existing_price = await qris_repository.qris.find_one({"price": total_price})
        if not existing_price:
            break
    qris_url, qris_code = get_qris_payment(total_price)
    qris_expired = datetime.now(UTC).astimezone(Config.TIMEZONE) + timedelta(minutes=10)
    try:
        await update.callback_query.delete_message()
    except:
        pass
    caption = (
        "Scan QRIS ini untuk pembayaran.\n\n"
        f"<b>Jumlah:</b> Rp {total_price}\n"
        f"<b>Expired:</b> {qris_expired.strftime('%H:%M:%S WIB')}\n\n"
        "QRIS akan kadaluarsa dalam 10 menit.\n\n\n"
        "<blockquote>"
        "Note: Jika sudah melakukan pembayaran , tunggu 1-5 menit , bot akan mengirimkan link."
        "</blockquote>"
    )
    keyboard = [
        [InlineKeyboardButton("CANCEL", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        img_bytes = await download_file(qris_url)
        msg = await update.callback_query.message.reply_photo(
            img_bytes,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        await qris_repository.add_qris(user_id, msg.id, duration, qris_code, qris_url, qris_expired.astimezone(UTC))
        context.job_queue.run_repeating(
            check_qris_payment, interval=60, first=30, user_id=user_id,
            data={
                "total_price": total_price, 
                "user_id": user_id, 
                "username": username, 
                "msg_id": msg.id, 
                "subscription": "host_pilihan"
            }
        )
    except Exception as e:
        print(e)

async def promo_database_record_qris(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.callback_query.from_user.id
    username = update.callback_query.from_user.username
    if await qris_repository.qris.find_one({"user_id": user_id}):
        try:
            await update.callback_query.edit_message_text(
                text="Anda masih memiliki order yang sedang berlangsung.\n\nSilahkan batalkan order dengan perintah /cancel terlebih dahulu sebelum melakukan order baru."
            )
        except:
            pass
        return
    price = PERMANENT['database_record_v2']['price']['promo']['price']
    duration = 0
    while True:
        unique_code = random.randint(100, 999)
        total_price = price + unique_code
        existing_price = await qris_repository.qris.find_one({"price": total_price})
        if not existing_price:
            break
    qris_url, qris_code = get_qris_payment(total_price)
    qris_expired = datetime.now(UTC).astimezone(Config.TIMEZONE) + timedelta(minutes=10)
    try:
        await update.callback_query.delete_message()
    except:
        pass
    caption = (
        "Scan QRIS ini untuk pembayaran.\n\n"
        f"<b>Jumlah:</b> Rp {total_price}\n"
        f"<b>Expired:</b> {qris_expired.strftime('%H:%M:%S WIB')}\n\n"
        "QRIS akan kadaluarsa dalam 10 menit.\n\n\n"
        "<blockquote>"
        "Note: Jika sudah melakukan pembayaran , tunggu 1-5 menit , bot akan mengirimkan link."
        "</blockquote>"
    )
    keyboard = [
        [InlineKeyboardButton("CANCEL", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        img_bytes = await download_file(qris_url)
        msg = await update.callback_query.message.reply_photo(
            img_bytes,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        await qris_repository.add_qris(user_id, msg.id, duration, qris_code, qris_url, qris_expired.astimezone(UTC))
        context.job_queue.run_repeating(
            check_qris_payment, interval=60, first=30, user_id=user_id,
            data={
                "total_price": total_price, 
                "user_id": user_id, 
                "username": username, 
                "msg_id": msg.id, 
                "subscription": "database_record"
            }
        )
    except Exception as e:
        print(e)

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await user_repository.add_user(user_id)
    user_qris = await qris_repository.qris.find_one({"user_id": user_id})
    if user_qris:
        if 'msg_id' in user_qris and user_qris['msg_id'] is not None:
            try:
                await context.bot.delete_message(chat_id=user_id, message_id=user_qris['msg_id'])
            except:
                pass
        await qris_repository.remove_qris(user_id)
        await update.message.reply_text("Order berhasil dibatalkan.")
    else:
        await update.message.reply_text("Anda tidak memiliki order yang sedang berlangsung.")

""" Payment callback """
async def callback_live_temp_qris(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.callback_query.from_user.id
    username = update.callback_query.from_user.username
    if await qris_repository.qris.find_one({"user_id": user_id}):
        try:
            await update.callback_query.edit_message_text(
                text="Anda masih memiliki order yang sedang berlangsung.\n\nSilahkan batalkan order dengan perintah /cancel terlebih dahulu sebelum melakukan order baru."
            )
        except:
            pass
        return
    price = int(update.callback_query.data.split("_")[2])
    duration = int(update.callback_query.data.split("_")[3])
    while True:
        unique_code = random.randint(100, 999)
        total_price = price + unique_code
        existing_price = await qris_repository.qris.find_one({"price": total_price})
        if not existing_price:
            break
    qris_url, qris_code = get_qris_payment(total_price)
    qris_expired = datetime.now(UTC).astimezone(Config.TIMEZONE) + timedelta(minutes=10)
    try:
        await update.callback_query.delete_message()
    except:
        pass
    caption = (
        "Scan QRIS ini untuk pembayaran.\n\n"
        f"<b>Jumlah:</b> Rp {total_price}\n"
        f"<b>Expired:</b> {qris_expired.strftime('%H:%M:%S WIB')}\n\n"
        "QRIS akan kadaluarsa dalam 10 menit.\n\n\n"
        "<blockquote>"
        "Note: Jika sudah melakukan pembayaran , tunggu 1-5 menit , bot akan mengirimkan link."
        "</blockquote>"
    )
    keyboard = [
        [InlineKeyboardButton("CANCEL", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        img_bytes = await download_file(qris_url)
        msg = await update.callback_query.message.reply_photo(
            img_bytes,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        await qris_repository.add_qris(user_id, msg.id, duration, qris_code, qris_url, qris_expired.astimezone(UTC))
        context.job_queue.run_repeating(
            check_qris_payment, interval=60, first=30, user_id=user_id,
            data={
                "total_price": total_price, 
                "user_id": user_id, 
                "username": username, 
                "msg_id": msg.id, 
                "subscription": "monthly"
            }
        )
    except Exception as e:
        print(e)

async def callback_host_pilihan_qris(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.callback_query.from_user.id
    username = update.callback_query.from_user.username
    if await qris_repository.qris.find_one({"user_id": user_id}):
        try:
            await update.callback_query.edit_message_text(
                text="Anda masih memiliki order yang sedang berlangsung.\n\nSilahkan batalkan order dengan perintah /cancel terlebih dahulu sebelum melakukan order baru."
            )
        except:
            pass
        return
    price = PERMANENT['host_pilihan_v1']['price']['default']['price']
    duration = 0
    while True:
        unique_code = random.randint(100, 999)
        total_price = price + unique_code
        existing_price = await qris_repository.qris.find_one({"price": total_price})
        if not existing_price:
            break
    qris_url, qris_code = get_qris_payment(total_price)
    qris_expired = datetime.now(UTC).astimezone(Config.TIMEZONE) + timedelta(minutes=10)
    try:
        await update.callback_query.delete_message()
    except:
        pass
    caption = (
        "Scan QRIS ini untuk pembayaran.\n\n"
        f"<b>Jumlah:</b> Rp {total_price}\n"
        f"<b>Expired:</b> {qris_expired.strftime('%H:%M:%S WIB')}\n\n"
        "QRIS akan kadaluarsa dalam 10 menit.\n\n\n"
        "<blockquote>"
        "Note: Jika sudah melakukan pembayaran , tunggu 1-5 menit , bot akan mengirimkan link."
        "</blockquote>"
    )
    keyboard = [
        [InlineKeyboardButton("CANCEL", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        img_bytes = await download_file(qris_url)
        msg = await update.callback_query.message.reply_photo(
            img_bytes,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        await qris_repository.add_qris(user_id, msg.id, duration, qris_code, qris_url, qris_expired.astimezone(UTC))
        context.job_queue.run_repeating(
            check_qris_payment, interval=60, first=30, user_id=user_id,
            data={
                "total_price": total_price, 
                "user_id": user_id, 
                "username": username, 
                "msg_id": msg.id, 
                "subscription": "host_pilihan"
            }
        )
    except Exception as e:
        print(e)

async def callback_database_record_qris(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.callback_query.from_user.id
    username = update.callback_query.from_user.username
    if await qris_repository.qris.find_one({"user_id": user_id}):
        try:
            await update.callback_query.edit_message_text(
                text="Anda masih memiliki order yang sedang berlangsung.\n\nSilahkan batalkan order dengan perintah /cancel terlebih dahulu sebelum melakukan order baru."
            )
        except:
            pass
        return
    price = PERMANENT['database_record_v2']['price']['default']['price']
    duration = 0
    while True:
        unique_code = random.randint(100, 999)
        total_price = price + unique_code
        existing_price = await qris_repository.qris.find_one({"price": total_price})
        if not existing_price:
            break
    qris_url, qris_code = get_qris_payment(total_price)
    qris_expired = datetime.now(UTC).astimezone(Config.TIMEZONE) + timedelta(minutes=10)
    try:
        await update.callback_query.delete_message()
    except:
        pass
    caption = (
        "Scan QRIS ini untuk pembayaran.\n\n"
        f"<b>Jumlah:</b> Rp {total_price}\n"
        f"<b>Expired:</b> {qris_expired.strftime('%H:%M:%S WIB')}\n\n"
        "QRIS akan kadaluarsa dalam 10 menit.\n\n\n"
        "<blockquote>"
        "Note: Jika sudah melakukan pembayaran , tunggu 1-5 menit , bot akan mengirimkan link."
        "</blockquote>"
    )
    keyboard = [
        [InlineKeyboardButton("CANCEL", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        img_bytes = await download_file(qris_url)
        msg = await update.callback_query.message.reply_photo(
            img_bytes,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        await qris_repository.add_qris(user_id, msg.id, duration, qris_code, qris_url, qris_expired.astimezone(UTC))
        context.job_queue.run_repeating(
            check_qris_payment, interval=60, first=30, user_id=user_id,
            data={
                "total_price": total_price, 
                "user_id": user_id, 
                "username": username, 
                "msg_id": msg.id, 
                "subscription": "database_record"
            }
        )
    except Exception as e:
        print(e)

async def callback_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.callback_query.from_user.id
    await user_repository.add_user(user_id)
    user_qris = await qris_repository.qris.find_one({"user_id": user_id})
    if user_qris:
        if 'msg_id' in user_qris and user_qris['msg_id'] is not None:
            try:
                await context.bot.delete_message(chat_id=user_id, message_id=user_qris['msg_id'])
            except:
                pass
        await qris_repository.remove_qris(user_id)
        await update.callback_query.message.reply_text("Order berhasil dibatalkan.")
    else:
        await update.callback_query.message.reply_text("Anda tidak memiliki order yang sedang berlangsung.")

""" Check payment """
async def get_mutasi():
    url = "https://orkut.ftvpn.me/api/mutasi"
    payload = {
        "auth_username": Config.ORDER_KUOTA_USERNAME,
        "auth_token": Config.ORDER_KUOTA_AUTHTOKEN
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                resp.raise_for_status()
                return await resp.json()
    except Exception as e:
        print("❌ Error:", e)
        try:
            data = await resp.json()
            print(data)
        except:
            pass
        return None

async def check_qris_payment(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    user_id = job.data['user_id']
    username = job.data['username']
    total_price = job.data['total_price']
    msg_id = job.data['msg_id']
    subscription = job.data['subscription']
    order = await qris_repository.qris.find_one({"user_id": user_id})
    if not order:
        job.schedule_removal()
        return
    
    expiry = order['expiry'].replace(tzinfo=pytz.UTC).astimezone(Config.TIMEZONE)
    msg_id = order['msg_id']
    histories = await get_mutasi()
    if histories is None:
        return
    print("Getting success history:", histories["status"])
    if histories["status"]:
        for history in histories['data']:
            if history['type'] == 'CR' and int(history['amount']) == total_price:
                await qris_repository.remove_qris(user_id)
                try:
                    await context.bot.delete_message(chat_id=user_id, message_id=msg_id)
                except:
                    pass
                if subscription == "monthly":
                    await monthly_v1_success(context.bot, user_id, order['duration'], username)
                elif subscription == "host_pilihan":
                    await permanent_v1_success(context.bot, user_id, "lifetime", username)
                elif subscription == "database_record":
                    await permanent_v2_success(context.bot, user_id, "lifetime", username)
                job.schedule_removal()
                return
    
    if datetime.now(UTC).astimezone(Config.TIMEZONE) >= expiry.astimezone(Config.TIMEZONE):
        try:
            await context.bot.delete_message(chat_id=user_id, message_id=msg_id)
        except:
            pass
        await context.bot.send_message(chat_id=user_id, text="Pembayaran gagal. QRIS telah kadaluarsa.")
        await qris_repository.qris.delete_one({"user_id": user_id})
        job.schedule_removal()


""" Successfull payment button 1 """
async def create_temp_link(bot_instance):
    try:
        chat = await bot_instance.get_chat(Config.CHANNEL_TEMP)
        expiry = datetime.now(UTC).astimezone(Config.TIMEZONE) + timedelta(minutes=60)
        try:
            invite_link = await bot_instance.create_chat_invite_link(
                chat_id=Config.CHANNEL_TEMP, expire_date=expiry, creates_join_request=True
            )
            return invite_link.invite_link
        except Exception as e:
            return str(e)
    except Exception as e:
        print(e)
        return str(e)

async def monthly_v1_success(bot_instance, user_id, duration, username=""):
    try:
        if type(duration) == int:
            try:
                invite_link = await create_temp_link(bot_instance)
            except:
                print(f"Failed: ( {Config.CHANNEL_TEMP} ) | ( {user_id} ) | ( {username} )")
            expiry = datetime.now(UTC).astimezone(Config.TIMEZONE) + timedelta(days=duration)
            await user_repository.add_temp_user(user_id, expiry)
            caption = (
                "🎉 Pembayaran berhasil!\n\n"
                f"🔥 Link: {invite_link}\n\n"
                "⚠️ NOTE !\nLink akan kadaluarsa dalam 1 jam!"
            )
            await bot_instance.send_message(chat_id=user_id, text=caption, parse_mode=ParseMode.HTML)
    except Exception as e:
        print("Error vip monthly:", e)
        
""" Successfull payment button 2 """
async def create_perm_link_v1(bot_instance):
    try:
        chat = await bot_instance.get_chat(Config.CHANNEL_PERM_1)
        expiry = datetime.now(UTC).astimezone(Config.TIMEZONE) + timedelta(minutes=60)
        try:
            invite_link = await bot_instance.create_chat_invite_link(
                chat_id=Config.CHANNEL_PERM_1, expire_date=expiry, creates_join_request=True
            )
            return invite_link.invite_link
        except Exception as e:
            return str(e)
    except Exception as e:
        print(e)
        return str(e)

async def permanent_v1_success(bot_instance, user_id, duration, username=""):
    try:
        invite_link = create_perm_link_v1(bot_instance)
    except:
        print(f"Failed: ( {Config.CHANNEL_PERM_1} ) | ( {user_id} ) | ( {username} )")
    await user_repository.add_perm_v1(user_id)
    caption = (
        "🎉 Pembayaran berhasil!\n\n"
        f"🔥 Link: {invite_link}\n\n"
        "⚠️ NOTE !\nLink akan kadaluarsa dalam 1 jam!"
    )
    await bot_instance.send_message(chat_id=user_id, text=caption, parse_mode=ParseMode.HTML)

""" Successfull payment button 3 """
async def create_perm_link_v2(bot_instance):
    try:
        chat = await bot_instance.get_chat(Config.CHANNEL_PERM_2)
        expiry = datetime.now(UTC).astimezone(Config.TIMEZONE) + timedelta(minutes=60)
        try:
            invite_link = await bot_instance.create_chat_invite_link(
                chat_id=Config.CHANNEL_PERM_2, expire_date=expiry, creates_join_request=True
            )
            return invite_link.invite_link
        except Exception as e:
            return str(e)
    except Exception as e:
        print(e)
        return str(e)

async def permanent_v2_success(bot_instance, user_id, duration, username=""):
    try:
        invite_link = create_perm_link_v2(bot_instance)
    except:
        print(f"Failed: ( {Config.CHANNEL_PERM_2} ) | ( {user_id} ) | ( {username} )")
    await user_repository.add_perm_v2(user_id)
    caption = (
        "🎉 Pembayaran berhasil!\n\n"
        f"🔥 Link: {invite_link}\n\n"
        "⚠️ NOTE !\nLink akan kadaluarsa dalam 1 jam!"
    )
    await bot_instance.send_message(chat_id=user_id, text=caption, parse_mode=ParseMode.HTML)

""" Button Back Callback Handler """
async def back_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    caption = (
        "<blockquote>"
        f"Halo {update.effective_user.first_name} Ingin order apa hari ini?\n\n"
        "Bot ini dibuat khusus untuk memudahkan kamu mendapatkan akses ke GROUP RECORD VIP kami yang berisi:\n\n"
        " • Ribuan koleksi video berkualitas\n"
        " • Update video terbaru setiap hari\n"
        " • Akses cepat dan mudah\n\n"
        "Silahkan gunakan tombol di bawah untuk mendapatkan akses VIP"
        "</blockquote>"
    )
    keyboard = [
        [InlineKeyboardButton("LIVE RECORD : PERBULAN ( V1 )", callback_data="live_temp_callback")],
        [InlineKeyboardButton("LIVE RECORD : HOST PILIHAN", callback_data="live_perm_v1")],
        [InlineKeyboardButton("LIVE RECORD : DATABASE", callback_data="live_perm_v2")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        await update.callback_query.edit_message_text(
            text=caption,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    except:
        pass
        
async def handle_chat_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    req = update.chat_join_request
    user_id = req.from_user.id
    await user_repository.add_user(user_id)
    if req.chat.id == Config.CHANNEL_TEMP:
        member = await user_repository.temp_user.find_one({"user_id": user_id})
        if member:
            try:
                await context.bot.approve_chat_join_request(chat_id=Config.CHANNEL_TEMP, user_id=user_id)
            except Exception as e:
                if "User_already_participant" in str(e):
                    return
                else:
                    print("Error accept member CHANNEL_TEMP:", e)
                return
            await context.bot.send_message(user_id, "Permintaan join Anda telah disetujui!")
        else:
            await context.bot.decline_chat_join_request(chat_id=Config.CHANNEL_TEMP, user_id=user_id)
            await context.bot.send_message(user_id, "Anda belum berlangganan VIP.")
    elif req.chat.id == Config.CHANNEL_PERM_1:
        member = await user_repository.perm_v1.find_one({"user_id": user_id})
        if member:
            try:
                await context.bot.approve_chat_join_request(chat_id=Config.CHANNEL_PERM_1, user_id=user_id)
            except Exception as e:
                if "User_already_participant" in str(e):
                    return
                else:
                    print("Error accept member CHANNEL_PERM_1:", e)
                return
            await context.bot.send_message(user_id, "Permintaan join Anda telah disetujui!")
        else:
            await context.bot.decline_chat_join_request(chat_id=Config.CHANNEL_PERM_1, user_id=user_id)
            await context.bot.send_message(user_id, "Anda belum berlangganan Host Pilihan.")
    elif req.chat.id == Config.CHANNEL_PERM_2:
        member = await user_repository.perm_v2.find_one({"user_id": user_id})
        if member:
            try:
                await context.bot.approve_chat_join_request(chat_id=Config.CHANNEL_PERM_2, user_id=user_id)
            except Exception as e:
                if "User_already_participant" in str(e):
                    return
                else:
                    print("Error accept member CHANNEL_PERM_2:", e)
                return
            await context.bot.send_message(user_id, "Permintaan join Anda telah disetujui!")
        else:
            await context.bot.decline_chat_join_request(chat_id=Config.CHANNEL_PERM_2, user_id=user_id)
            await context.bot.send_message(user_id, "Anda belum berlangganan DATABASE RECORD.")
