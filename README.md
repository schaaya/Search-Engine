# Search Application README

This is a simple search application developed in Python using Flask framework. It allows users to search for information based on a query and perform text categorization on the search results from the internet.

## Getting Started

### Prerequisites

- Python 3.x
- Flask
- OpenAI GPT-3.5 Turbo API key
- Google Custom Search JSON API key

### Running the Application

1. Install the required Python packages:

```
pip install flask openai
```
2. Set up the API keys:

    - Obtain an OpenAI GPT-3.5 Turbo API key from OpenAI and set it as an environment variable named OPENAI_API_KEY in settings.py file.
    
    - Obtain a Google Custom Search JSON API key and Custom Search Engine ID from the Google Developers Console and set it as an environment variable named SEARCH_KEY and SEARCH_ID in settings.py file.
    
    - Run the application on PyCharm IDE.

3. In Python Console, run the Flask app using the following command:
```
flask --debug run --port 5001
```
4. Open the URL http://127.0.0.1:5001 in a web browser to access the search results.

5. To search for the query "https://netflixtechblog.com/serverless", enter the query in the search box on the web page.

6. The search results will be displayed on the web page, and the categorized text will be stored in the file "categorized_text.txt" in the current working directory.

