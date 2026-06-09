import yfinance as yf
import requests
import xml.etree.ElementTree as ET
import html
import re

# List of assets to track
ASSETS = {
    "indices": {
        "S&P 500": "^GSPC",
        "Nasdaq 100": "^IXIC",
        "Dow Jones": "^DJI"
    },
    "stocks": {
        "NVIDIA": "NVDA",
        "Apple": "AAPL",
        "Microsoft": "MSFT",
        "Tesla": "TSLA"
    },
    "crypto": {
        "Bitcoin": "BTC-USD",
        "Ethereum": "ETH-USD"
    },
    "commodities": {
        "Gold": "GC=F",
        "Crude Oil": "CL=F"
    },
    "forex": {
        "US Dollar Index": "DX-Y.NYB"
    },
    "bonds": {
        "10-Year Yield": "^TNX"
    }
}

def clean_html(text):
    """Helper to remove HTML tags and unescape HTML entities from feed descriptions."""
    if not text:
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    # Unescape HTML characters like &amp; &quot;
    return html.unescape(text).strip()

def fetch_rss_news(symbol=None):
    """
    Fetches the top news headlines for a specific symbol or general market news.
    Uses Yahoo Finance RSS feeds.
    """
    if symbol:
        # Ticker-specific feed
        url = f"https://feeds.finance.yahoo.com/rss.2.0/headline?s={symbol}"
    else:
        # General market news
        url = "https://finance.yahoo.com/rss/topstories"
        
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    news_items = []
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            for item in root.findall('.//item'):
                title = item.find('title')
                link = item.find('link')
                pub_date = item.find('pubDate')
                description = item.find('description')
                
                title_text = clean_html(title.text) if title is not None else "No Title"
                desc_text = clean_html(description.text) if description is not None else ""
                
                # Exclude ads or boilerplate if present
                if "Yahoo" in title_text and len(title_text) < 20:
                    continue
                    
                news_items.append({
                    "title": title_text,
                    "link": link.text if link is not None else "#",
                    "pubDate": pub_date.text if pub_date is not None else "",
                    "description": desc_text[:200] + "..." if len(desc_text) > 200 else desc_text
                })
                if len(news_items) >= 5: # Return top 5 news items
                    break
    except Exception as e:
        print(f"Warning: Failed to fetch RSS news for {symbol or 'General'}: {e}")
        
    return news_items

def fetch_asset_data(name, symbol):
    """Fetches historical and current price data for a symbol via yfinance."""
    try:
        ticker = yf.Ticker(symbol)
        # Fetch 5 days history to ensure we have at least 2 valid trading sessions
        hist = ticker.history(period="5d")
        
        if hist.empty or len(hist) < 2:
            print(f"Warning: Insufficient data for {name} ({symbol})")
            return None
            
        current_price = hist['Close'].iloc[-1]
        prev_price = hist['Close'].iloc[-2]
        pct_change = ((current_price - prev_price) / prev_price) * 100
        
        high = hist['High'].iloc[-1]
        low = hist['Low'].iloc[-1]
        open_price = hist['Open'].iloc[-1]
        
        return {
            "name": name,
            "symbol": symbol,
            "current_price": float(current_price),
            "prev_price": float(prev_price),
            "change_pct": float(pct_change),
            "high": float(high),
            "low": float(low),
            "open": float(open_price)
        }
    except Exception as e:
        print(f"Error fetching market data for {name} ({symbol}): {e}")
        return None

def fetch_all_market_data():
    """
    Fetches data for all configured indices, stocks, cryptos, commodities, forex and bonds.
    Also gathers relevant news articles.
    """
    print("Fetching financial market data from Yahoo Finance...")
    data = {}
    
    # Fetch asset metrics
    for category, symbols in ASSETS.items():
        data[category] = {}
        for name, symbol in symbols.items():
            result = fetch_asset_data(name, symbol)
            if result:
                data[category][name] = result
            else:
                data[category][name] = {
                    "name": name,
                    "symbol": symbol,
                    "current_price": None,
                    "prev_price": None,
                    "change_pct": 0.0,
                    "high": None,
                    "low": None,
                    "open": None,
                    "error": True
                }
                
    # Fetch News
    print("Fetching market news RSS feeds...")
    data["news"] = {
        "general": fetch_rss_news(),
        "NVDA": fetch_rss_news("NVDA"),
        "AAPL": fetch_rss_news("AAPL"),
        "MSFT": fetch_rss_news("MSFT"),
        "TSLA": fetch_rss_news("TSLA"),
        "BTC": fetch_rss_news("BTC-USD")
    }
    
    return data

if __name__ == "__main__":
    # Test script execution
    import json
    market_data = fetch_all_market_data()
    print(json.dumps(market_data, indent=2))
