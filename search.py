import openai

from settings import *
import requests
from requests.exceptions import RequestException
import pandas as pd
from storage import DBStorage
from datetime import datetime
from urllib.parse import quote_plus
import time

openai.api_key = OPENAI_API_KEY
# Add the following variable at the top of your code
OPENAI_REQUESTS_PER_MINUTE = 3
OPENAI_REQUESTS_PER_DAY = 200
OPENAI_RATE_LIMIT_PERIOD = 60  # 60 seconds in a minute


# Implement a rate limiter function for OpenAI
def rate_limit_openai_api():
    current_time = time.time()
    last_request_time = getattr(rate_limit_openai_api, 'last_request_time', 0)
    time_since_last_request = current_time - last_request_time
    if time_since_last_request < OPENAI_RATE_LIMIT_PERIOD:
        time.sleep(OPENAI_RATE_LIMIT_PERIOD - time_since_last_request)
    rate_limit_openai_api.last_request_time = time.time()


def openai_text_categorization(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use GPT-3.5-turbo chat model
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that categorizes text."
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )
    # Extract the category from the API response
    category = response['choices'][0]['message']['content'].strip()
    return category


def search_api(query, pages=int(RESULT_COUNT / 10)):
    results = []
    try:
        for i in range(0, pages):
            start = i * 10 + i
            url = SEARCH_URL.format(
                key=SEARCH_KEY,
                cx=SEARCH_ID,
                query=quote_plus(query),
                start=start
            )
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception if the request was unsuccessful
            data = response.json()
            # print("API Response:", data)

            # Check if the key 'items' exists in the data
            if 'items' in data:
                results += data["items"]
            else:
                print("Key 'items' not found in the API response.")
                # print("API Response:", response.text)  # Print the entire response for debugging

        # Classify each snippet using OpenAI and add the category to the results DataFrame
        categories = [openai_text_categorization(result["snippet"]) for result in results]
        for i, result in enumerate(results):
            result["category"] = categories[i]

    except requests.RequestException as e:
        print(f"Error occurred during API request: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of an API error

    res_df = pd.DataFrame.from_dict(results)

    if not res_df.empty:
        res_df["rank"] = list(range(1, res_df.shape[0] + 1))
        res_df = res_df[["link", "rank", "snippet", "title", "category"]]
    return res_df


def scrape_page(links):
    html = []
    for link in links:
        print(link)
        try:
            data = requests.get(link, timeout=5)
            html.append(data.text)
        except RequestException:
            html.append("")
    return html


def search(query):
    columns = ["query", "rank", "link", "title", "snippet", "html", "category", "created"]
    storage = DBStorage()

    stored_results = storage.query_results(query)
    if stored_results.shape[0] > 0:
        stored_results["created"] = pd.to_datetime(stored_results["created"])
        return stored_results[columns]

    print("No results in the database. Using the API.")
    results = search_api(query)
    html = scrape_page(results["link"])
    results["html"] = html
    results = results[results["html"].str.len() > 0].copy()
    results["query"] = query

    # Classify snippets using OpenAI and add the category to the results DataFrame
    results["category"] = results["snippet"].apply(openai_text_categorization)

    results["created"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    results = results[columns]

    # Store the results in the database
    # results.apply(lambda x: storage.insert_row(x), axis=1)
    storage.insert_data(results)

    print(f"Inserted {results.shape[0]} records.")

    # Print the categorized text
    for index, row in results.iterrows():
        print(f"Rank: {row['rank']}")
        print(f"Title: {row['title']}")
        print(f"Category: {row['category']}")
        print(f"Snippet: {row['snippet']}")
        print(f"Link: {row['link']}")
        print("----------------------------------")

    return results
