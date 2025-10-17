import requests
from bs4 import BeautifulSoup
import time
import random
import re
from urllib.parse import quote, urljoin
from datetime import datetime
from fake_useragent import UserAgent

class WebPriceParser:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.ua = UserAgent()
        self.update_headers()

    def update_headers(self):
        """Обновление заголовков"""
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def search_product(self, supplier_name, product_name):
        """Реальный поиск товара в магазине"""
        supplier_config = self.config['scout']['suppliers'].get(supplier_name)
        if not supplier_config:
            return None
        
        try:
            # Кодируем запрос для URL
            search_query = quote(product_name)
            search_url = supplier_config['search_url'].format(query=search_query)
            
            print(f"🔍 Ищем '{product_name}' в {supplier_name}...")
            
            response = self.session.get(
                search_url, 
                timeout=self.config['scout']['parser_settings']['timeout']
            )
            response.raise_for_status()
            
            # Парсим результаты
            products = self.parse_real_search_results(response.text, supplier_config, product_name)
            
            if products:
                print(f"   ✅ Найдено {len(products)} товаров")
            else:
                print(f"   ❌ Товары не найдены")
            
            return products
            
        except Exception as e:
            print(f"   ❌ Ошибка поиска в {supplier_name}: {e}")
            return None

    def parse_real_search_results(self, html, supplier_config, original_query):
        """Парсинг реальных результатов поиска"""
        soup = BeautifulSoup(html, 'html.parser')
        selectors = supplier_config['selectors']
        
        products = []
        
        # Ищем товары по селектору карточки товара
        product_cards = soup.select(selectors['product_card'])
        
        for card in product_cards[:self.config['scout']['parser_settings']['max_products_per_search']]:
            try:
                product_data = self.extract_real_product_data(card, selectors, supplier_config['base_url'])
                if product_data and self.is_relevant_product(product_data['name'], original_query):
                    products.append(product_data)
            except Exception as e:
                continue
        
        return products

    def extract_real_product_data(self, product_element, selectors, base_url):
        """Извлечение реальных данных о товаре"""
        # Название товара
        title_element = product_element.select_one(selectors['product_title'])
        if not title_element:
            return None
            
        product_name = title_element.get_text(strip=True)
        
        # Цена товара
        price = self.extract_real_price(product_element, selectors)
        if not price:
            return None
            
        # Ссылка на товар
        link_element = product_element.select_one(selectors['product_link'])
        if link_element and link_element.get('href'):
            product_url = link_element.get('href')
            if not product_url.startswith('http'):
                product_url = urljoin(base_url, product_url)
        else:
            product_url = ""
        
        return {
            'name': product_name,
            'price': price,
            'url': product_url,
            'date_found': datetime.now()
        }

    def extract_real_price(self, product_element, selectors):
        """Извлечение реальной цены"""
        price_text = ""
        
        # Пробуем разные селекторы цены
        price_selectors = [
            selectors['product_price'],
            'span.price',
            'div.price',
            'meta[itemprop="price"]',
            'span[class*="price"]',
            'div[class*="price"]'
        ]
        
        for selector in price_selectors:
            price_element = product_element.select_one(selector)
            if price_element:
                if price_element.get('content'):  # Для meta тегов
                    price_text = price_element.get('content')
                else:
                    price_text = price_element.get_text(strip=True)
                if price_text:
                    break
        
        return self.clean_price(price_text)

    def clean_price(self, price_text):
        """Очистка и преобразование цены в число"""
        if not price_text:
            return None
            
        # Удаляем всё кроме цифр
        cleaned = re.sub(r'[^\d]', '', str(price_text))
        
        try:
            return float(cleaned)
        except ValueError:
            return None

    def is_relevant_product(self, product_name, search_query):
        """Проверка релевантности товара запросу"""
        search_words = search_query.lower().split()
        product_name_lower = product_name.lower()
        
        # Ключевые слова для исключения
        exclude_words = ['аксессуар', 'инструмент', 'кисть', 'валик', 'перчатк']
        
        # Проверяем на исключения
        if any(exclude in product_name_lower for exclude in exclude_words):
            return False
        
        # Считаем количество совпадающих слов
        matches = sum(1 for word in search_words if word in product_name_lower)
        
        return matches >= len(search_words) * 0.3  # 30% совпадений достаточно

    def parse_all_prices(self, selected_city=None):
        """Парсинг цен по всем товарам и магазинам с фильтром по городу"""
        all_prices = []
        settings = self.config['scout']['parser_settings']
        
        for supplier_name, supplier_config in self.config['scout']['suppliers'].items():
            # Фильтр по городу
            if selected_city and selected_city not in supplier_config['regions']:
                print(f"⏭️  Пропускаем {supplier_name} (не в {selected_city})")
                continue
            
            print(f"\n🏪 Парсим {supplier_name} ({supplier_config['city']})...")
            
            for material in self.config['scout']['target_materials']:
                try:
                    products = self.search_product(supplier_name, material)
                    
                    if products:
                        # Берем товар с минимальной ценой
                        best_product = min(products, key=lambda x: x['price'])
                        
                        all_prices.append({
                            'material': material,
                            'supplier': supplier_name,
                            'price': best_product['price'],
                            'product_name': best_product['name'],
                            'url': best_product['url'],
                            'city': supplier_config['city'],
                            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                        
                        print(f"   ✅ {material}: {best_product['price']} руб. - {best_product['name'][:50]}...")
                    else:
                        print(f"   ❌ {material}: не найден")
                    
                    # Случайная задержка между запросами
                    delay = settings['delay_between_requests'] + random.uniform(0.5, 1.5)
                    time.sleep(delay)
                    
                    # Обновляем User-Agent каждые 5 запросов
                    if len(all_prices) % 5 == 0:
                        self.update_headers()
                    
                except Exception as e:
                    print(f"   💥 {material}: ошибка - {e}")
                    continue
        
        return all_prices

    def get_available_cities(self):
        """Получение списка доступных городов"""
        cities = set()
        for supplier_config in self.config['scout']['suppliers'].values():
            cities.update(supplier_config['regions'])
        return sorted(list(cities))