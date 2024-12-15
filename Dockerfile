# # Usa uma imagem base do Python
# FROM python:3.10.9-slim

# # Define o diretório de trabalho dentro do container
# WORKDIR /app/src

# # Instalar dependências do sistema necessárias
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     libpq-dev \
#     gcc \
#     build-essential \
#     python3-dev \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# # Copia o arquivo requirements.txt para o diretório de trabalho
# COPY src/requirements.txt .

# # Instala as dependências do projeto
# RUN pip install --no-cache-dir -r requirements.txt

# # Copia apenas a pasta 'src' onde está o scrapy.cfg e o projeto
# COPY src /app/src

# # Expõe a porta do Postgres (se necessário para sua aplicação)
# EXPOSE 5432

# # Define o comando para rodar o Scrapy
# CMD ["scrapy", "crawl", "HousePriceScraper"]


# Usa uma imagem base do Python
FROM python:3.10.9-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app/src

# Instalar dependências do sistema necessárias, incluindo cron e tzdata para configurar o fuso horário
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    build-essential \
    python3-dev \
    cron \
    tzdata \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configura o fuso horário para o Brasil (Horário de Brasília)
RUN ln -fs /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime && dpkg-reconfigure --frontend noninteractive tzdata

# Copia o arquivo requirements.txt para o diretório de trabalho
COPY src/requirements.txt .

# Instala as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Copia apenas a pasta 'src' onde está o scrapy.cfg e o projeto
COPY src /app/src

# Expõe a porta do Postgres (se necessário para sua aplicação)
EXPOSE 5432

# Cria o arquivo cron para rodar o comando a cada 5 dias às 10h da manhã
RUN echo "0 10 */1 * * cd /app/src && scrapy crawl HousePriceScraper" > /etc/cron.d/scrapy-cron

# Dá permissões para o arquivo de cron
RUN chmod 0644 /etc/cron.d/scrapy-cron

# Aplica as permissões necessárias ao cron
RUN crontab /etc/cron.d/scrapy-cron

# Inicia o cron no contêiner
CMD ["cron", "-f"]


