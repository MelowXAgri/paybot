# -*- coding: utf-8 -*-
from config import Config
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

async def force_sub_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user = update.effective_user
    try:
        member = await context.bot.get_chat_member(chat_id=Config.FORCE_SUB_CHANNEL_ID, user_id=user.id)
        if member.status not in ["creator", "administrator", "member"]:
            return False
        return True
    except Exception as e:
        if "chat not found" in str(e).lower():
            print("Oops saya tidak berada di group / channel tersebut.")
        elif "Forbidden: bot was kicked from the supergroup chat" in str(e):
            print("Oops saya di telah dikeluarkan dari group / channel tersebut.")
        return False

async def refresh_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() 
    user = update.effective_user
    first_name = update.effective_user.first_name
    try:
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
        member = await context.bot.get_chat_member(chat_id=Config.FORCE_SUB_CHANNEL_ID, user_id=user.id)
        if member.status in ["creator", "administrator", "member"]:
            await query.edit_message_text(
                text=caption,
                reply_markup=None,
                parse_mode=ParseMode.HTML
            )
            return
        else:
            keyboard = [
                [InlineKeyboardButton("JOIN CHANNEL", url=f"{Config.FORCE_SUB_CHANNEL_NAME}")],
                [InlineKeyboardButton("REFRESH", callback_data="refresh")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text=(
                    "Sepertinya anda masih belum bergabung dengan channel kami..\n\n"
                    "<blockquote>note:\njika sudah klik ' JOIN CHANNEL ' lalu klik ' REFRESH '</blockquote>"
                ),
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
    except Exception as e:
        pass