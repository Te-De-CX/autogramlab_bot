from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
from keyboards.reply_keyboards import get_main_menu_keyboard
import config

# ---------- Portfolio Data ----------
PROJECTS = [
    {
        "name": "Crypto Alert Bot",
        "description": "Real-time cryptocurrency price alerts with custom thresholds, multi‑exchange support, and instant push notifications.",
        "link": "https://t.me/YourDemoBot"  # Replace with actual bot link or demo
    },
    {
        "name": "Task Manager Mini App",
        "description": "Team productivity tool with task assignment, deadline tracking, file attachments, and real‑time sync.",
        "link": "https://t.me/YourDemoApp"
    },
    {
        "name": "E‑commerce Website",
        "description": "Full‑featured online store with payment integration, inventory management, and admin dashboard.",
        "link": "https://yourdemo.com"
    },
    {
        "name": "Social Media Automation",
        "description": "Auto‑post across platforms (Twitter, Telegram, Discord) with scheduling, content recycling, and analytics.",
        "link": "https://t.me/YourDemoBot"
    }
]

# ---------- Helper to get main menu keyboard (needed for callbacks) ----------
async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send the main menu (used after callbacks)"""
    user_id = update.effective_user.id
    welcome_message = (
        "Welcome to AutoGram Lab ⚙️\n\n"
        "We build powerful Telegram bots and automation systems.\nAnnouncement Channel: @autogramlab\n\n"
        "Choose an option below."
    )
    await update.message.reply_text(
        welcome_message,
        reply_markup=get_main_menu_keyboard()
    )

# ---------- Portfolio Command (now interactive) ----------
async def portfolio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send portfolio projects one by one with inline buttons"""
    # First, a header message
    await update.message.reply_text("📂 *Our Portfolio*\n\nHere are some of our recent projects:", parse_mode='Markdown')
    
    # Send each project as a separate message
    for project in PROJECTS:
        text = f"*{project['name']}*\n\n{project['description']}"
        keyboard = [
            [
                InlineKeyboardButton("🔍 View Bot", url=project['link']),]
            [    InlineKeyboardButton("💰 ", callback_data=f"purchase_{project['name'].replace(' ', '_')}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    
    # Final message with button to start ordering
    final_text = "✨ **\n\nClick the button below let's create your project!"
    keyboard = [[InlineKeyboardButton("🚀 Let's create your project", callback_data="start_order")]]
    await update.message.reply_text(final_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

# ---------- Callback Handlers for Portfolio ----------
async def purchase_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle '' button – creates an inquiry and notifies admin"""
    query = update.callback_query
    await query.answer()
    
    # Extract project name from callback data
    project_name = query.data.replace("purchase_", "").replace("_", " ")
    user = update.effective_user
    user_info = f"@{user.username} (ID: {user.id}) – {user.full_name}"
    
    # Notify user
    await query.edit_message_text(
        f"✅ Thank you for your interest in *{project_name}*!\n\n"
        "Our team has been notified. We will contact you shortly to discuss your requirements and provide a quote.\n\n"
        "You can also start a new order using the /order command.",
        parse_mode='Markdown'
    )
    
    # Notify admin(s)
    admin_ids = config.ADMIN_IDS  # Ensure this list exists in config.py
    if not admin_ids:
        # Fallback to single ADMIN_CHAT_ID if ADMIN_IDS not defined
        admin_ids = [config.ADMIN_CHAT_ID]
    
    for admin_id in admin_ids:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"💰 *Purchase Inquiry*\n\n"
                     f"User: {user_info}\n"
                     f"Project: {project_name}\n"
                     f"Action: Requested to .\n"
                     f"Please contact the user to proceed.",
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"Failed to notify admin {admin_id}: {e}")

async def start_order_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Redirect to the order flow (same as pressing 'Order a Bot' button)"""
    query = update.callback_query
    await query.answer()
    # Import here to avoid circular import
    from handlers.order import order_start
    # order_start expects a Message, not a CallbackQuery.
    # We simulate a message by using query.message and calling order_start with update = query
    # But order_start expects update to be a Message update. We'll call it with the original update object.
    # However, the callback query's `update` still contains the original message.
    # We'll simply call order_start(update, context) – it will work because update.message exists.
    await order_start(update, context)

# ---------- Existing /start command (unchanged) ----------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command with optional deep link argument"""
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
        reply_markup=get_main_menu_keyboard()
    )
    return ConversationHandler.END

# ---------- Other existing commands (pricing, contact, support, help) unchanged ----------
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📚 Help & Support\n\n"
        "Here's how to use this bot:\n\n"
        "• Click '🚀 Order a Bot' to start a new project\n"
        "• Click '📂 Our Portfolio' to see our work\n"
        "• Click '💰 Pricing' to view our rates\n"
        "• Click '📩 Contact Team' to reach us directly\n"
        "• Click '❓ Support' for assistance\n\n"
        "For urgent issues, contact @project"
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
        "Click '🚀 Order a Bot' for a detailed quote!"
    )
    await update.message.reply_text(pricing_text)

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact_text = (
        "📩 Contact Team\n\n"
        "You can reach us through:\n\n"
        "• Email: team@autogramlab.com\n"
        "• Telegram: @aglab_support\n"
        "• Website: autogramlab.com\n\n"
        "We project few hours."
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