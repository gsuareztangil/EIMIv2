import dotenv
from pathlib import Path
import re
import ipaddress
import sqlite3
from datetime import date
from termcolor import colored
import json
import functools
import requests
import os
def load_env_file():
    env_path = Path('..') / '.env'
    dotenv.load_dotenv(dotenv_path=env_path)

def store_static_fields(tuple_args):
    try:
        # Connection
        sqliteConnection = sqlite3.connect(os.getenv('DATABASE_NAME'))
        cursor = sqliteConnection.cursor()

        # Execute query
        cursor.execute('INSERT INTO samples_analysis VALUES (?, ?, ?, ?, ?, ?, ?)', tuple_args)

        # Commit changes and close the connection
        sqliteConnection.commit()
        sqliteConnection.close()
    except sqlite3.Error as error:
        print(colored("[X] Failed to insert data into sqlite table: " + str(error).lower(), 'red'))


def get_data_bbdd(field, hash, table, mode):
    try:
        # Connection
        sqliteConnection = sqlite3.connect(os.getenv('DATABASE_NAME'))
        cursor = sqliteConnection.cursor()

        result = []

        # Execute query
        if mode == 'n_grams':
            cursor.execute("SELECT static_anal FROM samples_analysis WHERE hash != '" + hash + "';")
            type = 'opcodes_func'
        elif mode == 'cc':
            cursor.execute("SELECT static_anal FROM samples_analysis WHERE hash != '" + hash + "';")
            type = 'cc'
        else:
            cursor.execute("SELECT static_anal FROM samples_analysis WHERE hash != '" + hash + "';")
            type = 'dynamic'

        # Parse
        sample_data = cursor.fetchall()
        for i in sample_data:
            a = json.loads(i[0])
            data = dict()
            data['name'] = a['md5']
            data[type] = a[type]
            result.append(data)

        # Commit changes and close the connection
        sqliteConnection.commit()
        sqliteConnection.close()

        return result
    except sqlite3.Error as error:
        print(colored("[X] Failed to insert data into sqlite table: " + str(error).lower(), 'red'))

# get_data_bbdd('static_anal', '47e8f92ae8f428300b630ed62599203a', 'web_muestra', 'n_grams')
