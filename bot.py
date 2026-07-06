import os
import sys
import logging
import asyncio
from datetime import datetime
from typing import Dict, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)
from deep_translator import GoogleTranslator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 8080))
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

if not BOT_TOKEN:
    logger.error("No BOT_TOKEN found in environment variables!")
    sys.exit(1)

# Language mapping
LANGUAGES = {
    'en': '🇬🇧 English',
    'es': '🇪🇸 Spanish',
    'fr': '🇫🇷 French',
    'de': '🇩🇪 German',
    'it': '🇮🇹 Italian',
    'pt': '🇵🇹 Portuguese',
    'ru': '🇷🇺 Russian',
    'zh-cn': '🇨🇳 Chinese (Simplified)',
    'ja': '🇯🇵 Japanese',
    'ko': '🇰🇷 Korean',
    'ar': '🇸🇦 Arabic',
    'hi': '🇮🇳 Hindi',
    'bn': '🇧🇩 Bengali',
    'ur': '🇵🇰 Urdu',
    'ta': '🇮🇳 Tamil',
    'te': '🇮🇳 Telugu',
    'mr': '🇮🇳 Marathi',
    'sw': '🇰🇪 Swahili',
    'ha': '🇳🇬 Hausa',
    'yo': '🇳🇬 Yoruba',
    'ig': '🇳🇬 Igbo',
    'zu': '🇿🇦 Zulu',
    'af': '🇿🇦 Afrikaans',
    'am': '🇪🇹 Amharic',
    'ne': '🇳🇵 Nepali',
    'si': '🇱🇰 Sinhala',
    'th': '🇹🇭 Thai',
    'vi': '🇻🇳 Vietnamese',
    'id': '🇮🇩 Indonesian',
    'ms': '🇲🇾 Malay',
}

# User preferences storage (in-memory)
user_prefs: Dict[str, Dict] = {}
user_stats: Dict[str, Dict] = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when /start is issued."""
    user = update.effective_user
    user_id = str(user.id)
    
    # Initialize user preferences
    if user_id not in user_prefs:
        user_prefs[user_id] = {'target_lang': 'en'}
    if user_id not in user_stats:
        user_stats[user_id] = {
            'translations': 0,
            'first_seen': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat()
        }
    
    welcome_message = (
        f"🌍 *Welcome {user.first_name}!*\n\n"
        f"I'm your multilingual translator bot powered by Google Translate.\n\n"
        f"✨ *How to use me:*\n"
        f"• Send any text → I'll translate it instantly\n"
        f"• Use /translate → Change your target language\n"
        f"• Use /languages → See all available languages\n"
        f"• Use /stats → View your usage statistics\n"
        f"• Use /help → Get more help\n\n"
        f"🔹 *Your default target language:* English 🇬🇧\n"
        f"🔹 *Supported languages:* {len(LANGUAGES)}\n\n"
        f"_Start translating now! Just send me a message._"
    )
    
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message."""
    help_text = (
        "🤖 *Available Commands*\n\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/translate - Change your target language\n"
        "/languages - List all available languages\n"
        "/stats - View your translation stats\n"
        "/about - About this bot\n"
        "/reset - Reset your preferences\n\n"
        "💡 *Quick Tips:*\n"
        "• Send any text to translate it\n"
        "• Your language preference is saved\n"
        "• Works in groups too!\n"
        "• No need to specify source language\n\n"
        "_Need support? Just ask!_"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send about information."""
    about_text = (
        "🌐 *Language87 Translator Bot*\n\n"
        "📝 *Version:* 2.0.0\n"
        "🔄 *Powered by:* Google Translate API\n"
        "🌍 *Languages:* 30+ supported\n"
        "🚀 *Deployed on:* Railway\n"
        "📦 *Open Source:* GitHub\n\n"
        "✨ *Features:*\n"
        "• Automatic language detection\n"
        "• 30+ language support\n"
        "• User preferences saved\n"
        "• Usage statistics tracking\n"
        "• Inline language selection\n\n"
        "❤️ *Created with passion for global communication*"
    )
    
    await update.message.reply_text(about_text, parse_mode='Markdown')

async def languages_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show all available languages."""
    # Split languages into chunks for better display
    lang_list = []
    for code, name in LANGUAGES.items():
        lang_list.append(f"• {code}: {name}")
    
    # Send in chunks if too long
    chunk_size = 20
    chunks = [lang_list[i:i + chunk_size] for i in range(0, len(lang_list), chunk_size)]
    
    await update.message.reply_text(
        f"🌐 *Available Languages*\n\n"
        f"Total: {len(LANGUAGES)} languages\n\n"
        f"{chr(10).join(chunks[0])}\n"
    )
    
    if len(chunks) > 1:
        await update.message.reply_text(
            f"{chr(10).join(chunks[1])}\n"
        )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user statistics."""
    user_id = str(update.effective_user.id)
    
    if user_id not in user_stats:
        stats_text = "📊 *Your Statistics*\n\nNo translations yet. Start translating!"
    else:
        stats = user_stats[user_id]
        target_lang = user_prefs.get(user_id, {}).get('target_lang', 'en')
        target_name = LANGUAGES.get(target_lang, target_lang)
        
        stats_text = (
            f"📊 *Your Translation Statistics*\n\n"
            f"📝 Total translations: {stats.get('translations', 0)}\n"
            f"🎯 Current target: {target_name}\n"
            f"📅 First used: {stats.get('first_seen', 'N/A')[:10]}\n"
            f"🕐 Last active: {stats.get('last_seen', 'N/A')[:10]}\n"
            f"🌍 Available languages: {len(LANGUAGES)}"
        )
    
    await update.message.reply_text(stats_text, parse_mode='Markdown')

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reset user preferences."""
    user_id = str(update.effective_user.id)
    
    if user_id in user_prefs:
        user_prefs[user_id] = {'target_lang': 'en'}
        await update.message.reply_text(
            "✅ *Preferences Reset*\n\n"
            "Your target language has been reset to English 🇬🇧\n"
            "Your translation history has been cleared."
        )
    else:
        await update.message.reply_text(
            "ℹ️ No preferences to reset. Start using the bot!"
        )

async def translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show language selection keyboard."""
    keyboard = []
    row = []
    
    # Create inline keyboard with languages
    for code, name in LANGUAGES.items():
        row.append(InlineKeyboardButton(name, callback_data=f"lang_{code}"))
        if len(row) == 3:  # 3 buttons per row
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    # Add special buttons
    keyboard.append([
        InlineKeyboardButton("ℹ️ How to use", callback_data="help_lang"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌐 *Select your target translation language:*\n\n"
        "_Scroll through all 30+ languages_\n"
        "Your preference will be saved automatically.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses."""
    query = update.callback_query
    await query.answer()
    
    user_id = str(update.effective_user.id)
    
    if query.data.startswith("lang_"):
        lang_code = query.data.replace("lang_", "")
        lang_name = LANGUAGES.get(lang_code, lang_code)
        
        # Update user preference
        if user_id not in user_prefs:
            user_prefs[user_id] = {}
        user_prefs[user_id]['target_lang'] = lang_code
        
        await query.edit_message_text(
            f"✅ *Language Updated!*\n\n"
            f"Target language: {lang_name}\n"
            f"Language code: `{lang_code}`\n\n"
            f"Now send me any text and I'll translate it to {lang_name}!",
            parse_mode='Markdown'
        )
    
    elif query.data == "help_lang":
        await query.edit_message_text(
            "ℹ️ *How to change language:*\n\n"
            "1️⃣ Click on any language name below\n"
            "2️⃣ Your target language will be updated\n"
            "3️⃣ Send any text to test it\n\n"
            "Use /translate anytime to change again.",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data="back_to_lang")
            ]])
        )
    
    elif query.data == "back_to_lang":
        # Re-show language selection
        keyboard = []
        row = []
        for code, name in LANGUAGES.items():
            row.append(InlineKeyboardButton(name, callback_data=f"lang_{code}"))
            if len(row) == 3:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        keyboard.append([
            InlineKeyboardButton("ℹ️ How to use", callback_data="help_lang"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel")
        ])
        
        await query.edit_message_text(
            "🌐 *Select your target translation language:*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif query.data == "cancel":
        await query.edit_message_text(
            "❌ *Cancelled*\n\n"
            "Your language preference remains unchanged.",
            parse_mode='Markdown'
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages and translate them."""
    user_id = str(update.effective_user.id)
    text = update.message.text.strip()
    
    # Ignore very short messages or commands
    if len(text) < 1:
        return
    
    # Show typing indicator
    await update.message.chat.send_action(action="typing")
    
    # Get user's target language
    if user_id not in user_prefs:
        user_prefs[user_id] = {'target_lang': 'en'}
    if user_id not in user_stats:
        user_stats[user_id] = {
            'translations': 0,
            'first_seen': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat()
        }
    
    target_lang = user_prefs[user_id].get('target_lang', 'en')
    
    try:
        # Create translator instance
        translator = GoogleTranslator()
        
        # Detect source language
        try:
            detected = translator.detect(text)
            source_lang = detected
        except:
            # Fallback to auto
            source_lang = 'auto'
        
        # Translate
        if source_lang == target_lang:
            # Same language, no translation needed
            await update.message.reply_text(
                f"ℹ️ *Already in target language*\n\n"
                f"The text appears to be already in {LANGUAGES.get(target_lang, target_lang)}.\n"
                f"Try sending text in a different language or change your target language.",
                parse_mode='Markdown'
            )
            return
        
        # Perform translation
        translated = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
        
        # Get language names
        source_name = LANGUAGES.get(source_lang, source_lang)
        target_name = LANGUAGES.get(target_lang, target_lang)
        
        # Update statistics
        user_stats[user_id]['translations'] = user_stats[user_id].get('translations', 0) + 1
        user_stats[user_id]['last_seen'] = datetime.now().isoformat()
        
        # Prepare response
        response = (
            f"🔄 *Translation*\n\n"
            f"📝 **From** ({source_name}):\n"
            f"`{text}`\n\n"
            f"➡️ **To** ({target_name}):\n"
            f"`{translated}`\n\n"
            f"🔹 Send more text to translate\n"
            f"🔹 Use /translate to change language"
        )
        
        # If text is too long, send as formatted
        if len(response) > 4096:
            response = (
                f"📝 **Original** ({source_name}):\n"
                f"{text[:2000]}...\n\n"
                f"➡️ **Translated** ({target_name}):\n"
                f"{translated[:2000]}..."
            )
        
        await update.message.reply_text(
            response,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logger.error(f"Translation error for user {user_id}: {e}")
        error_message = (
            "❌ *Translation Failed*\n\n"
            "I couldn't translate that text. Possible reasons:\n"
            "• Text is too long\n"
            "• Language not supported\n"
            "• Network issues\n\n"
            "Please try again with shorter text or a different language."
        )
        await update.message.reply_text(error_message, parse_mode='Markdown')

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}")
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "⚠️ *An error occurred*\n\n"
                "Please try again later or contact support.",
                parse_mode='Markdown'
            )
    except:
        pass

async def post_init(application: Application) -> None:
    """Post initialization setup."""
    logger.info("Bot initialized successfully!")
    logger.info(f"Bot name: {application.bot.username}")
    logger.info(f"Bot ID: {application.bot.id}")
    
    # Set up webhook if URL provided
    if WEBHOOK_URL:
        await application.bot.set_webhook(
            url=WEBHOOK_URL,
            allowed_updates=Update.ALL_TYPES
        )
        logger.info(f"Webhook set to: {WEBHOOK_URL}")

def main() -> None:
    """Start the bot."""
    # Create Application
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("languages", languages_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(CommandHandler("translate", translate_command))
    
    # Register message handler for text messages
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )
    
    # Register callback query handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Register error handler
    application.add_error_handler(error_handler)

    # Start the bot
    if WEBHOOK_URL:
        # Webhook mode (for Railway)
        logger.info(f"Starting bot in webhook mode on port {PORT}")
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=WEBHOOK_URL
        )
    else:
        # Polling mode (for local development)
        logger.info("Starting bot in polling mode")
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )

if __name__ == "__main__":
    main()
