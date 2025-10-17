import feedparser
import pandas as pd
from datetime import datetime
import yaml
import re

class NewsMonitor:
    def __init__(self, config_path="config/config.yaml"):
        with open(config_path, 'r', encoding='utf-8') as file:
            self.config = yaml.safe_load(file)
        
        self.keywords = self.config['scout']['target_materials']

    def analyze_sentiment(self, text):
        """Простой анализ тональности текста"""
        if not text:
            return 0
            
        text_lower = text.lower()
        
        positive_words = [
            'рост', 'снижение', 'увеличился', 'дешевеет', 'улучшение',
            'развитие', 'инвестиции', 'строительство', 'развитие'
        ]
        
        negative_words = [
            'подорожание', 'кризис', 'дефицит', 'забастовка', 'проблемы',
            'задержки', 'срыв', 'конфликт', 'санкции'
        ]
        
        positive_score = sum(1 for word in positive_words if word in text_lower)
        negative_score = sum(1 for word in negative_words if word in text_lower)
        
        return positive_score - negative_score

    def extract_material_mentions(self, text):
        """Извлечение упоминаний материалов в тексте"""
        mentions = []
        for material in self.keywords:
            # Простой поиск по ключевым словам
            material_keywords = material.lower().split()
            if any(keyword in text.lower() for keyword in material_keywords):
                mentions.append(material)
        
        return mentions

    def get_industry_news(self):
        """Получение и анализ новостей строительной отрасли"""
        news_items = []
        
        for feed_url in self.config['scout']['news_feeds']:
            try:
                print(f"Проверка ленты: {feed_url}")
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:10]:  # Берем последние 10 новостей
                    title = entry.get('title', '')
                    summary = entry.get('summary', '')
                    published = entry.get('published', '')
                    
                    full_text = f"{title} {summary}"
                    
                    # Анализируем материал
                    mentions = self.extract_material_mentions(full_text)
                    sentiment = self.analyze_sentiment(full_text)
                    
                    if mentions:  # Сохраняем только релевантные новости
                        news_items.append({
                            'title': title,
                            'summary': summary[:200] + '...' if len(summary) > 200 else summary,
                            'published': published,
                            'mentions': mentions,
                            'sentiment': sentiment,
                            'source': feed_url,
                            'date_collected': datetime.now()
                        })
                
            except Exception as e:
                print(f"Ошибка при обработке ленты {feed_url}: {e}")
                continue
        
        return pd.DataFrame(news_items)

    def get_critical_news(self):
        """Получение критически важных новостей"""
        news_df = self.get_industry_news()
        
        # Критическими считаем новости с негативным сентиментом
        critical_news = news_df[news_df['sentiment'] < -1]
        
        return critical_news

if __name__ == "__main__":
    monitor = NewsMonitor()
    news = monitor.get_industry_news()
    print(f"Найдено {len(news)} релевантных новостей")
    print(news[['title', 'mentions', 'sentiment']].head())