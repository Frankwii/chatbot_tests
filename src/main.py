from templates import PromptTemplate
from pathlib import Path
from dotenv import load_dotenv
from database_connector import DatabaseConnector

import os
import json

class PromptPreparer():
    def __init__(self, template_json_path:Path|str):
        with open(template_json_path, 'r', encoding='utf-8') as json_file:
            data=dict(json.load(json_file))

        self.__prompt_templates={prompt_name:PromptTemplate(raw_template) for prompt_name, raw_template in data.items()}

    def fill_prompt(self, prompt_template_name:str, replacements:dict[str,str])->str:
        return self.__prompt_templates[prompt_template_name].replace_all(replacements)

    @staticmethod
    def format_schema(schema:list)->str:
        pass


if __name__=="__main__":
    load_dotenv()
    db_host = str(os.getenv("DATABASE_HOST"))
    db_username = str(os.getenv("DATABASE_USERNAME"))
    db_password = str(os.getenv("DATABASE_PASSWORD"))
    db_name = str(os.getenv("DATABASE_NAME"))

    db_config = {
        'host': db_host,
        'user': db_username,
        'password': db_password,
        'database': db_name
    }

    connector=DatabaseConnector(db_config)

    schema=connector.get_table_schema("padron_test")

    print(schema)
