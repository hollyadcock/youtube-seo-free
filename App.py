import streamlit as st
import re
from collections import Counter
import requests
from bs4 import BeautifulSoup

# =========================
# COMPETITOR SCRAPING
# =========================

HEADERS = {"User-Agent": "Mozilla/5.0"}

def scrape_competitor_keywords(urls):
    text = ""
    for url in urls:
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            if soup.title:
                text += soup.title.text + " "
            for meta in soup.find_all("meta"):
                if meta.get("name") == "description":
                    text += meta.get("content", "") + " "
        except:
            continue
    words = re.findall(r"\b[a-z]{4,}\b", text.lower())
    stopwords = {
        "youtube","video","watch","this","that","with","from",
        "your","about","what","when","where","which","their"
    }
    keywords = [w for w, _ in Counter(words).most_common(15) if w not in stopwords]
    return keywords

# =========================
# FREE SEO GENERATOR
# =========================

def generate_seo_free(transcript, competitor_keywords=None):
    # clean transcript
    words = re.findall(r"\b[a-z]{4,}\b", transcript.lower())
    stopwords = {
        "this","that","with","from","your","about","what","when","where","which","their"
    }
    keywords = [w for w in words if w not in stopwords]
    
    if competitor_keywords:
        keywords += competitor_keywords
    
    # most common 20 keywords
    keyword_counts = Counter(keywords).most_common(20)
    keywords_list = [k for k, _ in keyword_counts]
    
    # Title: pick top 3 words
    title = " ".join([k.capitalize() for k in keywords_list[:3]])
    
    # Description: first 2 lines from transcript
    lines = transcript.split(".")
    description = ". ".join(lines[:2]) + "."
    
    # Hashtags: top 5 keywords
    hashtags = ["#" + k for k in keywords_list[:5]]
    
    output = f"""
**Title:** {title}

**Description:** {description}

**Keywords:** {', '.join(keywords_list)}

**Hashtags:** {', '.join(hashtags)}
"""
    return output

# =========================
# STREAMLIT UI
# =========================

st.set_page_config(page_title="YouTube SEO Free", layout="wide")
st.title("🎥 YouTube SEO Generator (Fully Free)")

if "competitor_keywords" not in st.session_state:
    st.session_state.competitor_keywords = []

st.subheader("1️⃣ Paste Your Video Transcript")
transcript = st.text_area("Video Transcript", height=250)

st.subheader("2️⃣ Competitor YouTube URLs (Optional)")
urls = st.text_area("Paste competitor URLs (one per line)", height=150)

if st.button("Scrape Competitor Keywords"):
    if urls.strip():
        url_list = urls.strip().split("\n")
        st.session_state.competitor_keywords = scrape_competitor_keywords(url_list)
        st.success("Keywords extracted!")
        st.write(st.session_state.competitor_keywords)
    else:
        st.warning("Please add at least one URL.")

st.subheader("3️⃣ Generate SEO")
if st.button("Generate SEO"):
    if transcript.strip():
        output = generate_seo_free(
            transcript,
            st.session_state.competitor_keywords
        )
        st.markdown(output)
    else:
        st.warning("Transcript required.")
