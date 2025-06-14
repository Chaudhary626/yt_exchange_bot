import telebot
from telebot import types
from config import BOT_TOKEN
from handlers.start_handler import handle_start
from handlers.submit_handler import handle_submit, handle_remove_video, handle_submit_callback
from handlers.match_handler import handle_match, handle_next_task_callback
from handlers.proof_handler import handle_proof, handle_proof_document, handle_proof_callback
from handlers.verify_handler import handle_verify, handle_verify_callback
from handlers.video_handler import handle_videos, handle_remove_video_callback
from handlers.report_handler import handle_report, handle_report_callback

bot = telebot.TeleBot(BOT_TOKEN)

# --- Command Handlers ---
@bot.message_handler(commands=['start'])
def start(message):
    handle_start(bot, message)

@bot.message_handler(commands=['submit'])
def submit(message):
    handle_submit(bot, message)

@bot.message_handler(commands=['videos'])
def videos(message):
    handle_videos(bot, message)

@bot.message_handler(commands=['match'])
def match(message):
    handle_match(bot, message)

@bot.message_handler(commands=['proof'])
def proof(message):
    handle_proof(bot, message)

@bot.message_handler(commands=['verify'])
def verify(message):
    handle_verify(bot, message)

@bot.message_handler(commands=['report'])
def report(message):
    handle_report(bot, message)

# --- Callback Query Handler (for inline button presses) ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith('remove_video:'):
        handle_remove_video_callback(bot, call)
    elif call.data.startswith('submit_video:'):
        handle_submit_callback(bot, call)
    elif call.data.startswith('verify_proof:'):
        handle_verify_callback(bot, call)
    elif call.data.startswith('proof_approve:') or call.data.startswith('proof_reject:'):
        handle_proof_callback(bot, call)
    elif call.data.startswith('report_video:'):
        handle_report_callback(bot, call)
    elif call.data.startswith('next_task:'):
        handle_next_task_callback(bot, call)
    # Add more as needed

# --- Handle Proof Upload (photo/video) ---
@bot.message_handler(content_types=['photo', 'video', 'document'])
def proof_document(message):
    handle_proof_document(bot, message)

# --- Main ---
if __name__ == "__main__":
    print("Bot running...")
    bot.infinity_polling(skip_pending=True)