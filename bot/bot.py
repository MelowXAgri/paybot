from telegram.ext import (
    Application,
    CallbackQueryHandler,
    ChatJoinRequestHandler,
    CommandHandler,
    filters,
    Defaults
)
from config import Config
from .callback import (
    callback_live_temp,
    callback_live_temp_subscribe,
    
    callback_host_pilihan,
    callback_database_record,
)
from .handler import (
    start_command,
    order_command,
    cancel_command,
    tos_command,
    admin_command,
    cekuser_command,
    add_v1,
    add_host_pilihan,
    add_database_record,
    promo_command,
    promo_v1_qris,
    promo_host_pilihan_qris,
    promo_database_record_qris,
    callback_live_temp_qris,
    callback_host_pilihan_qris,
    callback_database_record_qris,
    callback_cancel,
    back_callback_handler,
    handle_chat_join_request,
    broadcast_handler,
    vipbroadcast_handler,
    broadcast_and_pin_handler,
    vipbroadcast_and_pin_handler,
)
from .subscriber import refresh_callback

class TelegramBot:
    def __init__(self):
        self.app = Application.builder().token(Config.BOT_TOKEN).get_updates_read_timeout(120).get_updates_connect_timeout(30).build()

    def register_handler(self):
        self.app.add_handler(CommandHandler("start", start_command, filters=filters.ChatType.PRIVATE))
        self.app.add_handler(CommandHandler("order", order_command, filters=filters.ChatType.PRIVATE))
        self.app.add_handler(CommandHandler("tos", tos_command, filters=filters.ChatType.PRIVATE))
        
        """ ADMIN MENU """
        self.app.add_handler(CommandHandler("admin", admin_command, filters=filters.ChatType.PRIVATE))
        self.app.add_handler(CommandHandler("broadcastpin", broadcast_and_pin_handler, filters=filters.ChatType.PRIVATE, block=False))
        self.app.add_handler(CommandHandler("vipbroadcastpin", vipbroadcast_and_pin_handler, filters=filters.ChatType.PRIVATE, block=False))
        
        self.app.add_handler(CommandHandler("broadcast", broadcast_handler, filters=filters.ChatType.PRIVATE, block=False))
        self.app.add_handler(CommandHandler("vipbroadcast", vipbroadcast_handler, filters=filters.ChatType.PRIVATE, block=False))
        self.app.add_handler(CommandHandler("cekuser", cekuser_command, filters=filters.ChatType.PRIVATE))
        self.app.add_handler(CommandHandler("addv1", add_v1, filters=filters.ChatType.PRIVATE))
        self.app.add_handler(CommandHandler("addv2", add_host_pilihan, filters=filters.ChatType.PRIVATE))
        self.app.add_handler(CommandHandler("addv3", add_database_record, filters=filters.ChatType.PRIVATE))
        
        """ Promo """
        self.app.add_handler(CommandHandler("promo", promo_command, filters=filters.ChatType.PRIVATE))
        self.app.add_handler(CallbackQueryHandler(promo_v1_qris, pattern="^promo_v1$"))
        self.app.add_handler(CallbackQueryHandler(promo_host_pilihan_qris, pattern="^promo_host_pilihan$"))
        self.app.add_handler(CallbackQueryHandler(promo_database_record_qris, pattern="^promo_database_record$"))
        self.app.add_handler(CommandHandler("cancel", cancel_command, filters=filters.ChatType.PRIVATE))
        
        
        # callback data
        self.app.add_handler(CallbackQueryHandler(refresh_callback, pattern="^refresh$"))
        self.app.add_handler(CallbackQueryHandler(callback_cancel, pattern="^cancel$"))
        
        # TEMPORARY GROUP BUTTON 1 ORDER
        self.app.add_handler(CallbackQueryHandler(callback_live_temp, pattern="^live_temp_callback"))
        self.app.add_handler(CallbackQueryHandler(callback_live_temp_subscribe, pattern="^live_temp_[0-9]+_[0-9]+_[0-9]+$"))
        self.app.add_handler(CallbackQueryHandler(callback_live_temp_qris, pattern="^price_qris_[0-9]+_[0-9]+$"))
        
        # PERMANENT GROUP BUTTON 2 ORDER
        self.app.add_handler(CallbackQueryHandler(callback_host_pilihan, pattern="^live_perm_v1$"))
        self.app.add_handler(CallbackQueryHandler(callback_host_pilihan_qris, pattern="^host_pilihan$"))
        
        #PERMANENT GROUP BUTTON 3 ORDER
        self.app.add_handler(CallbackQueryHandler(callback_database_record, pattern="^live_perm_v2$"))
        self.app.add_handler(CallbackQueryHandler(callback_database_record_qris, pattern="^database_record$"))

        self.app.add_handler(CallbackQueryHandler(back_callback_handler, pattern="^back_callback$"))
        
        
        """ Join Request """
        self.app.add_handler(ChatJoinRequestHandler(handle_chat_join_request))

    def run(self):
        self.app.run_polling()

bot = TelegramBot()