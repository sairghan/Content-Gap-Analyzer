import streamlit as st
from tavily import TavilyClient
from langchain_google_genai import ChatGoogleGenerativeAI
import os

# --- Configuration ---
st.set_page_config(page_title="SEO Content Gap Analyzer", page_icon="🔍", layout="wide")
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
tavily = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# --- Logic Functions ---
def get_market_leaders(keyword):
    # Research the top-ranking content for this keyword
    results = tavily.search(query=f"best articles about {keyword}", search_depth="advanced", max_results=3)
    return results

def get_competitor_content(domain, keyword):
    # Search specifically within the competitor's domain for this keyword
    query = f"site:{domain} {keyword}"
    results = tavily.search(query=query, search_depth="advanced", max_results=2)
    return results

def analyze_gap(keyword, market_data, competitor_data):
    prompt = f"""
    You are an expert SEO Content Strategist.
    
    KEYWORD: {keyword}
    
    MARKET LEADER CONTENT (The competition): {market_data}
    COMPETITOR SITE CONTENT: {competitor_data}
    
    TASK: Analyze the gap. Compare what the Market Leaders are covering vs what the 
    Competitor is currently writing about. 
    
    Identify 3 'Content Gaps' where the competitor is failing to address user intent 
    or specific sub-topics that the market leaders are capitalizing on.
    
    Output a Markdown Table:
    | Gap Topic | Why it's a gap | Content Angle to Win |
    """
    return llm.invoke(prompt).content

# --- UI ---
st.title("🔍 SEO Content Gap Analyzer")
col1, col2 = st.columns(2)

with col1:
    keyword = st.text_input("Target Keyword", placeholder="e.g., SDR automation")
with col2:
    competitor_domain = st.text_input("Competitor Domain", placeholder="e.g., outreach.io")

if st.button("Analyze Content Gap"):
    if not keyword or not competitor_domain:
        st.warning("Please enter both a keyword and a competitor domain.")
    else:
        with st.spinner("Researching market and competitor..."):
            try:
                # 1. Research
                market = get_market_leaders(keyword)
                competitor = get_competitor_content(competitor_domain, keyword)
                
                # 2. Analyze
                report = analyze_gap(keyword, market, competitor)
                
                # 3. Display
                st.subheader("Gap Analysis Report")
                st.markdown(report)
            except Exception as e:
                st.error(f"Analysis failed: {e}")
