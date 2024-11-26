import scrapy
from datetime import datetime
import re

class HousepricescrapermlSpider(scrapy.Spider):
    # Nome do spider
    name = "HousePriceScraperML"
    
    # Lista de estados brasileiros (UF) para coletar os dados
    list_UF = [
                'acre','alagoas', 'amazonas', 'bahia', 'ceara', 'distrito-federal', 'espirito-santo', 'goias', 'maranhao'
                'mato-grosso', 'mato-grosso-do-sul', 'minas-gerais', 'para', 'parana', 'piaui', 'paraiba', 'pernambuco', 
                'rio-de-janeiro', 'rio-grande-do-sul', 'rondonia', 'santa-catariana', 'sao-paulo', 'sergipe', 'tocantins']
    
    # Inicializa uma lista vazia para armazenar as URLs iniciais
    start_urls = []

    def __init__(self):
        # Constrói as URLs para cada estado e adiciona à lista de start_urls
        for uf in self.list_UF:
            url = f"https://imoveis.mercadolivre.com.br/casas/venda/{uf}/"
            self.start_urls.append(url)
    
    # Contador de páginas   para controle da paginação
    page_count = 1
    # Número máximo de páginas a serem coletadas por estado
    max_pages = 50

    def parse(self, response):
        # Seleciona todos os anúncios na página atual
        anuncios = response.css('div.poly-card__content')

        # Para cada anúncio, extrai informações básicas
        for anuncio in anuncios:
            link = anuncio.css('h2.poly-box.poly-component__title a::attr(href)').get()  # Link para o anúncio detalhado
            title = anuncio.css('h2.poly-box.poly-component__title a::text').get()  # Título do anúncio
            location = response.css('span.poly-component__location::text').get()  # Localização do imóvel

            # Verifica se o link e o título existem antes de continuar
            if link and title:
                yield response.follow(
                    link,  # Segue o link para a página detalhada do anúncio
                    self.parse_anuncio,  # Chama a função parse_anuncio para processar a página detalhada
                    meta={
                        'date_colect': datetime.now().date(),  # Data de coleta
                        'uf': response.url.split('/')[-2],  # Extrai a UF da URL
                        'title': title.strip(),  # Título do anúncio (removendo espaços extras)
                        'location': location  # Localização do imóvel
                    }
                )

        # Verifica se há uma próxima página e se o limite de páginas não foi atingido
        if self.page_count < self.max_pages:
            next_page = response.css('li.andes-pagination__button.andes-pagination__button--next a::attr(href)').get()
            if next_page:
                self.page_count += 1  # Incrementa o contador de páginas
                yield scrapy.Request(url=next_page, callback=self.parse)

    def parse_anuncio(self, response):
        # Extrai detalhes básicos do anúncio
        source = response.url  # URL da página do anúncio
        data_coleta = response.meta['date_colect']  # Data de coleta passada via meta
        uf = response.meta['uf']  # UF extraída do meta
        title = response.meta['title']  # Título extraído do meta
        location = response.meta['location']  # Localização extraída do meta
        
        # Extrai o preço do imóvel
        price = response.css('span.andes-money-amount__fraction::text').get()
        
        # Extrai o número de quartos
        bedrooms = response.xpath("//span[contains(text(), 'quarto')]/text()").get()
        bedrooms = re.search(r"\d+", bedrooms).group() if bedrooms else None  # Extrai o número dos quartos se encontrado

        # Extrai o número de banheiros
        bathrooms = response.xpath("//span[contains(text(), 'banheiro')]/text()").get()
        bathrooms = re.search(r"\d+", bathrooms).group() if bathrooms else None  # Extrai o número dos banheiros se encontrado

        # Extrai a metragem total (em m²)
        sqm = response.xpath("//span[contains(text(), 'm² totais')]/text()").get()
        sqm = re.search(r"\d+", sqm).group() if sqm else None  # Extrai o número da metragem se encontrado

        # Armazena os dados em um dicionário e os retorna
        yield {
            'data_coleta': data_coleta,  # Data de coleta
            'title': title,  # Título do anúncio
            'price': price,  # Preço do imóvel
            'bedrooms': bedrooms,  # Número de quartos
            'bathrooms': bathrooms,  # Número de banheiros
            'sqm': sqm,  # Metragem total
            'location': location,  # Localização
            'uf': uf,  # Estado (UF)
            'source': source  # URL do anúncio
        }
