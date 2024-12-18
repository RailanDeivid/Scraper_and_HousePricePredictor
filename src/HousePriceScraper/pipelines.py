import os
from dotenv import load_dotenv
import psycopg2


# Carregar as variáveis do arquivo .env
load_dotenv()

class PostgreSQLPipeline:
    def __init__(self):
        # Conexão com o banco de dados usando variáveis de ambiente
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST_PROD"),
            port=os.getenv("DB_PORT_PROD"),
            dbname=os.getenv("DB_NAME_PROD"),
            user=os.getenv("DB_USER_PROD"),
            password=os.getenv("DB_PASS_PROD")
        )
        self.cur = self.conn.cursor()
        self.create_table()

    def create_table(self):
        # Cria a tabela se ela não existir
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS house_prices (
            id SERIAL PRIMARY KEY,
            title TEXT,
            price VARCHAR(20),
            bedrooms TEXT,
            bathrooms TEXT,
            sqm TEXT,
            state VARCHAR(20),
            source TEXT
        )
        """)
        self.conn.commit()

    def process_item(self, item, spider):
        try:
            # Inserir dados no banco de dados
            self.cur.execute(
                """
                INSERT INTO house_prices (
                    title, price, bedrooms, bathrooms, sqm, state, source
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    item.get('title'), item.get('price'),
                    item.get('bedrooms'), item.get('bathrooms'), item.get('sqm'),
                    item.get('state'), item.get('source')
                )
            )
            self.conn.commit()
        except psycopg2.Error as e:
            spider.logger.error(f"Erro ao inserir no banco de dados: {e}")
        return item

    def remove_duplicates(self):
        try:
            # Remove registros duplicados com base em todas as colunas 
            self.cur.execute("""
            DELETE FROM house_prices
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM house_prices
                GROUP BY title, price, bedrooms, bathrooms, sqm, state, source
            )
            """)
            self.conn.commit()
        except psycopg2.Error as e:
            print(f"Erro ao remover duplicados: {e}")

    def close_spider(self, spider):
        # Remover duplicados antes de fechar a conexão
        self.remove_duplicates()
        # Fechar o cursor e a conexão ao final
        self.cur.close()
        self.conn.close()
