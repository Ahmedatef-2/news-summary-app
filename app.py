from flask import Flask, render_template, request
import feedparser
import trafilatura
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer

app = Flask(__name__)

# قاموس مصادر RSS
RSS_FEEDS = {
    "اليوم السابع - أخبار عامة": "http://www.youm7.com/rss/SectionRss?SectionID=65",
    "اليوم السابع - عاجل": "http://www.youm7.com/rss/SectionRss?SectionID=319",
    "اليوم السابع - حوادث": "http://www.youm7.com/rss/SectionRss?SectionID=203",
    "BBC Arabic": "https://feeds.bbci.co.uk/arabic/rss.xml",
    "Reuters": "http://feeds.reuters.com/reuters/topNews",
    "TechCrunch": "http://feeds.feedburner.com/TechCrunch/",
    "CNN": "https://rss.cnn.com/rss/edition.rss",
    "Medium Python": "https://medium.com/feed/tag/python"
}

def fetch_entries(feed_url):
    entries = []
    d = feedparser.parse(feed_url)
    for e in d.entries[:]:
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
    section_name = request.args.get("section")
    if not section_name or section_name not in RSS_FEEDS:
        # عرض الأقسام فقط
        return render_template("index.html", feeds=RSS_FEEDS, news=None, section_name=None)

    feed_url = RSS_FEEDS[section_name]
    news_list = []
    entries = fetch_entries(feed_url)
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

    return render_template("index.html", feeds=RSS_FEEDS, news=news_list, section_name=section_name)

if __name__ == "__main__":
    app.run(debug=True)
# Run the app on http://127.0.0.1:5000/