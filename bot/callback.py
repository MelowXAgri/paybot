# -*- coding: utf-8 -*-
from config import Config
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from database import UserRepository, QrisRepository

from .price import PRICE, PERMANENT
from .button import payment_markup
from .handler import (
    create_temp_link,
    create_perm_link_v1,
    
)

user_repository = UserRepository()
qris_repository = QrisRepository()

""" GROUP TEMPORARY V1 CALLBACK """
async def callback_live_temp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    vip_user = False
    if vip_user:
        invite_link = await create_temp_link(context.bot)
        caption = (
            "<blockquote>"
            "Anda sudah berlangganan!\n\n"
            f"Klik link ini untuk join grup Live Record Monthly: <a href='{invite_link}'>Join VIP</a>\n"
            "Link akan kadaluarsa dalam 1 jam!"
            "</blockquote>"
        )
        try:
            await update.callback_query.delete_message()
            await update.callback_query.message.reply_text(
                text=caption,
                parse_mode=ParseMode.HTML
            )
        except:
            pass
        return
    await update.callback_query.answer()
    caption = (
        "<blockquote>"
        "GROUP CONTENT VIDEO V1\n"
        " • TIDAK PERMANEN\n"
        " • UPDATE SETIAP HARI"
        "</blockquote>"
    )
    keyboard = [
        [InlineKeyboardButton(i['label'], callback_data=f"live_temp_{i['price']['qris']}_{i['price']['trakteer']}_{i['duration']}")] for i in PRICE
    ]
    keyboard.append([InlineKeyboardButton("Kembali", callback_data="back_callback")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        await update.callback_query.edit_message_text(
            text=caption,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        print(e)
        pass

async def callback_live_temp_subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    await update.callback_query.answer()
    data = update.callback_query.data.replace("live_temp_", "").split("_")
    qris_price = int(data[0])
    trakteer_price = int(data[1])
    duration = int(data[2])
    caption = (
        "<blockquote>"
        "Order\n\n"
        f"  • IDR: {qris_price}\n\n"
        "Bayar dengan QRIS:"
        "</blockquote>"
    )
    reply_markup = await payment_markup(qris_price, trakteer_price, duration)
    try:
        await update.callback_query.edit_message_text(
            text=caption,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    except:
        pass

""" GROUP PERMANENT CALLBACK HOST PILIHAN """
async def callback_host_pilihan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    vip_user = False
    if vip_user:
        invite_link = await create_perm_link_v1(context.bot)
        caption = (
            "<blockquote>"
            "Anda sudah berlangganan!\n\n"
            f"Klik link ini untuk join grup Live Record Host Pilihan: <a href='{invite_link}'>Join VIP</a>\n"
            "Link akan kadaluarsa dalam 1 jam!"
            "</blockquote>"
        )
        try:
            await update.callback_query.delete_message()
            await update.callback_query.message.reply_text(
                text=caption,
                parse_mode=ParseMode.HTML
            )
        except:
            pass
        return
    caption = (
        "<blockquote>"
        f"LIVE RECORD - HOST PILIHAN\n"
        "  • PERMANEN\n"
        "  • UPDATE SETIAP MINGGU\n"
        f"  • {PERMANENT['host_pilihan_v1']['price']['default']['label']}"
        "</blockquote>"
    )
    keyboard = [
        [InlineKeyboardButton("QRIS", callback_data=f"host_pilihan")],
        [InlineKeyboardButton("Kembali", callback_data="back_callback")]
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
        
""" GROUP PERMANENT CALLBACK DATABASE RECORD """
async def callback_database_record(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    vip_user = False
    if vip_user:
        invite_link = await create_perm_link_v2(context.bot)
        caption = (
            "<blockquote>"
            "Anda sudah berlangganan!\n\n"
            f"Klik link ini untuk join grup Live Record Database: <a href='{invite_link}'>Join VIP</a>\n"
            "Link akan kadaluarsa dalam 1 jam!"
            "</blockquote>"
        )
        try:
            await update.callback_query.delete_message()
            await update.callback_query.message.reply_text(
                text=caption,
                parse_mode=ParseMode.HTML
            )
        except:
            pass
        return
    caption = (
        "<blockquote>"
        f"LIVE RECORD - DATABASE\n"
        "  • FILE 2019 - 2025\n"
        "  • PERMANEN\n"
        "  • UPDATE SETIAP HARI\n"
        f"  • {PERMANENT['database_record_v2']['price']['default']['label']}"
        "</blockquote>"
    )
    keyboard = [
        [InlineKeyboardButton("QRIS", callback_data=f"database_record")],
        [InlineKeyboardButton("Kembali", callback_data="back_callback")]
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