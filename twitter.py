import csv
import os
import re
from playwright.sync_api import sync_playwright

def scrape_twitter(query):
    # Cargar los tweets existentes en el archivo CSV para evitar duplicados
    existing_tweets = set()
    if os.path.exists("tweets.csv"):
        with open("tweets.csv", "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                existing_tweets.add((row["tweet"], row["link"]))  # Identificador único

    with sync_playwright() as p:
        # Si existen cookies guardadas, se usa el estado de almacenamiento
        if os.path.exists("twitter_cookies.json"):
            context = p.chromium.launch(headless=False).new_context(storage_state="twitter_cookies.json")
        else:
            context = p.chromium.launch(headless=False).new_context()

        page = context.new_page()

        # Construir la URL de búsqueda
        url = f"https://twitter.com/search?q={query.replace(' ', '%20')}&src=typed_query&f=live"
        page.goto(url)

        try:
            # Esperar a que se carguen los tweets
            page.wait_for_selector('div[data-testid="tweetText"]', timeout=60000)
            tweets_locator = page.locator('div[data-testid="tweetText"]')
            links_locator = page.locator('a[role="link"][href^="/"]')
            
            tweet_data = []
            for i in range(tweets_locator.count()):
                tweet_text = tweets_locator.nth(i).inner_text()
                href = links_locator.nth(i).get_attribute('href')
                link = f"https://twitter.com{href}" if href else "Link no disponible"
                if (tweet_text, link) not in existing_tweets:
                    # Extraer el usuario desde la URL, asumiendo que la estructura es "twitter.com/usuario/status/..."
                    parts = link.split("/")
                    usuario = parts[3] if len(parts) > 3 else "Usuario no disponible"
                    hashtags = re.findall(r"(#\w+)", tweet_text)
                    
                    tweet_data.append({
                        "tweet": tweet_text,
                        "link": link,
                        "usuario": usuario,
                        "query": query,
                        "likes": "",
                        "retweets": "",
                        "views": "",
                        "hashtags": hashtags,
                        "comments": []
                    })
                    existing_tweets.add((tweet_text, link))

            # Para cada tweet, acceder a su página individual y extraer likes, retweets, views y comentarios
            for tweet in tweet_data:
                page.goto(tweet["link"])
                if page.url != tweet["link"]:
                    print(f"Redirigido al intentar acceder a {tweet['link']}. Ignorando.")
                    continue
                try:
                    page.wait_for_selector('div[data-testid="tweetText"]', timeout=60000)
                    
                    # Extraer likes
                    try:
                        like_selector = 'div[data-testid="like"] span'
                        if page.locator(like_selector).count() > 0:
                            likes = page.locator(like_selector).nth(0).inner_text()
                        else:
                            likes = "0"
                    except Exception as e:
                        likes = "Likes no disponibles"
                    tweet["likes"] = likes

                    # Extraer retweets (reposts)
                    try:
                        retweet_selector = 'div[data-testid="retweet"] span'
                        if page.locator(retweet_selector).count() > 0:
                            retweets = page.locator(retweet_selector).nth(0).inner_text()
                        else:
                            retweets = "0"
                    except Exception as e:
                        retweets = "Reposts no disponibles"
                    tweet["retweets"] = retweets

                    # Extraer views (veces visitada la publicación)
                    try:
                        view_selector = 'div[data-testid="viewCount"] span'
                        if page.locator(view_selector).count() > 0:
                            views = page.locator(view_selector).nth(0).inner_text()
                        else:
                            views = "0"
                    except Exception as e:
                        views = "Visitas no disponibles"
                    tweet["views"] = views

                    # Extraer comentarios: se ignora el primer div que corresponde al tweet original
                    comments_locator = page.locator('div[data-testid="tweetText"]')
                    tweet["comments"] = [comments_locator.nth(j).inner_text() 
                                           for j in range(1, comments_locator.count())]

                except Exception as e:
                    print(f"No se pudieron cargar los datos para {tweet['link']}: {e}")
                    tweet["likes"] = "Likes no disponibles"
                    tweet["retweets"] = "Reposts no disponibles"
                    tweet["views"] = "Visitas no disponibles"
                    tweet["comments"] = []

            # Guardar los datos en CSV (se añade al archivo existente)
            fieldnames = ["tweet", "link", "usuario", "query", "likes", "retweets", "views", "hashtags", "comments"]
            file_exists = os.path.exists("tweets.csv")
            with open("tweets.csv", "a", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                if not file_exists or os.stat("tweets.csv").st_size == 0:
                    writer.writeheader()
                for row in tweet_data:
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

            print(f"Se han añadido {len(tweet_data)} tweets nuevos con comentarios, likes, reposts y visitas al archivo 'tweets.csv'.")
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="error_screenshot.png")

        # Guardar el estado de las cookies para futuros usos
        context.storage_state(path="twitter_cookies.json")
        context.browser.close()

# Ejecuta la función con la búsqueda deseada
scrape_twitter("deslave Baños Rio Verde Tungurahua")
