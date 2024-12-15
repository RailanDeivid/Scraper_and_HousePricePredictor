# usa uma imagem base do Python
FROM python:3.12-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo requirements.txt para o diretório de trabalho
COPY requirements.txt .

# Instala as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante dos arquivos do projeto para o diretório de trabalho
COPY . .

# expoe a posrta do postgres
EXPOSE 5432

# Definir o comando para rodar o Scrapy no diretório correto
CMD ["scrapy", "crawl", "HousePriceScraper"]
