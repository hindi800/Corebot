import telebot
import qrcode
import io
import os
import json
import random
import string
import urllib.request
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

# ==========================================
# APNI SETTINGS (FORCE JOIN & BULK PACKS SET)
# ==========================================
BOT_TOKEN = "9223716709:AAF1zYFdQ1Wz8fwLDycv4SNZpTedGFzZxQg"
ADMIN_ID = 6657235468
UPI_ID = "shaikhdemon@fam"
PAYEE_NAME = "Premium Digital Store"
SUPPORT_USERNAME = "@rahulst000"
BANNER_IMAGE_URL = "https://graph.org/file/03f6566588ca28e57ea63-03d48d1adf3f4bd0b7.jpg"

# Feature #2: Force Join Channel Settings
FORCE_CHANNEL_USERNAME = "@waterdropkrdo"
FORCE_CHANNEL_LINK = "https://t.me/waterdropkrdo"

# Promo Codes
COUPONS = {
    "WELCOME10": 10,  # ₹10 Off
    "VIP20": 20       # ₹20 Off
}

REFER_BONUS = 10

# Feature #4: Bulk Multi-Video Delivery ('msg_ids' me jitne chaho utne video numbers dalein)
PRODUCTS = {
    "pack1": {
        "name": "🎬 Pack 1 (Starter Demo)",
        "price": 39,
        "validity": "365 Days",
        "color": "success",
        "channel_id": -1004461175417,
        "msg_ids": [2],        # Single Video
        "demo_msg_id": 2,
        "desc": "• Full HD 1080p Quality\n• Anti-Leak Protected Delivery\n• 365 Days Cloud Access"
    },
    "pack2": {
        "name": "🔥 Pack 2 (Pro Bundle)",
        "price": 69,
        "validity": "365 Days",
        "color": "primary",
        "channel_id": -1004461175417,
        "msg_ids": [3],        # Single ya Multiple IDs dal sakte hain (jaise [3, 4])
        "demo_msg_id": 2,
        "desc": "• 4K Ultra HD Collection\n• Fast Direct Telegram File\n• Priority Support Included"
    },
    "pack3": {
        "name": "💎 Pack 3 (VIP All-In-One)",
        "price": 99,
        "validity": "Lifetime",
        "color": "danger",
        "channel_id": -1004461175417,
        "msg_ids": [2, 3, 4],  # Bulk Delivery: Teeno videos ek saath jayenge!
        "demo_msg_id": 2,
        "desc": "• All 3 VIP Videos Combo Pack\n• Regular Free Updates\n• Instant Automated Delivery"
    }
}
# ==========================================

bot = telebot.TeleBot(BOT_TOKEN)
BOT_USERNAME = bot.get_me().username

users_db = {}
active_orders = {}
awaiting_coupon = set()

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"VIP Store Bot (Protected + ForceJoin + Bulk) is Live!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

def get_user(user_id):
    if user_id not in users_db:
        users_db[user_id] = {"wallet": 0, "orders": [], "referred_by": None, "referrals": 0}
    return users_db[user_id]

# Force Join Check Function
def is_user_joined(user_id):
    if user_id == ADMIN_ID:
        return True
    try:
        member = bot.get_chat_member(FORCE_CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print("Force Join Check Error:", e)
        return True  # Agar bot admin nahi hai toh user block na ho

def send_force_join_prompt(chat_id):
    text = (
        "🔒 **ACCESS RESTRICTED!**\n\n"
        "Store kholne aur packs dekhne ke liye pehle hamara **Official Updates Channel** join karein.\n\n"
        "👇 Niche button se channel join karein aur phir **'I Have Joined'** par click karein:"
    )
    buttons = [
        [{"text": "📢 Join Official Channel", "url": FORCE_CHANNEL_LINK, "style": "primary"}],
        [{"text": "✅ I Have Joined", "callback_data": "verify_join", "style": "success"}]
    ]
    send_colored_message(chat_id, text, buttons)

# Colorful Buttons Helper
def send_colored_message(chat_id, text, buttons_rows, photo=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{'sendPhoto' if photo else 'sendMessage'}"
    payload = {
        "chat_id": chat_id,
        "parse_mode": "Markdown",
        "reply_markup": {"inline_keyboard": buttons_rows}
    }
    if photo:
        payload["photo"] = photo
        payload["caption"] = text
    else:
        payload["text"] = text

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    try:
        urllib.request.urlopen(req)
    except Exception as e:
        print("API Error:", e)

def generate_order_id():
    return "TRX" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def generate_upi_qr(amount, note):
    upi_url = f"upi://pay?pa={UPI_ID}&pn={PAYEE_NAME}&am={amount}&cu=INR&tn={note}"
    qr = qrcode.make(upi_url)
    bio = io.BytesIO()
    bio.name = 'qr.png'
    qr.save(bio, 'PNG')
    bio.seek(0)
    return bio

# 1. START COMMAND + REFERRAL + FORCE JOIN
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    is_new = user_id not in users_db
    user = get_user(user_id)
    
    parts = message.text.split()
    if is_new and len(parts) > 1 and parts[1].startswith("ref_"):
        try:
            ref_id = int(parts[1].replace("ref_", ""))
            if ref_id != user_id and ref_id in users_db:
                user["referred_by"] = ref_id
                users_db[ref_id]["wallet"] += REFER_BONUS
                users_db[ref_id]["referrals"] += 1
                bot.send_message(ref_id, f"🎉 **Referral Bonus!** Aapke link se ek naya user join hua hai. Aapke wallet me **₹{REFER_BONUS}** add ho gaye!", parse_mode="Markdown")
        except:
            pass

    if not is_user_joined(user_id):
        send_force_join_prompt(message.chat.id)
        return

    show_main_menu(message.chat.id, message.from_user.first_name or "User", user_id)

def show_main_menu(chat_id, first_name, user_id):
    user = get_user(user_id)
    buttons = []
    for key, item in PRODUCTS.items():
        video_count = len(item['msg_ids'])
        badge = f"({video_count} Videos)" if video_count > 1 else ""
        buttons.append([{
            "text": f"{item['name']} {badge} • ₹{item['price']}",
            "callback_data": f"view_{key}",
            "style": item['color']
        }])
    
    buttons.append([
        {"text": "👤 My Profile & Orders", "callback_data": "my_profile", "style": "primary"},
        {"text": "🎁 Refer & Earn", "callback_data": "refer_earn", "style": "success"}
    ])
    buttons.append([
        {"text": "📖 How to Buy", "callback_data": "how_to_use", "style": "primary"},
        {"text": "💬 Support", "url": f"https://t.me/{SUPPORT_USERNAME.replace('@', '')}", "style": "danger"}
    ])
    
    caption = (
        f"🌟 **WELCOME TO OUR VIP DIGITAL STORE** 🌟\n\n"
        f"👋 Hello **{first_name}**!\n"
        f"💰 **Wallet Balance:** ₹{user['wallet']}\n\n"
        f"✨ **Why Choose Us?**\n"
        f"┣ ⚡ Instant Auto-Delivery System\n"
        f"┣ 🎥 1080p / 4K Original Quality\n"
        f"┗ 🛡️ 100% Trusted & Verified Store\n\n"
        f"👇 **Niche apna pasandida pack select karein:**"
    )
    send_colored_message(chat_id, caption, buttons, photo=BANNER_IMAGE_URL)

# Verify Join Callback
@bot.callback_query_handler(func=lambda call: call.data == "verify_join")
def verify_join(call):
    user_id = call.from_user.id
    if is_user_joined(user_id):
        bot.answer_callback_query(call.id, "✅ Verified! Welcome to the Store.")
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        show_main_menu(call.message.chat.id, call.from_user.first_name or "User", user_id)
    else:
        bot.answer_callback_query(call.id, "❌ Aapne abhi tak channel join nahi kiya hai! Pehle Join dabayein.", show_alert=True)

# 2. MY PROFILE & ORDERS
@bot.callback_query_handler(func=lambda call: call.data == "my_profile")
def show_profile(call):
    bot.answer_callback_query(call.id)
    user = get_user(call.from_user.id)
    orders_text = "\n".join([f"✅ {o}" for o in user["orders"]]) if user["orders"] else "Abhi tak koi order nahi hai."
    
    text = (
        f"👤 **YOUR VIP PROFILE**\n\n"
        f"🆔 **User ID:** `{call.from_user.id}`\n"
        f"💰 **Wallet Balance:** ₹{user['wallet']}\n"
        f"👥 **Total Referrals:** {user['referrals']}\n\n"
        f"📦 **Purchased Packs:**\n{orders_text}"
    )
    buttons = [[{"text": "⬅️ Back to Store", "callback_data": "back_home", "style": "danger"}]]
    send_colored_message(call.message.chat.id, text, buttons)

# 3. REFER & EARN
@bot.callback_query_handler(func=lambda call: call.data == "refer_earn")
def show_refer(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    user = get_user(user_id)
    ref_link = f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"
    
    text = (
        f"🎁 **REFER & EARN FREE PACKS!**\n\n"
        f"Apne doston ko apna referral link share karein. Har join par aapko **₹{REFER_BONUS}** wallet balance milega!\n\n"
        f"💰 **Your Wallet:** ₹{user['wallet']}\n"
        f"🔗 **Your Referral Link:**\n`{ref_link}`\n\n"
        f"*(Link par tap karke copy karein aur share karein)*"
    )
    buttons = [[{"text": "⬅️ Back to Store", "callback_data": "back_home", "style": "danger"}]]
    send_colored_message(call.message.chat.id, text, buttons)

# 4. HOW TO USE
@bot.callback_query_handler(func=lambda call: call.data == "how_to_use")
def show_guide(call):
    bot.answer_callback_query(call.id)
    guide_text = (
        "📖 **STORE KAISE USE KAREIN?**\n\n"
        "1️⃣ Koi bhi pack select karein (aap **Free Demo** bhi dekh sakte hain).\n"
        "2️⃣ **Buy Now** par click karein — agar aapke paas Coupon Code hai toh apply karein.\n"
        "3️⃣ Screen par aaye UPI QR code ko kisi bhi UPI app se scan karke pay karein.\n"
        "4️⃣ Payment ka **Screenshot** yahan bhej dein.\n"
        "5️⃣ Verify hote hi video(s) aapko direct chat me mil jayenge!"
    )
    buttons = [[{"text": "⬅️ Back to Store", "callback_data": "back_home", "style": "danger"}]]
    send_colored_message(call.message.chat.id, guide_text, buttons)

# 5. PACK DETAILS + FREE DEMO PREVIEW
@bot.callback_query_handler(func=lambda call: call.data.startswith("view_"))
def view_pack(call):
    if not is_user_joined(call.from_user.id):
        bot.answer_callback_query(call.id, "Pehle channel join karein!")
        send_force_join_prompt(call.message.chat.id)
        return

    bot.answer_callback_query(call.id)
    prod_key = call.data.split("_", 1)[1]
    product = PRODUCTS[prod_key]
    total_vids = len(product['msg_ids'])
    
    text = (
        f"🔥 **{product['name']}**\n\n"
        f"💰 **Price:** ₹{product['price']}\n"
        f"🎬 **Total Videos:** {total_vids} Video(s)\n"
        f"⏳ **Validity:** {product['validity']}\n"
        f"🎁 **Active Coupons:** `WELCOME10` (₹10 Off)\n\n"
        f"📋 **Included Features:**\n{product['desc']}\n\n"
        f"👇 **Niche se Demo dekhein ya Buy Now par click karein:**"
    )
    buttons = [
        [{"text": f"✔️ Buy Now (₹{product['price']})", "callback_data": f"buy_{prod_key}_0", "style": "success"}],
        [{"text": "🎥 Watch Free Demo", "callback_data": f"demo_{prod_key}", "style": "primary"}],
        [{"text": "⬅️ Back", "callback_data": "back_home", "style": "danger"}]
    ]
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    send_colored_message(call.message.chat.id, text, buttons)

# Free Demo Handler
@bot.callback_query_handler(func=lambda call: call.data.startswith("demo_"))
def send_demo(call):
    bot.answer_callback_query(call.id, "Sending Free Demo...")
    prod_key = call.data.split("_", 1)[1]
    product = PRODUCTS[prod_key]
    try:
        bot.copy_message(chat_id=call.from_user.id, from_chat_id=product['channel_id'], message_id=product['demo_msg_id'])
        bot.send_message(call.from_user.id, f"👆 Ye **{product['name']}** ka free sample hai. Full pack ke liye upar **Buy Now** dabayein!", parse_mode="Markdown")
    except Exception as e:
        bot.send_message(call.from_user.id, "⚠️ Demo abhi update ho raha hai, aap direct Buy Now kar sakte hain.")

# 6. PAYMENT QR PAGE
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def handle_buy(call):
    bot.answer_callback_query(call.id)
    _, prod_key, extra_disc = call.data.split("_")
    extra_disc = int(extra_disc)
    product = PRODUCTS[prod_key]
    user_id = call.from_user.id
    user = get_user(user_id)
    
    wallet_used = min(user["wallet"], max(0, product["price"] - extra_disc - 10))
    total_disc = extra_disc + wallet_used
    final_price = max(10, product["price"] - total_disc)
    
    order_id = generate_order_id()
    active_orders[user_id] = {
        "prod_key": prod_key,
        "order_id": order_id,
        "final_price": final_price,
        "wallet_used": wallet_used
    }
    
    qr_image = generate_upi_qr(final_price, order_id)
    
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
        
    caption = (
        f"💳 **SCAN & PAY (10 MIN VALID)**\n\n"
        f"📦 **Plan:** {product['name']}\n"
        f"💵 **Original Price:** ₹{product['price']}\n"
        f"🎁 **Discount + Wallet:** -₹{total_disc}\n"
        f"💰 **Final Payable:** **₹{final_price}.00**\n"
        f"🏦 **UPI ID:** `{UPI_ID}`\n"
        f"🆔 **Order ID:** `{order_id}`\n\n"
        f"📲 QR scan karein — **₹{final_price}** automatic bhar jayega."
    )
    
    bot.send_photo(call.message.chat.id, qr_image, caption=caption, parse_mode="Markdown")
    
    buttons = [
        [{"text": "📸 Send Payment Screenshot", "callback_data": "send_ss", "style": "success"}],
        [{"text": "🎟️ Apply Promo Code", "callback_data": f"coupon_{prod_key}", "style": "primary"}],
        [{"text": "❌ Cancel Order", "callback_data": "back_home", "style": "danger"}]
    ]
    send_colored_message(call.message.chat.id, "👇 **Payment karne ke baad screenshot bhejein ya Coupon lagayein:**", buttons)

@bot.callback_query_handler(func=lambda call: call.data.startswith("coupon_"))
def ask_coupon(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    awaiting_coupon.add(user_id)
    bot.send_message(user_id, "🎟️ Apna **Promo Code** likh kar bhejein (jaise `WELCOME10`):", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.from_user.id in awaiting_coupon)
def apply_coupon(message):
    user_id = message.from_user.id
    awaiting_coupon.remove(user_id)
    code = message.text.strip().upper()
    
    if code in COUPONS and user_id in active_orders:
        disc = COUPONS[code]
        prod_key = active_orders[user_id]["prod_key"]
        bot.reply_to(message, f"🎉 Coupon **`{code}`** applied! Aapko **₹{disc} Extra Discount** mila hai. Naya QR ban raha hai...", parse_mode="Markdown")
        
        class FakeCall:
            def __init__(self, uid, cid, mid, data):
                self.id = "0"
                self.from_user = type('obj', (object,), {'id': uid})
                self.message = type('obj', (object,), {'chat': type('obj', (object,), {'id': cid}), 'message_id': mid})
                self.data = data
        handle_buy(FakeCall(user_id, message.chat.id, message.message_id, f"buy_{prod_key}_{disc}"))
    else:
        bot.reply_to(message, "❌ Invalid Promo Code! Aap upar wale QR se payment continue kar sakte hain.")

@bot.callback_query_handler(func=lambda call: call.data == "back_home")
def go_back(call):
    bot.answer_callback_query(call.id)
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    show_main_menu(call.message.chat.id, call.from_user.first_name or "User", call.from_user.id)

@bot.callback_query_handler(func=lambda call: call.data == "send_ss")
def ask_ss(call):
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        "📸 **KINDLY SEND YOUR PAYMENT SCREENSHOT**\n\n⚡ Make sure screenshot me **Amount** aur **UPI Ref / UTR Number** saaf dikh raha ho.",
        parse_mode="Markdown"
    )

# 7. SCREENSHOT RECEIVE & ADMIN APPROVAL
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    if user_id not in active_orders:
        bot.reply_to(message, "⚠️ Pehle /start dabakar koi pack select karein.")
        return

    order = active_orders[user_id]
    product = PRODUCTS[order["prod_key"]]
    
    bot.reply_to(message, f"⏳ **Order `{order['order_id']}` Verification Pending...**\n\nAdmin aapka screenshot check kar rahe hain. 1-2 minute me video mil jayega!", parse_mode="Markdown")
    
    bot.send_photo(
        ADMIN_ID,
        message.photo[-1].file_id,
        caption=(
            f"🔔 **NEW PAYMENT RECEIVED!**\n\n"
            f"🆔 **Order ID:** `{order['order_id']}`\n"
            f"👤 **User:** {message.from_user.first_name} (`{user_id}`)\n"
            f"📦 **Pack:** {product['name']}\n"
            f"💰 **Paid Amount:** ₹{order['final_price']}"
        ),
        parse_mode="Markdown"
    )
    
    admin_buttons = [[
        {"text": "✅ Approve & Send Videos", "callback_data": f"app_{user_id}_{order['prod_key']}", "style": "success"},
        {"text": "❌ Reject", "callback_data": f"rej_{user_id}", "style": "danger"}
    ]]
    send_colored_message(ADMIN_ID, f"⚡ Action for Order `{order['order_id']}`:", admin_buttons)

# 8. ADMIN APPROVE (BULK DELIVERY + ANTI-FORWARD PROTECTION)
@bot.callback_query_handler(func=lambda call: call.data.startswith("app_"))
def approve_order(call):
    bot.answer_callback_query(call.id, "Approved! Sending protected videos...")
    _, user_id, prod_key = call.data.split("_", 2)
    user_id = int(user_id)
    product = PRODUCTS[prod_key]
    user = get_user(user_id)
    
    if user_id in active_orders:
        used = active_orders[user_id].get("wallet_used", 0)
        user["wallet"] = max(0, user["wallet"] - used)
    user["orders"].append(product["name"])
    
    try:
        # Feature #1 (protect_content=True) + Feature #4 (Loop for Bulk Videos)
        for msg_id in product['msg_ids']:
            bot.copy_message(
                chat_id=user_id,
                from_chat_id=product['channel_id'],
                message_id=msg_id,
                protect_content=True  # Anti-Forward & Anti-Save Lock!
            )
        bot.send_message(
            user_id,
            f"🎉 **PAYMENT APPROVED!**\n\nUpar aapke **{product['name']}** ke saare videos ({len(product['msg_ids'])}) bhej diye gaye hain. Enjoy karein!",
            parse_mode="Markdown"
        )
        bot.edit_message_text("✅ **Order Approved & Protected Videos Delivered!**", call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Error sending video: {e}\n(Check karein ki bot storage channel me Admin hai ya nahi)")

@bot.callback_query_handler(func=lambda call: call.data.startswith("rej_"))
def reject_order(call):
    bot.answer_callback_query(call.id, "Rejected!")
    user_id = int(call.data.split("_")[1])
    bot.send_message(user_id, "❌ **Payment Rejected!**\n\nAapka screenshot verify nahi ho paya. Kripya sahi payment screenshot bhejein ya Support se baat karein.", parse_mode="Markdown")
    bot.edit_message_text("❌ **Order Rejected!**", call.message.chat.id, call.message.message_id, parse_mode="Markdown")

# 9. ADMIN STATS & BROADCAST
@bot.message_handler(commands=['users'])
def total_users(message):
    if message.from_user.id == ADMIN_ID:
        total_orders = sum(len(u["orders"]) for u in users_db.values())
        bot.reply_to(message, f"📊 **STORE ANALYTICS**\n\n👥 **Total Users:** {len(users_db)}\n📦 **Completed Orders:** {total_orders}", parse_mode="Markdown")

@bot.message_handler(commands=['broadcast'])
def broadcast_msg(message):
    if message.from_user.id == ADMIN_ID:
        msg_text = message.text.replace("/broadcast", "").strip()
        if not msg_text:
            bot.reply_to(message, "Use: `/broadcast Naya VIP Pack aa gaya hai! Abhi /start dabayein.`", parse_mode="Markdown")
            return
        count = 0
        for uid in users_db:
            try:
                bot.send_message(uid, f"📢 **NEW UPDATE**\n\n{msg_text}", parse_mode="Markdown")
                count += 1
            except:
                pass
        bot.reply_to(message, f"✅ Broadcast {count} users ko bhej diya gaya!")

if __name__ == "__main__":
    Thread(target=run_web_server).start()
    print("VIP Store Bot (Protected + ForceJoin + Bulk) Live Hai...")
    bot.infinity_polling()
