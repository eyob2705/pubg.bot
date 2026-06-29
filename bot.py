import telebot
from telebot import types
from flask import Flask
import threading

# ያንተ የቦት ቶከን በትክክል ገብቷል
TOKEN = '8863850090:AAEr6EDdoq2VkHqR2wUHdUGRxTS5C3fG-U'
bot = telebot.TeleBot(TOKEN)

# የፍላስክ አፕሊኬሽን (ለሰርቨሩ)
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run_server():
    app.run(host='0.0.0.0', port=8080)

# ዋናው ማውጫ (Start Command)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton('🎮 የጨዋታ አማራጮች (Match Options)')
    btn2 = types.KeyboardButton('💰 አካውንት ለመሙላት (Deposit)')
    btn3 = types.KeyboardButton('📞 ድጋፍ ለማግኘት (Support)')
    markup.add(btn1, btn2, btn3)
    
    bot.send_message(
        message.chat.id, 
        "👋 እንኳን ወደ PUBG MONEY BOT በደህና መጡ! ከእኛ ጋር በመጫወት ተሸላሚ ይሁኑ። ለመጀመር ከታች ያሉትን ምርጫዎች ይጠቀሙ።", 
        reply_markup=markup
    )

# በተኖችን ማስተናገጃ
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if message.text == '🎮 የጨዋታ አማራጮች (Match Options)':
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_50 = types.InlineKeyboardButton("🕹 የ 50 ብር ጨዋታ (አሸናፊው 90 ብር ያገኛል)", callback_data="match_50")
        btn_100 = types.InlineKeyboardButton("🕹 የ 100 ብር ጨዋታ (አሸናፊው 180 ብር ያገኛል)", callback_data="match_100")
        markup.add(btn_50, btn_100)
        bot.send_message(message.chat.id, "እባክዎ መጫወት የሚፈልጉትን የክፍያ መጠን ይምረጡ፦", reply_markup=markup)
        
    elif message.text == '💰 አካውንት ለመሙላት (Deposit)':
        deposit_text = (
            "▶️ **አካውንት ለመሙላት (Deposit)**\n\n"
            "በሚከተሉት የባንክ አካውንቶች ማስገባት ይችላሉ፦\n\n"
            "▫️ **የኢትዮጵያ ንግድ ባንክ (CBE):** `1000505254663`\n"
            "▫️ **ቴሌብር (telebirr):** `0904874443`\n\n"
            "⚠️ **ማсаሰቢያ:** ብሩን ካስገቡ በኋላ የደረሰኝ ስክሪንሾት (Screenshot) ለዋናው አድሚን በ '📞 ድጋፍ ለማግኘት' በኩል መላክዎን እንዳይረሱ።"
        )
        bot.send_message(message.chat.id, deposit_text, parse_mode="Markdown")
        
    elif message.text == '📞 ድጋፍ ለማግኘት (Support)':
        bot.send_message(
            message.chat.id, 
            "ማንኛውንም ጥያቄ ለመጠየቅ ወይም የክፍያ ደረሰኝ ለመላክ ዋናውን አድሚን በስልክ ቁጥር ማነጋገር ይችላሉ፦\n👉 0904874443"
        )

# የውስጥ በተኖች ሲነኩ (Callback query)
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "match_50":
        bot.send_message(call.message.chat.id, "✅ የ 50 ብር ጨዋታ መርጠዋል። ለመመዝገብና የክፍል መለያ (Room ID) ለመቀበል የክፍያ ደረሰኝዎን በ 'Support' በኩል ይላኩ።")
    elif call.data == "match_100":
        bot.send_message(call.message.chat.id, "✅ የ 100 ብር ጨዋታ መርጠዋል። ለመመዝገብና የክፍል መለያ (Room ID) ለመቀበል የክፍያ ደረሰኝዎን በ 'Support' በኩል ይላኩ።")

if __name__ == "__main__":
    # ሰርቨሩን በሌላ ትሬድ ማስጀመር
    t = threading.Thread(target=run_server)
    t.start()
    # ቦቱን ማስነሳት
    bot.polling(none_stop=True)
