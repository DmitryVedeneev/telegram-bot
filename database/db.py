from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Boolean,
    Integer,
    Float,
    DateTime,
    CursorResult,
    insert,
    event,
    inspect
)
from sqlalchemy.exc import OperationalError
import datetime
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def insert_rows_into_table(rows, table, engine):
    for row in rows:
        stmt = insert(table).values(**row)
        with engine.begin() as connection:
            connection.execute(stmt)

# Создание текстового описания схемы БД
def get_scheme_description(engine, metadata_obj):
    scheme_description = ""

    inspector = inspect(engine)
    for table in metadata_obj.tables:
        print(table)
        columns_info = [(col["name"], col["type"]) for col in inspector.get_columns(table)]

        print(columns_info)
        table_description = f"Table '{table}':\n"

        table_description += "Columns:\n" + "\n".join([f"  - {name}: {col_type}" for name, col_type in columns_info])
        scheme_description += table_description + "\n\n"
    # test = metadata_obj.tables
    # for table_name in metadata_obj.tables:
    #     print(f"Table: {table_name}")
    #     scheme_description += f"Table: {table_name}"
    #     columns = inspector.get_columns(table_name)
    #     for column in columns:
    #         print(f"Column Name: {column['name']}, Type: {column['type']}")
    #         scheme_description += f"Column Name: {column['name']}, Type: {column['type']}"
    # scheme_description += "\n\n"

    return scheme_description

def init_postgres_db():
    # try:
    engine = create_engine("postgresql://postgres:password@localhost:5431/demo")
    metadata_obj = MetaData()
    metadata_obj.reflect(bind=engine)
    for table in metadata_obj.tables: print(table)
    return engine, metadata_obj
    # except OperationalError as error: 
    #     logging.exception(f"Ошибка подключения к PostgreSQL - {error}")
    #     return None, None

def init_sqlite_db():
    engine = create_engine("sqlite:///:memory:")
    metadata_obj = MetaData()

    # Таблица "Пользователи"
    users = Table(
        "users",
        metadata_obj,
        Column("user_id", Integer, primary_key=True), # id пользователя
        Column("username", String(16), primary_key=True), # имя пользователя
        Column("notifications_enabled", Boolean), # признак включения оповещений
    )

    # Таблица "Оповещения"
    notifications = Table(
        "notifications",
        metadata_obj,
        Column("notification_id", Integer, primary_key=True),  # id оповещения
        Column("user_id", String(16)), # id пользователя
        Column("text", String(128)), # текст оповещения
        Column("datetime", DateTime), # время отправки оповещения
    )

    # Таблица "Параметры"
    params = Table(
        "params",
        metadata_obj,
        Column("param_id", Integer, primary_key=True),  # id параметра
        Column("code", String(128)), # код параметра
        Column("description", String(128)), # описание параметра
    )

    # Таблица "Значения параметров"
    param_values = Table(
        "param_values",
        metadata_obj,
        Column("param_id", Integer, primary_key=True), # id параметра
        Column("datetime", DateTime, primary_key=True), # метка времени значения 
        Column("value", Float), # значение параметра
    )

    metadata_obj.create_all(engine)

    user_rows = [
        {"user_id": 1, "username": "User_1", "notifications_enabled": True},
        {"user_id": 2, "username": "User_2",  "notifications_enabled": False},
        {"user_id": 3, "username": "User_3", "notifications_enabled": True},
        {"user_id": 4, "username": "User_4", "notifications_enabled": True},
    ]
    insert_rows_into_table(user_rows, users, engine)

    notification_rows = [
        {"notification_id": 1, "user_id": 1, "text": "abc", "datetime": datetime.datetime(2025, 11, 2)},
        {"notification_id": 2, "user_id": 1,  "text": "abcd", "datetime": datetime.datetime(2025, 11, 3)},
        {"notification_id": 3, "user_id": 3, "text": "abcef", "datetime": datetime.datetime(2025, 11, 4)},
        {"notification_id": 4, "user_id": 4, "text": "ab", "datetime": datetime.datetime(2025, 11, 5)},
    ]
    insert_rows_into_table(notification_rows, notifications, engine)

    param_rows = [
        {"param_id": 1, "code": "Param_1", "description": "Description 1"},
        {"param_id": 2, "code": "Param_2",  "description": "Description 1"},
        {"param_id": 3, "code": "Param_3", "description": "Description 3"},
        {"param_id": 4, "code": "Param_4", "description": "Description 4"},
    ]
    insert_rows_into_table(param_rows, params, engine)

    param_value_rows = [
        {"param_id": 1, "datetime": datetime.datetime(2025, 11, 2), "value": '1.11'},
        {"param_id": 1, "datetime": datetime.datetime(2025, 11, 3), "value": '2.11'},
        {"param_id": 1, "datetime": datetime.datetime(2025, 11, 4), "value": '3.11'},
        {"param_id": 1, "datetime": datetime.datetime(2025, 11, 5), "value": '1.11'},
    ]
    insert_rows_into_table(param_value_rows, param_values, engine)
    
    return engine, metadata_obj