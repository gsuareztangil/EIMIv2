import sqlite3
import os


def database_init():
    # Conectar a la base de datos o la creamos si no existe
    conn = sqlite3.connect(os.getenv('DATABASE_NAME'))
    cursor = conn.cursor()

    # Creamos la tabla si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS samples_analysis (
            hash varchar(50) NOT NULL PRIMARY KEY,
            name varchar(50) NULL,
            dynamic_anal text NULL,
            family_name text NULL,
            architecture varchar(30) NULL,
            static_anal text NULL,
            date date NULL)
    ''')

    # Guardar los cambios y cerramos la conexion
    conn.commit()
    conn.close()
