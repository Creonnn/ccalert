import sqlite3
from bs4 import BeautifulSoup
import requests
from db import DB
from config import Config as conf

def add_new_sku(urls, gpu):
    """
    Adds new SKU to DB.
    """
    id_bound_stmt = "SELECT id FROM products ORDER BY id DESC LIMIT 1"
    model_id_lower_bound = DB.get_query(id_bound_stmt)[0][0]

    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        model = soup.find("meta", attrs={"name": "description"})["content"]

        stmt = ("INSERT INTO products (model, gpu, url) "
                                            "VALUES (?, ?, ?)")
        data = (model, gpu, url)
        DB.insert(stmt, data)

    conn = sqlite3.connect(conf.db_path)
    cursor = conn.cursor()
    cursor.execute(f"""
        INSERT INTO in_stock (model_id, region, quantity)
        SELECT products.id, locations.region, 0
        FROM products
        CROSS JOIN locations 
        WHERE products.id>{model_id_lower_bound}
    """)
    cursor.close()
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    pass