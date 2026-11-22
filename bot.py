import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import qrcode
import io
import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

# ==========================================
# AAPKI COMPLETE DETAILS SET HAIN
# ==========================================
BOT_TOKEN = "9223716709:AAF1zYFdQ1Wz8fwLDycv4SNZpTedGFzZxQg"
ADMIN_ID = 6657235468
UPI_ID = "shaikhdemon@fam"
PAYEE_NAME = "Digital Store"

# Aapke 3 Videos / Packs Set Hain
PRODUCTS = {
    "pack1": {
        "name": "🎬 Pack 1 (Demo)",
        "price": 39,
        "channel_id": -1004461175417,
        "msg_id": 2
    },
    "pack2": {
        "name": "🔥 Pack 2 (Standard)",
        "price": 69,
        "channel_id": -1004461175417,
        "msg_id": 3
    },
    "pack3": {
        "name": "💎 Pack 3 (Full VIP)",
        "price": 99,
        "channel_id": -1004461175417,
        "msg_id": 4
    }
}
# ==========================================

bot = telebot.TeleBot(BOT_TOKEN)
user_orders = {}

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running 24/7!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

def generate_upi_qr(amount, note):
    upi_url = f"upi://pay?pa={UPI_ID}&pn={PAYEE_NAME}&am={amount}&cu=INR&tn={note}"
    qr = qrcode.make(upi_url)
    bio = io.BytesIO()
    bio.name = 'qr.png'
    qr.save(bio, 'PNG')
    bio.seek(0)
    return bio

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    for key, item in PRODUCTS.items():
        btn = InlineKeyboardButton(f"{item['name']} - ₹{item['price']}", callback_data=f"buy_{key}")
        markup.add(btn)
    
    bot.send_message(
        message.chat.id,
        "🌟 **WELCOME TO OUR DIGITAL STORE** 🌟\n\nNiche diye gaye packs me se apna pack select karein:",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def handle_buy(call):
    prod_key = call.data.split("_", 1)[1]
    product = PRODUCTS[prod_key]
    user_id = call.from_user.id
    user_orders[user_id] = prod_key
    
    qr_image = generate_upi_qr(product['price'], f"Order_{user_id}")
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ Payment Kar Diya (Send Screenshot)", callback_data="send_ss"))
    markup.add(InlineKeyboardButton("🔙 Back", callback_data="go_back"))
    
    caption = (
        f"🛒 **Selected:** {product['name']}\n"
        f"💰 **Amount:** ₹{product['price']}\n\n"
        f"📲 Is QR code ko kisi bhi UPI app se scan karein. Exact amount automatic fill ho jayega.\n\n"
        f"Payment karne ke baad niche button dabayein aur screenshot bhejein."
    )
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_photo(call.message.chat.id, qr_image, caption=caption, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "go_back")
def go_back(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    send_welcome(call.message)

@bot.callback_query_handler(func=lambda call: call.data == "send_ss")
def ask_ss(call):
    bot.send_message(call.message.chat.id, "📸 Ab apna **Payment Screenshot** yahan bhejein.", parse_mode="Markdown")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    if user_id not in user_orders:
        bot.reply_to(message, "Pehle /start dabakar koi pack select karein.")
        return

    prod_key = user_orders[user_id]
    product = PRODUCTS[prod_key]
    
    bot.reply_to(message, "⏳ Screenshot mil gaya! Admin verify karte hi aapko video mil jayega.")
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ Approve & Send", callback_data=f"app_{user_id}_{prod_key}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}")
    )
    
    bot.send_photo(
        ADMIN_ID,
        message.photo[-1].file_id,
        caption=f"🔔 **New Payment!**\n👤 User ID: `{user_id}`\n📦 Pack: {product['name']}\n💰 Price: ₹{product['price']}",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("app_"))
def approve_order(call):
    _, user_id, prod_key = call.data.split("_", 2)
    user_id = int(user_id)
    product = PRODUCTS[prod_key]
    
    bot.copy_message(chat_id=user_id, from_chat_id=product['channel_id'], message_id=product['msg_id'])
    bot.send_message(user_id, "🎉 **Payment Approved!** Upar aapka video bhej diya gaya hai.", parse_mode="Markdown")
    bot.edit_message_caption("✅ **Approved & Delivered!**", call.message.chat.id, call.message.message_id, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("rej_"))
def reject_order(call):
    user_id = int(call.data.split("_")[1])
    bot.send_message(user_id, "❌ Aapka screenshot verify nahi ho paya. Kripya sahi screenshot bhejein.")
    bot.edit_message_caption("❌ **Rejected!**", call.message.chat.id, call.message.message_id, parse_mode="Markdown")

if __name__ == "__main__":
    Thread(target=run_web_server).start()
    print("Bot chalu ho gaya hai...")
    bot.infinity_polling()
