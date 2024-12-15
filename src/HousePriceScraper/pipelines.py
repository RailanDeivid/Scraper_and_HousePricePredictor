import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Text, Table, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError


# Carregar variáveis do arquivo .env
load_dotenv()

# Carregar as variáveis de ambiente
host = os.getenv("DB_HOST_PROD")
port = "5432"
dbname = os.getenv("DB_NAME_PROD")
user = os.getenv("DB_USER_PROD")
password = os.getenv("DB_PASS_PROD")

class PostgreSQLPipeline:
    def __init__(self):
        # Configurar conexão com o banco de dados
        database_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
        self.session = None

        # Criação da tabela usando SQLAlchemy
        self.metadata = MetaData()
        self.house_prices_table = Table(
            'house_prices', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('title', Text),
            Column('price', String(20)),
            Column('bedrooms', Text),
            Column('bathrooms', Text),
            Column('sqm', Text),
            Column('location', Text),
            Column('state', String(20)),
            Column('source', Text)
        )
        self.metadata.create_all(self.engine)

    def open_spider(self, spider):
        # Abrir sessão ao iniciar o spider
        self.session = self.Session()

    def process_item(self, item, spider):
        try:
            # Inserir item na tabela
            insert_stmt = self.house_prices_table.insert().values(
                title=item.get('title'),
                price=item.get('price'),
                bedrooms=item.get('bedrooms'),
                bathrooms=item.get('bathrooms'),
                sqm=item.get('sqm'),
                location=item.get('location'),
                state=item.get('state'),
                source=item.get('source')
            )
            self.session.execute(insert_stmt)
            self.session.commit()
        except SQLAlchemyError as e:
            spider.logger.error(f"Erro ao inserir no banco de dados: {e}")
            self.session.rollback()
        return item

    def remove_duplicates(self):
        try:
            # Remover registros duplicados com base em todas as colunas exceto o id
            with self.engine.connect() as conn:
                conn.execute(
                    Text("""
                    DELETE FROM house_prices
                    WHERE id NOT IN (
                        SELECT MIN(id)
                        FROM house_prices
                        GROUP BY title, price, bedrooms, bathrooms, sqm, location, state, source
                    )
                    """))
        except SQLAlchemyError as e:
            print(f"Erro ao remover duplicados: {e}")

    def close_spider(self, spider):
        # Remover duplicados antes de fechar a conexão
        self.remove_duplicates()
        # Fechar a sessão ao final
        if self.session:
            self.session.close()
