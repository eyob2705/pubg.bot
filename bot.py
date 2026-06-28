import telebot
import sqlite3
from flask import Flask
from threading import Thread

# 1. የአዲሱ ቦትህ ቶከን 
API_TOKEN = '8863850090:AAEr6EDdoq2VkHqR2wUHdUGRxTSYz2KbnY4'
bot = telebot.TeleBot(API_TOKEN)

# 2. ያንተ የቴሌግራም ID ቁጥር
ADMIN_ID = 1843109355  

user_states = {}

# ----------------- ዳታቤዝ መፍጠር -----------------
def init_db():
    conn = sqlite3.connect('pubg_new_system.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            user_id INTEGER PRIMARY KEY,
            pubg_name TEXT,
            pubg_id TEXT,
            balance INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ----------------- የተጫዋች ተግባራት -----------------

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "🎮 እንኳን ወደ PUBG ውድድር ቦት በሰላም መጡ! 🎮\n\n"
        "እባክዎን ከታች ካሉት ምርጫዎች አንዱን ይጫኑ፦\n"
        "🔹 /register - ለመመዝገብ\n"
        "🔹 /deposit - ብር ለማስገባት\n"
        "🔹 /profile - አካውንትዎን ለማየት\n"
        "🔹 /match - የዛሬውን ጨዋታ ለማየት"
    )
    if message.chat.id == ADMIN_ID:
        welcome_text += "\n\n👑 **የአድሚን ትዕዛዞች:**\n/addmoney - ለተጫዋች ብር ለመጨመር\n/players - የተመዘገቡ ሰዎችን ለማየት"
        
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['register'])
def start_registration(message):
    user_id = message.chat.id
    conn = sqlite3.connect('pubg_new_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        bot.reply_to(message, f"❌ እርስዎ አስቀድመው ተመዝግበዋል!\n🆔 PUBG ID: {user[2]}")
        return
        
    bot.reply_to(message, "📝 መመዝገብ እንጀምር! በመጀመሪያ የ PUBG ስምዎን (In-Game Name) ያስገቡ፦")
    user_states[user_id] = {'step': 'waiting_for_name'}

@bot.message_handler(func=lambda message: message.chat.id in user_states and 'step' in user_states[message.chat.id])
def handle_registration_inputs(message):
    user_id = message.chat.id
    current_step = user_states[user_id]['step']
    
    if current_step == 'waiting_for_name':
        user_states[user_id]['pubg_name'] = message.text
        bot.reply_to(message, "✅ ስምህ ተመዝግቧል። አሁን ደግሞ የ PUBG Character ID ቁጥርህን ብቻ ላክልኝ፦")
        user_states[user_id]['step'] = 'waiting_for_id'
        
    elif current_step == 'waiting_for_id':
        pubg_id = message.text
        if not pubg_id.isdigit():
            bot.reply_to(message, "❌ እባክህ ትክክለኛ ቁጥር ብቻ አስገባ! በድጋሚ ላክልኝ፦")
            return
            
        pubg_name = user_states[user_id]['pubg_name']
        
        conn = sqlite3.connect('pubg_new_system.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO players (user_id, pubg_name, pubg_id, balance) VALUES (?, ?, ?, ?)", 
                       (user_id, pubg_name, pubg_id, 0))
        conn.commit()
        conn.close()
        
        bot.reply_to(message, f"🎉 ምዝገባዎ ተጠናቋል።\n👤 ስም: {pubg_name}\n🆔 ID: {pubg_id}\n💰 ቀሪ ሂሳብ: 0 ETB")
        del user_states[user_id]

@bot.message_handler(commands=['profile'])
def view_profile(message):
    user_id = message.chat.id
    conn = sqlite3.connect('pubg_new_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT pubg_name, pubg_id, balance FROM players WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        bot.reply_to(message, f"👤 የእርስዎ መረጃ፦\n\n🔹 ስም: {user[0]}\n🔹 PUBG ID: {user[1]}\n💰 ቀሪ ሂሳብ: {user[2]} ETB")
    else:
        bot.reply_to(message, "❌ አልተመዘገቡም! /register ይበሉ።")

@bot.message_handler(commands=['deposit'])
def deposit_money(message):
    bot.reply_to(message, "💰 ብር ለማስገባት በቴሌብር 0912345678 ላይ ልከው ማረጋገጫውን (Screenshot) ለአድሚን ይላኩ።")

@bot.message_handler(commands=['match'])
def view_match(message):
    bot.reply_to(message, "🎮 የዛሬው ውድድር መርሃ-ግብር 🎮\n\n📅 ቀን፡ ዛሬ ማታ\n⏰ ሰዓት፡ 3:00 (ምሽት)\n💵 መግቢያ፡ 50 ብር\n🏆 ሽልማት፡ 1000 ብር\n\n(የክፍሉ ID እና Password ጨዋታው ከመጀመሩ 15 ደቂቃ በፊት ይለቀቃል)")

# ----------------- የአድሚን ተግባራት -----------------

@bot.message_handler(commands=['players'])
def list_players(message):
    if message.chat.id != ADMIN_ID: return
    
    conn = sqlite3.connect('pubg_new_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, pubg_name, balance FROM players")
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        bot.reply_to(message, "ምንም የተመዘገበ ተጫዋች የለም።")
        return
        
    reply = "👥 የተመዘገቡ ተጫዋቾች ዝርዝር፦\n\n"
    for row in rows:
        reply += f"🆔 Telegram ID: `{row[0]}`\n👤 ስም: {row[1]}\n💰 ሂሳብ: {row[2]} ETB\n------------------------\n"
    bot.reply_to(message, reply, parse_mode="Markdown")

@bot.message_handler(commands=['addmoney'])
def start_add_money(message):
    if message.chat.id != ADMIN_ID: return
    bot.reply_to(message, "የተጫዋቹን የቴሌግራም ID ቁጥር ያስገቡ፦")
    user_states[message.chat.id] = {'admin_step': 'waiting_for_user_id'}

@bot.message_handler(func=lambda message: message.chat.id in user_states and 'admin_step' in user_states[message.chat.id])
def handle_admin_inputs(message):
    admin_id = message.chat.id
    step = user_states[admin_id]['admin_step']
    
    if step == 'waiting_for_user_id':
        if not message.text.isdigit():
            bot.reply_to(message, "❌ እባክህ ቁጥር ብቻ አስገባ። የተጫዋቹን ቴሌግራም ID አስገባ፦")
            return
        user_states[admin_id]['target_user'] = int(message.text)
        bot.reply_to(message, "የሚጨመረውን የብር መጠን በቁጥር ብቻ ያስገቡ (ምሳሌ፡ 100)፦")
        user_states[admin_id]['admin_step'] = 'waiting_for_amount'
        
    elif step == 'waiting_for_amount':
        if not message.text.isdigit():
            bot.reply_to(message, "❌ እባክህ ቁጥር ብቻ አስገባ። የብር መጠኑን አስገባ፦")
            return
        amount = int(message.text)
        target_user = user_states[admin_id]['target_user']
        
        conn = sqlite3.connect('pubg_new_system.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE players SET balance = balance + ? WHERE user_id = ?", (amount, target_user))
        conn.commit()
        
        if cursor.rowcount > 0:
            bot.reply_to(message, f"✅ በተሳካ ሁኔታ ለተጫዋች {target_user} {amount} ብር ተጨምሯል!")
            try:
                bot.send_message(target_user, f"🎉 ሂሳብዎ ታድሷል!\n💰 {amount} ETB ወደ አካውንትዎ ተጨምሯል።\nየአሁኑ ቀሪ ሂሳብዎን ለማየት /profile ይበሉ።")
            except:
                pass
        else:
            bot.reply_to(message, "❌ ይህ ተጫዋች በዳታቤዙ ውስጥ አልተገኘም!")
            
        conn.close()
        del user_states[admin_id]

# ====== 🌐 ይህ ክፍል ለሰርቨሩ የተጨመረ አዲስ የዌብ ሰርቨር ኮድ ነው ======
app = Flask('')

@app.route('/')
def home():
    return "ቦቱ በጥሩ ሁኔታ እየሰራ ነው!"

def run_web_server():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web_server)
    t.start()

if __name__ == '__main__':
    keep_alive() # የዌብ ሰርቨሩን ያስነሳል
    print("ቦቱ በሰርቨር ላይ ለመነሳት ዝግጁ ነው...")
    bot.infinity_polling()
