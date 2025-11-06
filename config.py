import os, pytz

class Config:
    BOT_TOKEN      = os.getenv("BOT_TOKEN", "8202415032:AAF1l_HkN4bmL0YeX1RTIt5EVLMhAKtvxZo")
    CHANNEL_TEMP   = int(os.getenv("CHANNEL_ID", "-1002633596412"))
    CHANNEL_PERM_1 = int(os.getenv("CHANNEL_ID_1", "-1002633596412"))
    CHANNEL_PERM_2 = int(os.getenv("CHANNEL_ID_2", "-1002633596412"))
    CHANNEL_JAV    = int(os.getenv("CHANNEL_JAV", "-1002633596412"))
    CHANNEL_CCTV   = int(os.getenv("CHANNEL_CCTV", "-1002633596412"))
    CHANNEL_INDO   = int(os.getenv("CHANNEL_INDO", "-1002633596412"))
    ADMIN_ID       = [int(id) for id in os.getenv("ADMIN_ID", "692043981,1516420756,7481738979,7830551403").split(",")]
    
    FORCE_SUB_CHANNEL_ID   = int(os.getenv("FORCE_SUB_CHANNEL_ID", "-1002601296115"))
    FORCE_SUB_CHANNEL_NAME = os.getenv("FORCE_SUB_CHANNEL_NAME", "https://t.me/AwwwRelaxKiddo")
    ORDER_KUOTA_USERNAME   = "klmxstore"
    ORDER_KUOTA_AUTHTOKEN  = "1164623:0q3fiSp1Ab6goOjwx7Ple4TXcsrhRuZ5"
    
    MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://raze98fhx:xgM9MDTC4eue333Y@cluster0.nu84e.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    TIMEZONE  = pytz.timezone("Asia/Jakarta")