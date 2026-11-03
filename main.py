import asyncio
import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from pyrogram.errors import UserNotParticipant
from telethon import TelegramClient
from telethon.sessions import StringSession
import config
import database as db

app = Client(
    "NobiNumberBot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN
)

def get_country_from_phone(phone: str):
    if phone.startswith("+91") or phone.startswith("91"):
        return "🇮🇳 India (+91)"
    elif phone.startswith("+1") or phone.startswith("1"):
        return "🇺🇸 USA (+1)"
    elif phone.startswith("+880") or phone.startswith("880"):
        return "🇧🇩 Bangladesh (+880)"
    elif phone.startswith("+95") or phone.startswith("95"):
        return "🇲🇲 Myanmar (+95)"
    elif phone.startswith("+66") or phone.startswith("66"):
        return "🇹🇭 Thailand (+66)"
    else:
        match = re.match(r"^\+?(\d{1,4})", phone)
        code = match.group(1) if match else "Unknown"
        return f"🌐 International (+{code})"

async def check_force_sub(client, user_id):
    if not config.FORCE_CHANNEL_USERNAME:
        return True
    try:
        member = await client.get_chat_member(config.FORCE_CHANNEL_USERNAME, user_id)
        if member.status in ["left", "kicked"]:
            return False
        return True
    except UserNotParticipant:
        return False
    except Exception:
        return True

@app.on_message(filters.command("start"))
async def start_handler(client, message: Message):
    user_id = message.from_user.id
    
    is_joined = await check_force_sub(client, user_id)
    if not is_joined:
        join_text = (
            "🚀 **Join Our Channels First**\n\n"
            "📢 To use this bot, you must join our official channels.\n"
            "👉 Get updates, new features and support.\n"
            "✅ Join all channels and then tap **Verify Join**."
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Join Channel", url=config.FORCE_CHANNEL_INVITE_LINK)],
            [InlineKeyboardButton("✅ Verify Join", callback_data="verify_join")]
        ])
        await message.reply_text(join_text, reply_markup=buttons)
        return

    user = await db.get_user(user_id)
    
    if not user.get("terms_accepted", False):
        terms_text = (
            "<b>👋 WELCOME 🤲 ||</b>\n\n"
            "One last step before premium access\n\n"
            "🎉 <b>Human verification passed!</b>\n"
            "To unlock all premium features, please review and accept our policies.\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "By tapping ✅ <b>Yes, I Agree</b> you confirm:\n"
            "• You are 18+ and accept all terms\n"
            "• No refunds after account delivery\n"
            "• No chargebacks — instant permanent ban\n"
            "• Accounts for lawful personal use only\n"
            "• Supplier details remain confidential\n\n"
            "<i>Tap any policy below to read the full text, then agree.</i>"
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📜 User Agreement", callback_data="terms_info")],
            [InlineKeyboardButton("⚠️ Disclaimer", callback_data="terms_info")],
            [InlineKeyboardButton("📋 Terms & Conditions", callback_data="terms_info")],
            [InlineKeyboardButton("✅ Yes, I Agree", callback_data="accept_terms")]
        ])
        await message.reply_text(terms_text, reply_markup=buttons)
        return

    await show_main_menu(message)

@app.on_callback_query(filters.regex("verify_join"))
async def verify_join_cb(client, callback: CallbackQuery):
    user_id = callback.from_user.id
    is_joined = await check_force_sub(client, user_id)
    if not is_joined:
        await callback.answer("❌ You have not joined the channel yet! Please join first.", show_alert=True)
        return
    
    await callback.answer("✅ Verification Successful!", show_alert=True)
    user = await db.get_user(user_id)
    if not user.get("terms_accepted", False):
        terms_text = "<b>👋 WELCOME 🤲 ||</b>\n\nTap ✅ <b>Yes, I Agree</b> to continue."
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Yes, I Agree", callback_data="accept_terms")]
        ])
        await callback.message.edit_text(terms_text, reply_markup=buttons)
    else:
        await show_main_menu(callback, edit=True)

async def show_main_menu(message_or_callback, edit=False):
    user = message_or_callback.from_user
    user_id = user.id
    db_user = await db.get_user(user_id)
    balance = db_user.get("balance", 0.0)
    
    me = await app.get_me()
    current_bot_name = me.first_name
    
    full_name = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
    username_str = f"@{user.username}" if user.username else f"ID: {user_id}"

    text = (
        f"👋 Hi ~ {full_name} ({username_str}) = xD 🌿 / <3,\n\n"
        f"💎 **Welcome to {current_bot_name}** 🏪\n"
        f"Premium Digital Services & Assets.\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 {user_id}\n"
        f"💰 Your Wallet: ₹{balance}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⚡ Instant Delivery\n"
        f"🔒 Secure Payments\n\n"
        f"👇 Select an option:"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 Telegram Accounts", callback_data="buy_telegram_accounts")],
        [InlineKeyboardButton("💰 My Wallet", callback_data="my_wallet"), InlineKeyboardButton("➕ Deposit", callback_data="deposit_menu")],
        [InlineKeyboardButton("📦 My Orders", callback_data="my_orders"), InlineKeyboardButton("📢 Sales", callback_data="sales_info")],
        [InlineKeyboardButton("🆘 Support", url=f"https://t.me/{config.SUPPORT_USERNAME}")],
        [InlineKeyboardButton("📖 How to Use bot 🤖", callback_data="how_to_use")]
    ])
    
    if edit:
        await message_or_callback.edit_message_text(text, reply_markup=keyboard)
    else:
        if isinstance(message_or_callback, CallbackQuery):
            await message_or_callback.message.edit_text(text, reply_markup=keyboard)
        else:
            await message_or_callback.reply_text(text, reply_markup=keyboard)

@app.on_callback_query(filters.regex("accept_terms"))
async def accept_terms_cb(client, callback: CallbackQuery):
    await db.set_terms_accepted(callback.from_user.id)
    await callback.answer("Verified! Accept terms to continue.", show_alert=True)
    await show_main_menu(callback, edit=True)

@app.on_callback_query(filters.regex("terms_info"))
async def terms_info_cb(client, callback: CallbackQuery):
    await callback.answer(
        "Welcome to Nobi Number Store Bot. Here you will get cheapest Telegram numbers & OTP. All country numbers available. No refunds once paid. Must get approved by owner.",
        show_alert=True
    )

@app.on_callback_query(filters.regex("deposit_menu"))
async def deposit_menu_cb(client, callback: CallbackQuery):
    text = (
        f"💳 **Add Funds / Deposit**\n\n"
        f"Scan the QR code below or pay via UPI ID: `{config.UPI_ID}`\n"
        f"Minimum deposit: ₹10\n\n"
        f"After payment, click on 'Send Screenshot' to submit proof."
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 Send Screenshot", callback_data="send_screenshot_prompt")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
    ])
    
    if config.QR_IMAGE_URL:
        await callback.message.reply_photo(photo=config.QR_IMAGE_URL, caption=text, reply_markup=keyboard)
        try:
            await callback.message.delete()
        except Exception:
            pass
    else:
        await callback.message.edit_text(text, reply_markup=keyboard)

@app.on_callback_query(filters.regex("send_screenshot_prompt"))
async def send_screenshot_prompt_cb(client, callback: CallbackQuery):
    await callback.message.reply_text("📸 Please send your payment screenshot image. It will be forwarded to the owner for verification.")
    await callback.answer()

@app.on_message(filters.photo & filters.private)
async def handle_payment_screenshot(client, message: Message):
    user = message.from_user
    forward_text = (
        f"🔔 **New Payment Screenshot Received!**\n\n"
        f"👤 User: {user.mention}\n"
        f"🆔 User ID: <code>{user.id}</code>\n"
        f"🔗 Username: @{user.username if user.username else 'None'}\n\n"
        f"Use command to add balance:\n"
        f"<code>/addbalance {user.id} [amount]</code>"
    )
    await message.forward(config.OWNER_ID)
    await client.send_message(config.OWNER_ID, forward_text)
    await message.reply_text("✅ Your payment screenshot has been sent to the owner. Balance will be added after verification.")

@app.on_callback_query(filters.regex("how_to_use"))
async def how_to_use_cb(client, callback: CallbackQuery):
    guide_text = (
        "📖 **How to Use Bot** 🤖\n\n"
        "1️⃣ **Deposit Funds:** Go to 'Deposit', scan QR or pay via UPI, and send the screenshot. Once approved by the owner, your wallet balance will be credited.\n"
        "2️⃣ **Buy Number:** Go to 'Telegram Accounts', select your desired country and purchase a number.\n"
        "3️⃣ **Get OTP:** Login with the received number in Telegram. When the OTP prompt appears, click the **'Get OTP'** button in the bot.\n"
        "4️⃣ **2FA Password:** If two-step verification is enabled, the password will also be provided.\n\n"
        "⚠️ For any support, click the Support button."
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
    ])
    await callback.message.edit_text(guide_text, reply_markup=keyboard)

@app.on_callback_query(filters.regex("my_wallet"))
async def my_wallet_cb(client, callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    text = f"💰 **Your Wallet Balance:** ₹{user.get('balance', 0.0)}"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Deposit", callback_data="deposit_menu")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard)

@app.on_callback_query(filters.regex("my_orders"))
async def my_orders_cb(client, callback: CallbackQuery):
    text = "📦 **Your Orders History:**\n\nYour purchased numbers will appear here."
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard)

@app.on_callback_query(filters.regex("sales_info"))
async def sales_info_cb(client, callback: CallbackQuery):
    text = "📢 **Sales & Offers Info:**\n\nStay tuned with our official channel for all updates and offers."
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard)

# Admin Panel Command
@app.on_message(filters.command("admin") & filters.user(config.OWNER_ID))
async def admin_panel_cmd(client, message: Message):
    admin_text = (
        "🛠 **Admin Control Panel** 🛠\n\n"
        "Welcome to the admin panel. Here are your available commands:\n\n"
        "1️⃣ `/addnumber` - Add a new number, session and set its price.\n"
        "2️⃣ `/addbalance <user_id> <amount>` - Add balance to user wallet.\n"
        "3️⃣ `/rmbalance <user_id> <amount>` - Remove balance from user wallet.\n\n"
        "Use these commands carefully to manage your store!"
    )
    await message.reply_text(admin_text)

@app.on_message(filters.command("addbalance") & filters.user(config.OWNER_ID))
async def add_balance_cmd(client, message: Message):
    args = message.command
    if len(args) < 3:
        await message.reply_text("Usage: `/addbalance <user_id> <amount>`")
        return
    target = int(args[1])
    amount = float(args[2])
    await db.update_balance(target, amount)
    await message.reply_text(f"✅ Successfully added ₹{amount} to User ID `{target}`.")

@app.on_message(filters.command("rmbalance") & filters.user(config.OWNER_ID))
async def remove_balance_cmd(client, message: Message):
    args = message.command
    if len(args) < 3:
        await message.reply_text("Usage: `/rmbalance <user_id> <amount>`")
        return
    target = int(args[1])
    amount = float(args[2])
    await db.update_balance(target, -amount)
    await message.reply_text(f"✅ Successfully removed ₹{amount} from User ID `{target}`.")

# Add Number Flow with Price Setting
add_number_state = {}

@app.on_message(filters.command("addnumber") & filters.user(config.OWNER_ID))
async def add_number_cmd(client, message: Message):
    add_number_state[message.from_user.id] = {"step": "waiting_number"}
    await message.reply_text("📱 Please send phone number with country code (e.g. `+919876543210`):")

@app.on_message(filters.private & filters.user(config.OWNER_ID))
async def owner_text_handler(client, message: Message):
    user_id = message.from_user.id
    if user_id in add_number_state:
        state = add_number_state[user_id]
        if state["step"] == "waiting_number":
            phone = message.text.strip()
            state["phone"] = phone
            state["step"] = "waiting_session"
            await message.reply_text("🔑 Now send the **Telethon String Session** for this number:")
        elif state["step"] == "waiting_session":
            state["session"] = message.text.strip()
            state["step"] = "waiting_price"
            await message.reply_text("💵 Now enter the **Price** for this number (e.g. `35` or `50`):")
        elif state["step"] == "waiting_price":
            try:
                price = float(message.text.strip())
            except ValueError:
                await message.reply_text("❌ Invalid price! Please enter a valid number (e.g. 35):")
                return
            
            phone = state["phone"]
            session_str = state["session"]
            country = get_country_from_phone(phone)
            
            await db.numbers_col.insert_one({
                "phone": phone,
                "session": session_str,
                "country": country,
                "price": price,
                "status": "available"
            })
            del add_number_state[user_id]
            await message.reply_text(f"✅ Service added successfully!\nCountry: {country}\nPrice: ₹{price}")

@app.on_callback_query(filters.regex("buy_telegram_accounts"))
async def buy_accounts_cb(client, callback: CallbackQuery):
    cursor = db.numbers_col.find({"status": "available"})
    available_numbers = await cursor.to_list(length=100)
    
    if not available_numbers:
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]])
        await callback.message.edit_text("❌ No numbers available right now!", reply_markup=keyboard)
        return
    
    keyboard = []
    for num in available_numbers:
        # Hide full phone number, show only Flag, Country Name and Price (e.g. 🇮🇳 India (+91) - ₹35)
        price = num.get("price", 50.0)
        btn_text = f"🛒 {num['country']} - ₹{price}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"buy_num_{num['phone']}")])
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
    
    await callback.message.edit_text("🌍 **Select Country & Price:**", reply_markup=InlineKeyboardMarkup(keyboard))

@app.on_callback_query(filters.regex("^buy_num_"))
async def process_buy_number(client, callback: CallbackQuery):
    phone = callback.data.replace("buy_num_", "")
    user_id = callback.from_user.id
    
    num_doc = await db.numbers_col.find_one({"phone": phone, "status": "available"})
    if not num_doc:
        await callback.answer("Sorry, this number is already sold or unavailable.", show_alert=True)
        return
    
    price = num_doc.get("price", 50.0)
    user = await db.get_user(user_id)
    
    if user["balance"] < price:
        await callback.answer(f"❌ Insufficient balance! Required: ₹{price}", show_alert=True)
        return
    
    await db.update_balance(user_id, -price)
    updated_num = await db.numbers_col.find_one_and_update(
        {"phone": phone, "status": "available"},
        {"$set": {"status": "sold", "buyer_id": user_id}}
    )
    
    if not updated_num:
        await callback.answer("Sorry, this number is already sold.", show_alert=True)
        return
    
    text = (
        f"🎉 **Number Purchased Successfully!**\n\n"
        f"📱 Number: `+{phone}`\n"
        f"🌍 Country: {num_doc['country']}\n"
        f"💰 Price Paid: ₹{price}\n\n"
        f"⚠️ **Please Fast Login This Account!**\n"
        f"When you enter the number in Telegram and receive the OTP, click the button below."
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📩 Get OTP", callback_data=f"getotp_{phone}"),
         InlineKeyboardButton("❌ Cancel Order", callback_data=f"cancel_ord_{phone}")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@app.on_callback_query(filters.regex("^getotp_"))
async def get_otp_cb(client, callback: CallbackQuery):
    phone = callback.data.replace("getotp_", "")
    num_doc = await db.numbers_col.find_one({"phone": phone})
    
    if not num_doc or not num_doc.get("session"):
        await callback.answer("Session not found.", show_alert=True)
        return
    
    await callback.answer("🔄 Fetching OTP, please wait...", show_alert=True)
    
    try:
        tclient = TelegramClient(StringSession(num_doc['session']), config.API_ID, config.API_HASH)
        await tclient.connect()
        
        messages = await tclient.get_messages(777000, limit=1)
        otp_text = messages[0].text if messages else "No OTP received yet."
        
        password_status = "Not Enabled"
        try:
            pw = await tclient.get_password()
            if pw and pw.has_password:
                password_status = "Enabled / Set"
        except Exception:
            pass
            
        await tclient.disconnect()
        
        result_text = (
            f"🔐 **OTP Details for +{phone}**\n\n"
            f"📥 **Message / OTP:**\n<code>{otp_text}</code>\n\n"
            f"🔒 **2FA Password:** {password_status}"
        )
        await callback.message.reply_text(result_text)
    except Exception as e:
        await callback.message.reply_text(f"❌ Error fetching OTP: `{str(e)}`")

@app.on_callback_query(filters.regex("main_menu"))
async def back_to_menu(client, callback: CallbackQuery):
    await show_main_menu(callback, edit=True)

if __name__ == "__main__":
    print("🤖 Nobi Number Store Bot Started Successfully!")
    app.run()
