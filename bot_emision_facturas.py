import telebot
from config import TELEGRAM_BOT_TOKEN
from handlers.commands import register_commands
from handlers.items import register_items_handlers
from handlers.billing import register_billing_handlers
from handlers.sessions import get_session, set_session, delete_session

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def main():
    register_commands(bot)
    register_items_handlers(bot)
    register_billing_handlers(bot)
    bot.polling(none_stop=True)

if __name__ == "__main__":
    main()
