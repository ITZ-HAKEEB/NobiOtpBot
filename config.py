import os

# Telegram API Credentials
API_ID = int(os.environ.get("API_ID", "123456"))
API_HASH = os.environ.get("API_HASH", "your_api_hash")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token")

# Database
MONGO_URI = os.environ.get("MONGO_URI", "your_mongodb_connection_string")

# Owner Settings
OWNER_ID = int(os.environ.get("OWNER_ID", "123456789"))
OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "your_username")
SUPPORT_USERNAME = os.environ.get("SUPPORT_USERNAME", "your_support_username")

# Payment Settings (QR Image & UPI ID inside Config)
UPI_ID = os.environ.get("UPI_ID", "your_upi_id@paytm")
QR_IMAGE_URL = os.environ.get("QR_IMAGE_URL", "https://envs.sh/QR.jpg")

# Force Subscribe Channel Settings
FORCE_CHANNEL_USERNAME = os.environ.get("FORCE_CHANNEL_USERNAME", "OTPMasterUpdates")
FORCE_CHANNEL_INVITE_LINK = os.environ.get("FORCE_CHANNEL_INVITE_LINK", "https://t.me/OTPMasterUpdates")
