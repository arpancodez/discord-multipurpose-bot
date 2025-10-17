# Discord Multipurpose Bot 🤖

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Discord.py](https://img.shields.io/badge/Discord.py-2.0+-blue.svg)](https://github.com/Rapptz/discord.py)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A professional, feature-rich multipurpose Discord bot built with Discord.py featuring advanced moderation, anti-nuke protection, utility commands, fun games, and a modern UI with interactive buttons. Developed with veteran-level code quality and best practices.

## ✨ Features

### 🛡️ Moderation
- Advanced moderation commands (kick, ban, mute, warn)
- Customizable auto-moderation system
- Bulk message deletion
- Member management tools
- Role management
- Channel lockdown capabilities

### 🔒 Anti-Nuke Protection
- Real-time threat detection
- Automatic action rollback
- Channel/role spam protection
- Mass ban/kick detection
- Configurable security thresholds
- Admin action logging

### 🎮 Fun & Games
- Interactive mini-games
- Economy system
- Trivia commands
- Random fun commands
- Image manipulation
- Meme generation

### 🔧 Utility Commands
- Server information
- User information
- Role information
- Custom embeds
- Reminders
- Polls and voting
- Calculator
- Weather information

### 📚 Help System
- Beautiful embed paginator
- Categorized command list
- Interactive button navigation
- Command usage examples
- Permission requirements display

### 🎨 Modern UI
- Interactive button menus
- Select menu dropdowns
- Modal forms for input
- Rich embed designs
- Emoji reactions
- Color-coded embeds

### 📊 Comprehensive Logging
- Message logs (edit/delete)
- Member join/leave logs
- Role change logs
- Channel modification logs
- Moderation action logs
- Voice channel activity
- Customizable log channels

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- Discord Bot Token ([Get one here](https://discord.com/developers/applications))
- Required Python packages (see requirements.txt)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/arpancodez/discord-multipurpose-bot.git
cd discord-multipurpose-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the bot:
- Copy `config.example.json` to `config.json`
- Add your bot token and other settings
- Configure database connection (SQLite by default)

4. Run the bot:
```bash
python main.py
```

## ⚙️ Configuration

Edit `config.json` with your settings:

```json
{
  "token": "YOUR_BOT_TOKEN",
  "prefix": "!",
  "owner_ids": [],
  "database": "sqlite:///bot.db",
  "logging_channel": null,
  "anti_nuke": {
    "enabled": true,
    "threshold": 5
  }
}
```

## 📖 Usage

Default prefix: `!`

### Basic Commands
```
!help - Display the help menu
!ping - Check bot latency
!info - Bot information
!serverinfo - Server information
```

### Moderation Commands
```
!kick @user [reason] - Kick a member
!ban @user [reason] - Ban a member
!mute @user [duration] [reason] - Mute a member
!purge <amount> - Delete messages
!warn @user [reason] - Warn a member
```

### Fun Commands
```
!8ball <question> - Ask the magic 8ball
!meme - Generate a random meme
!trivia - Start a trivia game
!coinflip - Flip a coin
```

## 🏗️ Project Structure

```
discord-multipurpose-bot/
├── cogs/
│   ├── moderation.py
│   ├── antinuke.py
│   ├── fun.py
│   ├── utility.py
│   ├── logging.py
│   └── help.py
├── utils/
│   ├── database.py
│   ├── embeds.py
│   ├── checks.py
│   └── paginator.py
├── config/
│   └── config.json
├── main.py
├── requirements.txt
└── README.md
```

## 🔐 Permissions

The bot requires the following permissions:
- Read Messages/View Channels
- Send Messages
- Embed Links
- Attach Files
- Read Message History
- Add Reactions
- Use External Emojis
- Manage Messages
- Manage Roles
- Kick Members
- Ban Members
- Manage Channels

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Discord.py](https://github.com/Rapptz/discord.py) - The amazing Discord API wrapper
- All contributors and users of this bot

## 📞 Support

If you need help or have questions:
- Open an issue on GitHub
- Join our Discord server (coming soon)

## ⚠️ Disclaimer

This bot is provided as-is. Please ensure you comply with Discord's Terms of Service and Community Guidelines when using this bot.

---

**Made with ❤️ and Python** | **Star ⭐ this repository if you find it helpful!**
