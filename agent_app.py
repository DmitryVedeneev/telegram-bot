import logging
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackContext, CallbackQueryHandler
from agent.SQLExecutionAgent import SQLExecutionAgent
from database.db import get_scheme_description, init_postgres_db, init_sqlite_db

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ya_folder_id = os.getenv('YA_FOLDER_ID')
ya_api_key = os.getenv('YA_API_KEY')
model = f'gpt://{ya_folder_id}/yandexgpt-lite/latest'

pg_engine, pg_metadata_obj = init_postgres_db()
sqlite_engine, sqlite_metadata_obj = init_sqlite_db()

pg_system_prompt = f"""
    Ты разработчик SQL-запросов. Имеется следующая схема базы данных:"
    {get_scheme_description(pg_engine, pg_metadata_obj)}
    Тебе необходимо формировать SQL-запросы для этой базы данных на диалекте PL/pgSQL.   
    При формировании запросов нужно учитывать схему данных.
    Можно формировать запросы только на получение данных (SELECT). 
    При попытке выполнения запросов, которые модифицируют данные или схему базы данных, 
    необходимо возвращать сообщение о том, что такая операция не поддерживается. 
"""

sqlite_system_prompt = f"""
    Ты разработчик SQL-запросов для СУБД SQLite. Имеется следующая схема базы данных:"
    {get_scheme_description(sqlite_engine, sqlite_metadata_obj)}
    Тебе необходимо формировать SQL-запросы для этой базы данных. 
    При формировании запросов нужно учитывать схему данных.
    Можно формировать запросы только на получение данных (SELECT). 
    При попытке выполнения запросов, которые модифицируют данные или схему базы данных, 
    необходимо возвращать сообщение о том, что такая операция не поддерживается. 
"""

app_description = f"""
Я чат-бот с моделью для формирования SQL-запросов. 
Моя задача — помочь с созданием запросов на получение данных из указанной базы данных. 
Если у вас есть вопросы по SQL-запросам, пожалуйста, задайте их мне, и я постараюсь помочь.
"""

db_names = {"Bookings": "PostgreSQL", "Test": "SQLite"}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

user_selected_db = {}

# Приветственная функция
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=app_description)
    await select_db(update, context)

async def select_db(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with three inline buttons attached."""
    keyboard = [
        [
            InlineKeyboardButton("PostgreSQL (Bookings)", callback_data="Bookings"),
            InlineKeyboardButton("SQLite (Test)", callback_data="Test"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Выберите БД:", reply_markup=reply_markup)

# Функция получения данных из указанной пользователем БД
async def get_data(update: Update, context: CallbackContext):
    message = update.message.text
    logging.info(msg=f'Получен запрос: {message}')
    selected_db = user_selected_db[update.effective_sender.id]
    if (selected_db == 'PostgreSQL'):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=str(pg_agent.get_data(message)))
    elif (selected_db == 'SQLite'):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=str(sqlite_agent.get_data(message)))
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, 
                                       text=f'Ошибка получения данных - указана неподдерживаемая БД {selected_db}')
        
# Функция обработки кнопки выбора БД
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    selected_db = db_names[query.data]
    user_selected_db[update.effective_sender.id] = selected_db
    logging.info(f"User_id: {update.effective_sender.id}, db: {selected_db}")
    await query.answer()
    await query.edit_message_text(text=f"Выбрана БД: {query.data}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    pg_agent = SQLExecutionAgent(ya_api_key, ya_folder_id, model, pg_system_prompt, pg_engine)
    sqlite_agent = SQLExecutionAgent(ya_api_key, ya_folder_id, model, sqlite_system_prompt, sqlite_engine)
        
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    select_db_handler = CommandHandler('select', select_db)
    application.add_handler(select_db_handler)

    text_handler = MessageHandler(filters=None, callback=get_data)
    application.add_handler(text_handler)    

    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()

