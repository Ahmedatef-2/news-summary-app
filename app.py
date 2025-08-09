from flask import Flask, render_template
import feedparser
import trafilatura
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer

app = Flask(__name__)

# مصادر RSS
RSS_FEEDS = [
    "https://feeds.bbci.co.uk/arabic/rss.xml",
    "http://feeds.reuters.com/reuters/topNews",
    "http://feeds.feedburner.com/TechCrunch/",
    "https://rss.cnn.com/rss/edition.rss"
]

def fetch_entries():
    entries = []
    for feed in RSS_FEEDS:
        d = feedparser.parse(feed)
        for e in d.entries[:3]:
            entries.append({
                "title": e.get("title", ""),
                "link": e.get("link", ""),
                "published": e.get("published", "")
            })
    return entries

def extract_text(url):
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        text = trafilatura.extract(downloaded)
        return text
    return None

def summarize(text, count=4):
    parser = PlaintextParser.from_string(text, Tokenizer("arabic"))
    summarizer = TextRankSummarizer()
    return [str(s) for s in summarizer(parser.document, count)]

@app.route("/")
def home():
    news_list = []
    entries = fetch_entries()
    for entry in entries:
        text = extract_text(entry['link'])
        if text:
            bullets = summarize(text)
            news_list.append({
                "title": entry['title'],
                "link": entry['link'],
                "published": entry['published'],
                "bullets": bullets
            })
    return render_template("index.html", news=news_list)

if __name__ == "__main__":
    app.run(debug=True)
