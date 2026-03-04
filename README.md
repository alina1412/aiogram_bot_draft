## Aiogram Project Template (with RabbitMQ)
A draft project for Telegram bots with message queue integration (RabbitMQ)

- Bot Functionality Overview

This Telegram bot demonstrates three core features:
- 1️⃣ Basic Interaction

    /start - Welcome message

    Any message → Bot echoes it back (or shows keyboard for "key" trigger)

- 2️⃣ Delayed Messaging with RabbitMQ

    /later - Sends your message to RabbitMQ queue instead of responding immediately

    Demonstrates async message processing and queue integration

- 3️⃣ Interactive Keyboard

    Press buttons on inline keyboard → Bot responds with which button was pressed

    Shows callback query handling with data filtering


### 🛠️ Technology Stack

- Core: Python, Aiogram (Telegram Bot framework)
- Database: PostgreSQL, SQLAlchemy 2.0 (async), Alembic (migrations)
- Infrastructure: Docker, Docker Compose, RabbitMQ (message broker)
- Tools: Make (task automation), Uv (fast Python package manager)


### 📋 Prerequisites

- Python 3.13+
- Uv
- Docker and Docker Compose
- PostgreSQL (optional - can use Docker)
- Token for telegram bot (in config.yml) (get from @BotFather)

### Project Setup
1. Environment Configuration
- cp config_example.yml config.yml # Configure your variables
2. How to run project
- make up (docker compose up -d) # to run RabbitMQ in docker

    * in the process of creation a queue with name $QUEUE_NAME creates automatically

- make run (python -m aio)
