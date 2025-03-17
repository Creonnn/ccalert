import sqlite3
from tabulate import tabulate
import re
from config import Config as conf

class DB:

    @staticmethod
    def update(stmt: str, new: tuple) -> None:
        conn = sqlite3.connect(conf.db_path)
        cursor = conn.cursor()
        cursor.execute(stmt, new)
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def insert(stmt, new):
        conn = sqlite3.connect(conf.db_path)
        cursor = conn.cursor()
        cursor.execute(stmt, new)
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def get_query(stmt):
        conn = sqlite3.connect(conf.db_path)
        cursor = conn.cursor()
        cursor.execute(stmt)
        query = cursor.fetchall()
        cursor.close()
        conn.close()
        return query
    
    @staticmethod
    def get_query_table(stmt):
        try:
            conn = sqlite3.connect(conf.db_path)
            cursor = conn.cursor()
            cursor.execute(stmt)
            rows = cursor.fetchall()
            headers = [desc[0] for desc in cursor.description]
            cursor.close()
            table = tabulate(rows, headers=headers, tablefmt="plain")[:4090]
            message = f"```{table}```"
        except sqlite3.OperationalError as e:
            message = f"OperationalError: {e}"

        except sqlite3.IntegrityError as e:
            message = f"IntegrityError: {e}"

        except sqlite3.DatabaseError as e:
            message = f"DatabaseError: {e}"

        except Exception as e:
            message = f"General Error: {e}"

        finally:
            conn.close() 

        return message
    
    @staticmethod
    def get_top_sku_table(stmt):
        conn = sqlite3.connect(conf.db_path)
        cursor = conn.cursor()
        cursor.execute(stmt)
        rows = cursor.fetchall()
        headers = [desc[0] for desc in cursor.description]
        cursor.close()
        new_rows=[]
        for i, row in enumerate(rows):
            model = row[0]
            quantity = row[1]
            truncated_model = re.sub(conf.truncate_patterns, '', model, flags=re.IGNORECASE)
            truncated_model = re.sub(r"\s+", " ", truncated_model).strip()
            new_rows.append([truncated_model, quantity])
        table = tabulate(new_rows, headers=headers, tablefmt="plain")[:4096]
        message = f"```{table}```"
        return message