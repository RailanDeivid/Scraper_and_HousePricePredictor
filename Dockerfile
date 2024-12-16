# Usa uma imagem base do Python
FROM python:3.10.9-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app/src

# Instalar dependências do sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    build-essential \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copia o arquivo requirements.txt para o diretório de trabalho
COPY src/requirements.txt .

# Instala as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Copia apenas a pasta 'src' onde está o scrapy.cfg e o projeto
COPY src /app/src

# Expõe a porta do Postgres (se necessário para sua aplicação)
EXPOSE 5432

# Define o comando para rodar o Scrapy
CMD ["scrapy", "crawl", "HousePriceScraper"]



