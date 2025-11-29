"""
Food News Fetcher Agent using LangChain and LangGraph
Fetches latest food-related news from multiple sources
"""
from typing import Dict, Any, List, TypedDict, Annotated
import operator
import os
from datetime import datetime, timedelta
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.prompts import ChatPromptTemplate
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from langgraph.graph import StateGraph, END
import json
import re

# Configure Gemini
api_key = os.environ.get("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    gemini_model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        generation_config={"temperature": 0.7},
        safety_settings={
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
    )
else:
    print("⚠️ Warning: GOOGLE_API_KEY not found for news agent")
    gemini_model = None

# Initialize DuckDuckGo search tool
search_tool = DuckDuckGoSearchResults(
    num_results=10,
    backend="news"  # Use news backend for latest articles
)

# Define state for news agent
class NewsAgentState(TypedDict):
    messages: Annotated[List[Any], operator.add]
    search_queries: List[str]
    raw_results: List[Dict[str, Any]]
    processed_articles: List[Dict[str, Any]]
    final_news: List[Dict[str, Any]]

# System prompt for news agent
NEWS_SYSTEM_PROMPT = """You are a food news curator AI that specializes in finding and summarizing the latest food industry news.

Your responsibilities:
1. Search for latest food news from reliable sources
2. Filter out irrelevant or low-quality articles
3. Extract key information: title, summary, source, date, relevance
4. Categorize news by type: health, safety, regulations, trends, recalls
5. Provide concise, informative summaries

Focus areas:
- Food safety and recalls
- Nutritional research and health impacts
- Food industry regulations (FSSAI, FDA)
- Emerging food trends
- Ingredient innovations
- Restaurant and food tech news

Quality criteria:
- Recent (within last 7 days preferred)
- From credible sources
- Relevant to consumer health and food choices
- Actionable or informative for users
"""

def generate_search_queries(state: NewsAgentState):
    """Generate diverse search queries for food news"""
    
    # Define multiple search angles
    queries = [
        "food safety recalls latest news",
        "FSSAI food regulations updates India",
        "healthy eating nutrition research 2024",
        "food industry trends innovations",
        "food labeling regulations changes",
        "harmful ingredients banned food",
        "organic food certification news",
        "processed food health studies",
        "restaurant food safety violations",
        "nutritional guidelines updates"
    ]
    
    # Add to state
    state["search_queries"] = queries
    state["messages"].append(AIMessage(content=f"Generated {len(queries)} search queries for food news"))
    
    return state

def search_news(state: NewsAgentState):
    """Search for news using DuckDuckGo"""
    
    queries = state["search_queries"]
    all_results = []
    
    # Search with each query (limit to first 3 to avoid rate limits)
    for query in queries[:3]:
        try:
            results = search_tool.invoke(query)
            
            # Parse results (DDG returns string format)
            if isinstance(results, str):
                # Extract links and snippets from string result
                # Format: [snippet: text, title: title, link: url]
                parsed = []
                entries = results.split('[snippet:')
                for entry in entries[1:]:  # Skip first empty
                    try:
                        snippet_part = entry.split(', title:')[0].strip()
                        title_part = entry.split(', title:')[1].split(', link:')[0].strip()
                        link_part = entry.split(', link:')[1].split(']')[0].strip()
                        
                        parsed.append({
                            'snippet': snippet_part,
                            'title': title_part,
                            'link': link_part,
                            'query': query
                        })
                    except:
                        continue
                
                all_results.extend(parsed)
            
        except Exception as e:
            print(f"Search error for query '{query}': {str(e)}")
            continue
    
    state["raw_results"] = all_results
    state["messages"].append(AIMessage(content=f"Found {len(all_results)} news articles"))
    
    return state

def process_and_filter_articles(state: NewsAgentState):
    """Process articles and filter for quality and relevance"""
    
    raw_results = state["raw_results"]
    
    if not raw_results:
        state["processed_articles"] = []
        return state
    
    # Use Gemini to analyze and filter articles
    if not gemini_model:
        # Fallback: basic filtering
        state["processed_articles"] = raw_results[:10]
        return state
    
    # Prepare articles for analysis
    articles_text = "\n\n".join([
        f"Title: {r['title']}\nSnippet: {r['snippet']}\nLink: {r['link']}"
        for r in raw_results[:15]  # Limit to avoid token limits
    ])
    
    prompt = f"""Analyze these food news articles and extract the most relevant, high-quality ones.

Articles:
{articles_text}

For each relevant article, provide:
1. Title (cleaned up)
2. Summary (2-3 sentences about key points)
3. Category (safety/health/regulations/trends/recalls)
4. Relevance score (1-10)
5. Source credibility (low/medium/high)

Return ONLY a JSON array with this structure:
[
  {{
    "title": "Article title",
    "summary": "Brief summary",
    "category": "safety",
    "relevance": 8,
    "credibility": "high",
    "link": "original_url"
  }}
]

Filter out:
- Duplicate or very similar articles
- Low credibility sources
- Irrelevant content (not about food)
- Promotional/advertisement content

Select top 10 most relevant articles.
"""
    
    try:
        response = gemini_model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Extract JSON from response
        json_match = re.search(r'\[\s*\{.*\}\s*\]', response_text, re.DOTALL)
        if json_match:
            articles_json = json.loads(json_match.group())
            state["processed_articles"] = articles_json
        else:
            # Fallback to raw results
            state["processed_articles"] = raw_results[:10]
            
    except Exception as e:
        print(f"Article processing error: {str(e)}")
        # Fallback
        state["processed_articles"] = raw_results[:10]
    
    state["messages"].append(AIMessage(content=f"Processed and filtered {len(state['processed_articles'])} articles"))
    
    return state

def generate_final_news_feed(state: NewsAgentState):
    """Generate final curated news feed with enhanced metadata"""
    
    processed = state["processed_articles"]
    
    # Add metadata and structure for app
    final_news = []
    
    for i, article in enumerate(processed):
        # Ensure all required fields
        news_item = {
            "id": f"news_{datetime.now().strftime('%Y%m%d')}_{i}",
            "title": article.get("title", "Untitled"),
            "summary": article.get("summary", article.get("snippet", "No summary available")),
            "category": article.get("category", "general"),
            "source": extract_source_from_url(article.get("link", "")),
            "url": article.get("link", ""),
            "published_date": datetime.now().isoformat(),  # Current date as approximation
            "relevance_score": article.get("relevance", 5),
            "credibility": article.get("credibility", "medium"),
            "image_url": None,  # Could be enhanced with image search
            "tags": generate_tags(article.get("category", "general"))
        }
        
        final_news.append(news_item)
    
    state["final_news"] = final_news
    state["messages"].append(AIMessage(content=f"Generated final news feed with {len(final_news)} articles"))
    
    return state

def extract_source_from_url(url: str) -> str:
    """Extract source name from URL"""
    try:
        # Remove protocol and www
        domain = url.split("//")[-1].split("/")[0]
        domain = domain.replace("www.", "")
        # Get main domain
        parts = domain.split(".")
        if len(parts) > 1:
            return parts[-2].title()
        return domain.title()
    except:
        return "Unknown Source"

def generate_tags(category: str) -> List[str]:
    """Generate relevant tags based on category"""
    tag_map = {
        "safety": ["Food Safety", "Health Alert", "Consumer Info"],
        "health": ["Nutrition", "Healthy Eating", "Wellness"],
        "regulations": ["FSSAI", "Food Law", "Compliance"],
        "trends": ["Food Trends", "Innovation", "Industry"],
        "recalls": ["Product Recall", "Safety Alert", "Warning"]
    }
    return tag_map.get(category, ["Food News", "General"])

# Build the LangGraph workflow
workflow = StateGraph(NewsAgentState)

# Add nodes
workflow.add_node("generate_queries", generate_search_queries)
workflow.add_node("search_news", search_news)
workflow.add_node("process_articles", process_and_filter_articles)
workflow.add_node("generate_feed", generate_final_news_feed)

# Define edges
workflow.set_entry_point("generate_queries")
workflow.add_edge("generate_queries", "search_news")
workflow.add_edge("search_news", "process_articles")
workflow.add_edge("process_articles", "generate_feed")
workflow.add_edge("generate_feed", END)

# Compile the graph
news_agent = workflow.compile()

def fetch_latest_food_news() -> List[Dict[str, Any]]:
    """
    Main function to fetch latest food news
    Returns list of news articles with metadata
    """
    
    # Initialize state
    initial_state = {
        "messages": [SystemMessage(content=NEWS_SYSTEM_PROMPT)],
        "search_queries": [],
        "raw_results": [],
        "processed_articles": [],
        "final_news": []
    }
    
    try:
        # Run the agent
        result = news_agent.invoke(initial_state)
        
        # Return the final news feed
        return result["final_news"]
        
    except Exception as e:
        print(f"❌ News fetch error: {str(e)}")
        return []

# Test function
if __name__ == "__main__":
    print("🔍 Fetching latest food news...")
    news = fetch_latest_food_news()
    print(f"\n✅ Found {len(news)} articles\n")
    
    for article in news[:3]:
        print(f"📰 {article['title']}")
        print(f"   Category: {article['category']}")
        print(f"   Source: {article['source']}")
        print(f"   {article['summary']}\n")
