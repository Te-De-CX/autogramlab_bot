from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
from keyboards.reply_keyboards import get_main_menu_keyboard
from database import register_user, get_portfolio_projects
import config

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    welcome_message = (
        "Welcome to AutoGram Lab ⚙️\n\n"
        "We build powerful Telegram bots and automation systems.\nAnnouncement Channel: @autogramlab\n\n"
        "Choose an option below."
    )
    await update.message.reply_text(
        welcome_message,
        reply_markup=get_main_menu_keyboard(user_id=user_id)
    )

async def portfolio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    projects = get_portfolio_projects()
    if not projects:
        await update.message.reply_text("No projects available yet. Please check back later.")
        return
    await update.message.reply_text("📂 *Our Portfolio*\n\nHere are some of our recent projects:", parse_mode='Markdown')
    for project in projects:
        text = f"*{project['name']}*\n\n{project['description']}"
        keyboard = [
            [InlineKeyboardButton("🔍 View Bot", url=project['link'])],
            [InlineKeyboardButton("💰 Purchase this Bot", callback_data=f"purchase_{project['name'].replace(' ', '_')}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    final_text = "✨ *Want something similar?*\n\nClick the button below to start your project!"
    bot_username = config.BOT_USERNAME.replace('@', '')
    deep_link = f"https://t.me/{bot_username}?start=order"
    keyboard = [[InlineKeyboardButton("🚀 Start a project", url=deep_link)]]
    await update.message.reply_text(final_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def purchase_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    project_name = query.data.replace("purchase_", "").replace("_", " ")
    user = update.effective_user
    user_info = f"@{user.username} (ID: {user.id}) – {user.full_name}"
    await query.edit_message_text(
        f"✅ Thank you for your interest in *{project_name}*!\n\n"
        "Our team has been notified. We will contact you shortly to discuss your requirements and provide a quote.\n\n"
        "You can also start a new order using the /order command.",
        parse_mode='Markdown'
    )
    admin_ids = config.ADMIN_IDS if hasattr(config, 'ADMIN_IDS') else [config.ADMIN_CHAT_ID]
    for admin_id in admin_ids:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"💰 *Purchase Inquiry*\n\nUser: {user_info}\nProject: {project_name}\nAction: Requested to purchase this bot.\nPlease contact the user to proceed.",
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"Failed to notify admin {admin_id}: {e}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    register_user(user.id, user.username, user.first_name, user.last_name)
    args = context.args
    if args:
        deep_link = args[0].lower()
        if deep_link == "portfolio":
            await portfolio_command(update, context)
            return ConversationHandler.END
        elif deep_link == "pricing":
            await pricing_command(update, context)
            return ConversationHandler.END
        elif deep_link == "contact":
            await contact_command(update, context)
            return ConversationHandler.END
        elif deep_link == "support":
            await support_command(update, context)
            return ConversationHandler.END
        elif deep_link == "order":
            from handlers.order import order_start
            return await order_start(update, context)
    welcome_message = (
        "Welcome to AutoGram Lab ⚙️\n\n"
        "We build powerful Telegram bots and automation systems.\nAnnouncement Channel: @autogramlab\n\n"
        "Choose an option below."
    )
    await update.message.reply_text(
        welcome_message,
        reply_markup=get_main_menu_keyboard(user_id=user.id)
    )
    return ConversationHandler.END

# Other commands (pricing, contact, support, help)
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📚 Help & Support\n\n"
        "Here's how to use this bot:\n\n"
        "• Click '🚀 Start a project' to start a new project\n"
        "• Click '📂 Our Portfolio' to see our work\n"
        "• Click '💰 Pricing' to view our rates\n"
        "• Click '📩 Contact Team' to reach us directly\n"
        "• Click '❓ Support' for assistance\n\n"
        "For urgent issues, contact @aglab_support"
    )
    await update.message.reply_text(help_text)

async def pricing_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pricing_text = (
        "💰 Pricing\n\n"
        "Our pricing varies based on complexity:\n\n"
        "Telegram Bots: $50–$500+\n"
        "Mini Apps: $150–$1000+\n"
        "Websites: $200–$2000+\n"
        "Automation Tools: $100–$800+\n\n"
        "Click '🚀 Start a project' for a detailed quote!"
    )
    await update.message.reply_text(pricing_text)

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact_text = (
        "📩 Contact Team\n\n"
        "You can reach us through:\n\n"
        "• Email: team@autogramlab.com\n"
        "• Telegram: @aglab_support\n"
        "• Website: autogramlab.com\n\n"
        "We typically respond within few hours."
    )
    await update.message.reply_text(contact_text)

async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    support_text = (
        "❓ Support\n\n"
        "Need help? Here are your options:\n\n"
        "1. Check our FAQ: autogramlab.com/faq\n"
        "2. Contact support: @aglab_support\n"
        "3. Email: team@autogramlab.com\n\n"
        "Or just continue with your order and we'll guide you!"
    )
    await update.message.reply_text(support_text)