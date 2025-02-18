import csv
import os
import re
import logging
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TwitterScraper:
    def __init__(self, query: str, cookies_path: str = "twitter_cookies.json", csv_file: str = "tweets.csv"):
        """
        Inicializa el scraper de Twitter.

        Args:
            query (str): Término de búsqueda en Twitter.
            cookies_path (str, optional): Ruta al archivo de cookies. Se usará para mantener la sesión.
            csv_file (str, optional): Ruta al archivo CSV donde se guardarán los tweets.
        """
        self.query = query
        self.cookies_path = cookies_path
        self.csv_file = csv_file
        self.existing_tweets = set()
        self.tweet_data = []

    def load_existing_tweets(self):
        """Carga los tweets existentes del CSV para evitar duplicados."""
        if os.path.exists(self.csv_file):
            with open(self.csv_file, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.existing_tweets.add((row["tweet"], row["link"]))

    def save_tweets(self):
        """Guarda los tweets extraídos en el archivo CSV."""
        fieldnames = ["tweet", "link", "usuario", "query", "likes", "retweets", "views", "hashtags", "comments"]
        file_exists = os.path.exists(self.csv_file)
        with open(self.csv_file, "a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if not file_exists or os.stat(self.csv_file).st_size == 0:
                writer.writeheader()
            for row in self.tweet_data:
                writer.writerow({
                    "tweet": row["tweet"],
                    "link": row["link"],
                    "usuario": row["usuario"],
                    "query": row["query"],
                    "likes": row["likes"],
                    "retweets": row["retweets"],
                    "views": row["views"],
                    "hashtags": " | ".join(row["hashtags"]),
                    "comments": " | ".join(row["comments"])
                })

    def run(self):
        """Ejecuta el proceso de scraping en Twitter."""
        self.load_existing_tweets()
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            if os.path.exists(self.cookies_path):
                context = browser.new_context(storage_state=self.cookies_path)
            else:
                context = browser.new_context()

            page = context.new_page()
            search_url = f"https://twitter.com/search?q={self.query.replace(' ', '%20')}&src=typed_query&f=live"
            logging.info(f"Accediendo a: {search_url}")
            page.goto(search_url)

            try:
                page.wait_for_selector('div[data-testid="tweetText"]', timeout=60000)
                tweets_locator = page.locator('div[data-testid="tweetText"]')
                links_locator = page.locator('a[role="link"][href^="/"]')

                for i in range(tweets_locator.count()):
                    tweet_text = tweets_locator.nth(i).inner_text()
                    href = links_locator.nth(i).get_attribute('href')
                    link = f"https://twitter.com{href}" if href else "Link no disponible"
                    if (tweet_text, link) not in self.existing_tweets:
                        parts = link.split("/")
                        usuario = parts[3] if len(parts) > 3 else "Usuario no disponible"
                        hashtags = re.findall(r"(#\w+)", tweet_text)
                        tweet_item = {
                            "tweet": tweet_text,
                            "link": link,
                            "usuario": usuario,
                            "query": self.query,
                            "likes": "",
                            "retweets": "",
                            "views": "",
                            "hashtags": hashtags,
                            "comments": []
                        }
                        self.tweet_data.append(tweet_item)
                        self.existing_tweets.add((tweet_text, link))

                # Para cada tweet, se accede a su página individual para extraer datos adicionales.
                for tweet in self.tweet_data:
                    page.goto(tweet["link"])
                    if page.url != tweet["link"]:
                        logging.info(f"Redirigido al intentar acceder a {tweet['link']}. Ignorando.")
                        continue
                    try:
                        page.wait_for_selector('div[data-testid="tweetText"]', timeout=60000)

                        # Extraer likes
                        try:
                            like_selector = 'div[data-testid="like"] span'
                            likes = page.locator(like_selector).nth(0).inner_text() if page.locator(like_selector).count() > 0 else "0"
                        except Exception:
                            likes = "Likes no disponibles"
                        tweet["likes"] = likes

                        # Extraer retweets
                        try:
                            retweet_selector = 'div[data-testid="retweet"] span'
                            retweets = page.locator(retweet_selector).nth(0).inner_text() if page.locator(retweet_selector).count() > 0 else "0"
                        except Exception:
                            retweets = "Reposts no disponibles"
                        tweet["retweets"] = retweets

                        # Extraer views
                        try:
                            view_selector = 'div[data-testid="viewCount"] span'
                            views = page.locator(view_selector).nth(0).inner_text() if page.locator(view_selector).count() > 0 else "0"
                        except Exception:
                            views = "Visitas no disponibles"
                        tweet["views"] = views

                        # Extraer comentarios (se ignora el primer div que corresponde al tweet original)
                        comments_locator = page.locator('div[data-testid="tweetText"]')
                        tweet["comments"] = [comments_locator.nth(j).inner_text() for j in range(1, comments_locator.count())]
                    except Exception as e:
                        logging.error(f"No se pudieron cargar los datos para {tweet['link']}: {e}")
                        tweet["likes"] = "Likes no disponibles"
                        tweet["retweets"] = "Reposts no disponibles"
                        tweet["views"] = "Visitas no disponibles"
                        tweet["comments"] = []

                self.save_tweets()
                logging.info(f"Se han añadido {len(self.tweet_data)} tweets nuevos al archivo '{self.csv_file}'.")
            except Exception as e:
                logging.error(f"Error: {e}")
                page.screenshot(path="error_screenshot.png")

            # Guardar el estado de las cookies para futuros usos
            context.storage_state(path=self.cookies_path)
            context.browser.close()

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    query = "deslave Baños Rio Verde Tungurahua"
    scraper = TwitterScraper(query)
    scraper.run()

if __name__ == "__main__":
    main()
