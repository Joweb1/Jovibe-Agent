import requests
from bs4 import BeautifulSoup
from src.skills.registry import SkillRegistry

@SkillRegistry.register("web_search")
def web_search(query: str, num_results: int = 5):
    """
    Searches the web for a query and returns the top results (titles and URLs).
    
    Args:
        query: The search term.
        num_results: Number of results to return (default 5).
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    # DuckDuckGo HTML version is easier to scrape without JS
    url = f"https://html.duckduckgo.com/html/?q={query}"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        
        for i, result in enumerate(soup.find_all("div", class_="result__body")):
            if i >= num_results:
                break
            
            title_tag = result.find("a", class_="result__a")
            snippet_tag = result.find("a", class_="result__snippet")
            
            if title_tag:
                title = title_tag.get_text()
                link = title_tag.get("href")
                # Handle potential relative links (though DDG usually provides full redirects)
                if link.startswith("//"):
                    link = "https:" + link
                
                snippet = snippet_tag.get_text().strip() if snippet_tag else "No snippet available."
                results.append(f"{i+1}. {title}\n   URL: {link}\n   Snippet: {snippet}")
        
        if not results:
            return "No results found for the query."
            
        return "\n\n".join(results)
        
    except Exception as e:
        return f"Error during web search: {str(e)}"
