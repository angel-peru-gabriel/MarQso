import telebot
from config import TELEGRAM_BOT_TOKEN
from handlers.commands import register_commands
from handlers.items import register_items_handlers # inicializa las ediciones de items
from handlers.billing import register_billing_handlers
from handlers.sessions import get_session, set_session, delete_session

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def main():
    register_commands(bot)
    register_items_handlers(bot)
    register_billing_handlers(bot)
    #bot.polling(none_stop=True)
    # Start polling for updates
    try:
        print("🤖 Bot is running...")
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    main()
