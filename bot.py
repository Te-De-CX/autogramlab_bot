#!/usr/bin/env python3
"""
AutoGram Lab Bot - Main entry point
Username: @AutogramLab_bot
"""

import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    filters, ConversationHandler, ContextTypes, CallbackQueryHandler
)
import config
from database import init_db
from handlers.start import (
    start_command, help_command, portfolio_command, pricing_command,
    contact_command, support_command, purchase_callback
)
from handlers.order import (
    order_start, handle_service_selection, handle_bot_name,
    handle_bot_description, handle_budget, handle_deadline,
    cancel_order
)
from handlers.common import handle_menu_selection
from handlers.admin import admin_conv

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "Sorry, an error occurred. Please try again or contact support."
            )
    except:
        pass

def main():
    init_db()
    application = Application.builder().token(config.BOT_TOKEN).build()
    application.add_error_handler(error_handler)

    # Order conversation handler
    order_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex('^🚀 Start a project$'), order_start),
            CommandHandler('order', order_start)
        ],
        states={
            config.SERVICE_SELECTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_service_selection)
            ],
            config.BOT_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_bot_name)
            ],
            config.BOT_DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_bot_description)
            ],
            config.BUDGET_SELECTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_budget)
            ],
            config.DEADLINE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_deadline)
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel_order),
            MessageHandler(filters.Regex('^🔙 Back to Main Menu$'), cancel_order)
        ],
        name="order_conversation",
        persistent=False
    )

    # Command handlers
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('portfolio', portfolio_command))
    application.add_handler(CommandHandler('pricing', pricing_command))
    application.add_handler(CommandHandler('contact', contact_command))
    application.add_handler(CommandHandler('support', support_command))
    
    # Admin conversation
    application.add_handler(admin_conv)
    
    # Order conversation
    application.add_handler(order_conv_handler)
    
    # Menu button handlers (text messages)
    application.add_handler(MessageHandler(
        filters.Regex('^(📂 Our Portfolio|💰 Pricing|📩 Contact Team|❓ Support|👑 Admin Panel)$'),
        handle_menu_selection
    ))

    # Purchase callback
    application.add_handler(CallbackQueryHandler(purchase_callback, pattern='^purchase_'))

    # Unknown commands
    application.add_handler(MessageHandler(
        filters.COMMAND,
        lambda u, c: u.message.reply_text("Unknown command. Use /start or /help")
    ))

    print(f"🤖 Bot {config.BOT_USERNAME} is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()