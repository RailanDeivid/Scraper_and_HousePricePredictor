import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

# Carregar as variáveis do arquivo .env
load_dotenv()

class PostgreSQLPipeline:
    def __init__(self):
        # Verificar se as variáveis de ambiente estão definidas
        self.db_host = os.getenv("DB_HOST_PROD")
        self.db_port = os.getenv("DB_PORT_PROD")
        self.db_name = os.getenv("DB_NAME_PROD")
        self.db_user = os.getenv("DB_USER_PROD")
        self.db_pass = os.getenv("DB_PASS_PROD")

        if not all([self.db_host, self.db_port, self.db_name, self.db_user, self.db_pass]):
            raise ValueError("Faltam variáveis de ambiente para a conexão com o banco de dados")

        # Conexão com o banco de dados usando variáveis de ambiente
        try:
            self.conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                dbname=self.db_name,
                user=self.db_user,
                password=self.db_pass
            )
            self.cur = self.conn.cursor()
            self.create_table()
        except psycopg2.Error as e:
            raise Exception(f"Erro ao conectar com o banco de dados: {e}")

    def create_table(self):
        # Cria a tabela se ela não existir
        try:
            self.cur.execute("""
            CREATE TABLE IF NOT EXISTS house_prices (
                id SERIAL PRIMARY KEY,
                title TEXT,
                price VARCHAR(20),
                bedrooms TEXT,
                bathrooms TEXT,
                sqm TEXT,
                location TEXT,
                state VARCHAR(20),
                source TEXT
            )
            """)
            self.conn.commit()
        except psycopg2.Error as e:
            raise Exception(f"Erro ao criar tabela: {e}")

    def process_item(self, item, spider):
        try:
            # Inserir dados no banco de dados
            self.cur.execute(
                """
                INSERT INTO house_prices (
                    title, price, bedrooms, bathrooms, sqm, location, state, source
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    item.get('title'), item.get('price'),
                    item.get('bedrooms'), item.get('bathrooms'), item.get('sqm'),
                    item.get('location'), item.get('state'), item.get('source')
                )
            )
            self.conn.commit()
        except psycopg2.Error as e:
            spider.logger.error(f"Erro ao inserir no banco de dados: {e}")
        return item

    def remove_duplicates(self):
        try:
            # Remove registros duplicados com base em todas as colunas exceto o id
            self.cur.execute("""
            DELETE FROM house_prices
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM house_prices
                GROUP BY title, price, bedrooms, bathrooms, sqm, location, state, source
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
