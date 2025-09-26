# -*- coding: utf-8 -*-
from bot.bot import bot
from bot.job_queue import setup_jobs
from telegram import BotCommand
from fastapi import FastAPI

import asyncio, uvicorn

app = FastAPI()

web_server = uvicorn.Server(
    config=uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
)

async def main():
    bot.register_handler()
    setup_jobs(bot.app.job_queue)
    async with bot.app:
        await bot.app.initialize()
        await bot.app.start()
        await bot.app.bot.set_my_commands([
            BotCommand("start", "Menampilkan menu"),
            BotCommand("order", "Untuk join group VIP"),
            BotCommand("promo", "Untuk melihat promo yang tersedia"),
            BotCommand("tos", "Untuk melihat syarat dan ketentuan VIP"),
        ])
        await bot.app.updater.start_polling()
        await web_server.serve()
        await bot.app.updater.stop()
        await bot.app.stop()

if __name__ == "__main__":
    asyncio.run(main())