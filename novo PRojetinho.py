import feedparser
import csv
import json

def fetch_news(feed_url):
    """
    Coleta as notícias do feed RSS fornecido.
    """
    feed = feedparser.parse(feed_url)
    news_items = []
    for entry in feed.entries:
        title = entry.title
        link = entry.link
        published = entry.get('published', 'Data não disponível')
        news_items.append({'title': title, 'link': link, 'published': published})
    return news_items

def save_to_csv(news_items, filename='news.csv'):
    """
    Salva a lista de notícias em um arquivo CSV.
    """
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['title', 'link', 'published']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for item in news_items:
                writer.writerow(item)
        print(f"Resultados salvos em {filename}")
    except Exception as e:
        print(f"Erro ao salvar CSV: {e}")

def save_to_json(news_items, filename='news.json'):
    """
    Salva a lista de notícias em um arquivo JSON.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(news_items, jsonfile, ensure_ascii=False, indent=4)
        print(f"Resultados salvos em {filename}")
    except Exception as e:
        print(f"Erro ao salvar JSON: {e}")

def main():
    feed_url = 'https://g1.globo.com/Rss2/0,,AS0-5597,00.xml'  # Feed principal do G1
    news_items = fetch_news(feed_url)
    if news_items:
        print("\nÚltimas notícias:")
        for item in news_items:
            print(f"Título: {item['title']}")
            print(f"Link: {item['link']}")
            print(f"Publicado em: {item['published']}")
            print("-" * 40)
        
        opcao = input("\nDeseja salvar os resultados em (1) CSV ou (2) JSON? (Digite 1 ou 2): ").strip()
        if opcao == '1':
            save_to_csv(news_items)
        elif opcao == '2':
            save_to_json(news_items)
        else:
            print("Opção inválida. Saindo sem salvar.")
    else:
        print("Nenhuma notícia encontrada.")

if __name__ == '__main__':
    main()
