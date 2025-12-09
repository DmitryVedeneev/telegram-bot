from openai import OpenAI
from tabulate import tabulate
import sqlparse
import pandas as pd
import logging
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy import (
    CursorResult,
    text,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class SQLExecutionAgent:

    # Конструктор
    def __init__(self, ya_api_key, ya_folder_id, model, system_prompt, engine):
        self.system_prompt = system_prompt
        self.model = model
        self.prev_response_id = {}
        self.client = OpenAI(
            base_url='https://rest-assistant.api.cloud.yandex.net/v1',
            api_key=ya_api_key,
            project=ya_folder_id
        )
        self.engine = engine
    
    # Метод получения ответа от модели по запросу
    def __create_response(self, input_text, session_id = "default"):
        prev_response_id = self.prev_response_id.get(session_id)
        response = self.client.responses.create(
            model=self.model,
            instructions=self.system_prompt,
            previous_response_id=prev_response_id,
            input=input_text
        )
        self.prev_response_id[session_id] = response.id
        return response.output_text.replace('`', '')

    # Метод выполнения запроса к БД
    def __run_query(self, query):
        try :
            with self.engine.begin() as connection:
                result = connection.execute(text(query))
                return result, result.keys()
        except OperationalError:
            return f'Ошибка - {query}'
    
    # Метод получения данных из БД по текстовому запросу
    def get_data(self, input_text):
        response = self.__create_response(input_text)
        logging.info(response)
        try:
            data, columns = self.__run_query(response)
        # columns = self.__get_query_columns(response)
            if isinstance(data, CursorResult):
                return self.__parse_data(data, columns)
                # return tabulate(self.__parse_data(data, columns), headers=columns, tablefmt='html')
            else:
                return response
        except:
            return response
    
    # Перевод данных в DataFrame pandas
    def __parse_data(self, data, columns):
        df = pd.DataFrame().from_records(data)
        df.columns = columns
        return df

    # Метод получения запрашиваемых из БД столбцов
    def __get_query_columns(self, sql):
        logging.info(sql)
        statement = sqlparse.parse(sql)[0]
        columns = []

        in_select = False
        for token in statement.tokens:
            if isinstance(token, sqlparse.sql.Comment):
                continue
            if str(token).lower() == 'select':
                in_select = True
            elif in_select and token.ttype is None:
                for identifier in token.get_identifiers():
                    columns.append(identifier.get_name())
                break

        return columns