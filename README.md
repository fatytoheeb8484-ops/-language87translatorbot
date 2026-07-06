# 🌍 Language87 Translator Bot

A powerful multilingual translation bot for Telegram supporting 30+ languages, powered by Google Translate.

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template)

## ✨ Features

- 🌐 **30+ Languages** - Translate between major world languages
- 🎯 **Auto Detection** - Automatically detects source language
- 🔄 **Smart Translation** - Context-aware translations
- 💾 **Persistent Preferences** - Remembers your target language
- 📊 **Usage Statistics** - Track your translation activity
- 🎨 **User-Friendly** - Clean interface with inline buttons
- 🚀 **Fast & Reliable** - Deployed on Railway infrastructure

## 🚀 Quick Deploy

### 1. Create Bot on Telegram
1. Open Telegram and message [@BotFather](https://t.me/botfather)
2. Send `/newbot`
3. Name: `Language87 Translator`
4. Username: `language87translatorbot`
5. Copy the **HTTP API token**

### 2. Deploy on Railway
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template)

Or manually:
1. Fork this repository
2. Go to [Railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub"
4. Select your forked repository
5. Add environment variable: `BOT_TOKEN` = your token
6. Deploy!

### 3. Start Using
Search for `@language87translatorbot` on Telegram and start translating!

## 📚 Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and see welcome message |
| `/help` | Show all available commands |
| `/translate` | Change your target language |
| `/languages` | List all 30+ supported languages |
| `/stats` | View your translation statistics |
| `/about` | About this bot |
| `/reset` | Reset your preferences |

## 🔧 Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/language87-translator-bot.git
cd language87-translator-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your token
echo "BOT_TOKEN=your_token_here" > .env

# Run the bot
python bot.py
