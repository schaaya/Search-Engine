from flask import Flask, request, jsonify, render_template_string
from search import search, openai_text_categorization
# from filter import Filter
from storage import DBStorage
import html

app = Flask(__name__)

styles = """
<style>
    .site {
        font-size: .8rem;
        color: green;
    }

    .snippet {
        font-size: .9rem;
        color: gray;
        margin-bottom: 30px;
    }

    .rel-button {
        cursor: pointer;
        color: blue;
    }
</style>
<script>
const relevant = function(query, link){
    fetch("/relevant", {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
           "query": query,
           "link": link
          })
        });
}
</script>
"""

search_template = styles + """
     <form action="/" method="post">
      <input type="text" name="query">
      <input type="submit" value="Search">
    </form>
    """

result_template = """
<p class="site">{rank}: {link} <span class="rel-button" onclick='relevant("{query}", "{link}");'>Relevant</span></p>
<a href="{link}">{title}</a>
<p class="snippet">{snippet}</p>
"""


def show_search_form():
    return search_template


def run_search(query):
    results = search(query)
    # fi = Filter(results)
    # filtered = fi.filter()
    rendered = search_template
    results["snippet"] = results["snippet"].apply(lambda x: html.escape(x))
    # results["html"] = results["html"].apply(lambda x: html.escape(x))  # Escape the text for HTML display
    # for index, row in results.iterrows():
    #     rendered += render_template_string(result_template, **row)
    for index, row in results.iterrows():
        rendered += result_template.format(**row)

    output_filename = "categorized_text.txt"
    with open(output_filename, "w", encoding="utf-8") as file:
        for index, row in results.iterrows():
            category = openai_text_categorization(row["snippet"])
            file.write(f"Result {index + 1}:\n")
            file.write(f"Title: {row['title']}\n")
            file.write(f"Category: {category}\n\n")

    print(f"Inserted {results.shape[0]} records.")
    print(f"Categorized text saved to {output_filename}")
    return rendered


@app.route("/", methods=['GET', 'POST'])
def search_form():
    if request.method == 'POST':
        query = request.form["query"]
        return run_search(query)
    else:
        return show_search_form()


# @app.route("/relevant", methods=["POST"])
# def mark_relevant():
#     data = request.get_json()
#     query = data["query"]
#     link = data["link"]
#     storage = DBStorage()
#     storage.update_relevance(query, link, 10)
#     return jsonify(success=True)
