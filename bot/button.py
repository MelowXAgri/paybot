# -*- coding: utf-8 -*-
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def payment_markup(qris_price, trakteer_price, duration):
    keyboard = [
        [InlineKeyboardButton("QRIS", callback_data=f"price_qris_{qris_price}_{duration}")],
        [InlineKeyboardButton("Kembali", callback_data="back_callback")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup

