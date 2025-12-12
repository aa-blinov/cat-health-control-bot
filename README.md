# Cat Health Control Bot

## Overview

**Cat Health Control Bot** is a Python-based Telegram bot designed to help cat owners track their pet's health. The bot allows users to log and monitor key health metrics, such as defecation events, stool types, asthma symptoms, and other relevant data, ensuring better care for their feline companions.

## 📖 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Product Documentation](docs/PRODUCT.md)** (Russian) — Полная продуктовая документация: руководство пользователя, описание функций, типичные сценарии использования
- **[Technical Documentation](docs/TECHNICAL.md)** (Russian) — Техническая документация: архитектура, API, развёртывание, разработка

## Features

- 🫁 **Asthma Attack Tracking**: Log asthma attacks with duration, reason, inhalation usage, and comments
- 💩 **Defecation Monitoring**: Track stool type, food correlation, and digestive health
- ⚖️ **Weight Control**: Record weight measurements with food type tracking
- 📊 **Data Export**: Export data in CSV, TSV, HTML, and Markdown formats
- 🌐 **Web Interface**: Modern, responsive web application with full CRUD operations
- 🤖 **Telegram Bot**: Quick event logging through mobile-friendly bot interface
- 🗄️ **MongoDB Storage**: Persistent, scalable data storage
- 🐳 **Fully Dockerized**: Easy deployment with Docker Compose
- 🔒 **Secure**: Authentication, user isolation, and whitelist protection

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Your Telegram ID (from [@userinfobot](https://t.me/userinfobot))

### Installation

1. **Clone the repository**:
   ```sh
   git clone https://github.com/aa-blinov/cat-health-control-bot.git
   cd cat-health-control-bot
   ```

2. **Create `.env` file**:
   ```sh
   cp .env.example .env
   ```
   
   Edit `.env` and set your values:
   ```env
   MONGO_USER=admin
   MONGO_PASS=your_secure_password
   MONGO_HOST=db
   MONGO_PORT=27017
   MONGO_DB=cat_health
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   FLASK_SECRET_KEY=your_secret_key_here
   DEFAULT_PASSWORD=admin123
   ```

3. **Add your Telegram ID to whitelist**:
   ```sh
   echo "YOUR_TELEGRAM_ID" > bot/whitelist.txt
   ```

4. **Start the application**:
   ```sh
   docker-compose up -d --build
   ```

5. **Access the services**:
   - **Web Interface**: http://localhost:5001 (login: admin / admin123)
   - **Telegram Bot**: Find your bot in Telegram and send `/start`

### Usage

**For detailed usage instructions, see [Product Documentation](docs/PRODUCT.md).**

#### Telegram Bot

- Use main menu buttons: **Asthma Attack**, **Defecation**, **Export Data**
- Follow bot's prompts to complete each action
- Use "Back to Menu" button to return at any time

#### Web Interface

1. Login at `http://localhost:5001`
2. Use dashboard cards to:
   - Record asthma attacks
   - Record defecation events
   - Record weight measurements
   - View and manage history
3. Export data in various formats (CSV, TSV, HTML, Markdown)

## 🏗️ Architecture

```
┌─────────────┐
│    User     │
└──────┬──────┘
   ┌───┴───┐
   │       │
┌──▼──┐ ┌─▼───┐
│T-Bot│ │ Web │
└──┬──┘ └──┬──┘
   └───┬───┘
    ┌──▼──┐
    │ DB  │
    └─────┘
```

- **Telegram Bot**: Quick mobile data entry
- **Web Application**: Detailed management and analysis (Flask)
- **MongoDB**: Shared data storage
- **Docker Compose**: Container orchestration

## 📚 Technical Stack

- **Backend**: Python 3.x
- **Bot Framework**: python-telegram-bot
- **Web Framework**: Flask
- **Database**: MongoDB
- **Frontend**: Jinja2 templates, vanilla JavaScript, custom CSS
- **Deployment**: Docker + Docker Compose

## 📂 Project Structure

```text
cat-health-control-bot/
├── bot/                    # Telegram Bot
│   ├── main.py            # Bot entry point
│   ├── handlers.py        # Command handlers
│   ├── db.py              # Database operations
│   ├── config.py          # Configuration
│   └── whitelist.txt      # Authorized users
├── web/                    # Web Application
│   ├── main.py            # Web entry point
│   ├── app.py             # Flask application
│   ├── templates/         # HTML templates
│   │   ├── base.html
│   │   ├── login.html
│   │   └── dashboard.html
│   └── static/            # CSS, JS
│       └── css/
│           └── style.css
├── docs/                   # Documentation
│   ├── PRODUCT.md         # Product documentation
│   └── TECHNICAL.md       # Technical documentation
├── .env.example           # Environment variables template
├── docker-compose.yml     # Docker orchestration
├── Dockerfile             # Container definition
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Project metadata
└── README.md              # This file
```

## Useful Commands

**View logs**:
```sh
docker-compose logs -f        # All services
docker-compose logs -f bot    # Bot only
docker-compose logs -f web    # Web only
```

**Stop services**:
```sh
docker-compose down
```

**Restart a service**:
```sh
docker-compose restart bot
docker-compose restart web
```

**Check status**:
```sh
docker-compose ps
```

**For more commands and advanced usage, see [Technical Documentation](docs/TECHNICAL.md).**

## 🔒 Security

- **Authentication**: Login required for web interface
- **Whitelist**: Only authorized Telegram users can access the bot
- **Session Management**: Secure Flask sessions with secret key
- **Data Isolation**: Users see only their own data
- **Docker Isolation**: Services run in isolated containers

**For security best practices, see [Technical Documentation](docs/TECHNICAL.md).**

## 🚀 Deployment

### Local Development

See [Technical Documentation](docs/TECHNICAL.md#development) for local development setup without Docker.

### Production Deployment

For production deployment with Nginx, HTTPS, and monitoring, see [Technical Documentation](docs/TECHNICAL.md#production-deployment).

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [Technical Documentation](docs/TECHNICAL.md#contributing) for coding standards and guidelines.

## License

This project is licensed under the MIT License. See the [LICENSE](https://opensource.org/license/mit) file for details.

