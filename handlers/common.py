from telegram import Update
from telegram.ext import ContextTypes
from handlers.start import (
    portfolio_command, pricing_command, 
    contact_command, support_command
)
from handlers.order import order_start
from handlers.admin import admin_panel
from keyboards.reply_keyboards import get_main_menu_keyboard

async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🚀 Start a project":
        return await order_start(update, context)
    elif text == "📂 Our Portfolio":
        await portfolio_command(update, context)
    elif text == "💰 Pricing":
        await pricing_command(update, context)
    elif text == "📩 Contact Team":
        await contact_command(update, context)
    elif text == "❓ Support":
        await support_command(update, context)
    elif text == "👑 Admin Panel":
        await admin_panel(update, context)
        return True
    elif text == "🔙 Back to Main Menu":
        await back_to_main(update, context)
        return True
    return None

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(
        "Main menu:",
        reply_markup=get_main_menu_keyboard(user_id=user_id)
    )