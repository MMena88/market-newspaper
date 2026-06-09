import os
import json
from jinja2 import Environment, FileSystemLoader

DISCLAIMER = "Este reporte es únicamente de carácter informativo y educativo. No constituye asesoría financiera, recomendación de inversión ni oferta de compra/venta de activos. Operar en mercados financieros conlleva altos riesgos."

def build_ticker_items(data):
    """Formats ticker data for the header ribbon."""
    items = []
    
    # Add Indices
    for name, sym in [("S&P 500", "S&P 500"), ("Nasdaq 100", "Nasdaq 100"), ("Dow Jones", "Dow Jones")]:
        asset = data["indices"].get(sym, {})
        if asset.get("current_price") is not None:
            items.append({
                "name": name,
                "price": f"{asset['current_price']:,.2f}",
                "change_pct": asset["change_pct"]
            })
            
    # Add Crypto
    for name, sym in [("BTC", "Bitcoin"), ("ETH", "Ethereum")]:
        asset = data["crypto"].get(sym, {})
        if asset.get("current_price") is not None:
            items.append({
                "name": name,
                "price": f"${asset['current_price']:,.2f}",
                "change_pct": asset["change_pct"]
            })
            
    # Add Key Stocks
    for name, sym in [("NVDA", "NVIDIA"), ("TSLA", "Tesla")]:
        asset = data["stocks"].get(sym, {})
        if asset.get("current_price") is not None:
            items.append({
                "name": name,
                "price": f"${asset['current_price']:,.2f}",
                "change_pct": asset["change_pct"]
            })
            
    # Add Gold and Yield
    gold = data["commodities"].get("Gold", {})
    if gold.get("current_price") is not None:
        items.append({
            "name": "GOLD",
            "price": f"${gold['current_price']:,.2f}",
            "change_pct": gold["change_pct"]
        })
        
    yield_10y = data["bonds"].get("10-Year Yield", {})
    if yield_10y.get("current_price") is not None:
        items.append({
            "name": "US10Y",
            "price": f"{yield_10y['current_price']:.2f}%",
            "change_pct": yield_10y["change_pct"]
        })
        
    return items

def compile_markdown_report(date, data, analysis):
    """Compiles the report in Markdown format following the required sections."""
    sp500 = data["indices"].get("S&P 500", {})
    nasdaq = data["indices"].get("Nasdaq 100", {})
    dow = data["indices"].get("Dow Jones", {})
    btc = data["crypto"].get("Bitcoin", {})
    eth = data["crypto"].get("Ethereum", {})
    gold = data["commodities"].get("Gold", {})
    oil = data["commodities"].get("Crude Oil", {})
    usd = data["forex"].get("US Dollar Index", {})
    yield_10y = data["bonds"].get("10-Year Yield", {})
    
    def fmt_asset(a, prefix="", suffix=""):
        if not a or a.get("current_price") is None:
            return "N/A"
        price = a['current_price']
        change = a['change_pct']
        sign = "+" if change >= 0 else ""
        return f"{prefix}{price:,.2f}{suffix} ({sign}{change:.2f}%)"

    general_news_lines = []
    for item in data["news"].get("general", [])[:5]:
        general_news_lines.append(f"- [{item['title']}]({item['link']})")
    news_section = "\n".join(general_news_lines) if general_news_lines else "- No hay noticias relevantes disponibles."

    indices_levels = []
    for item in analysis["levels_to_watch"].get("Indices", []):
        indices_levels.append(f"- **{item['name']}**: Precio: {item['price']} | Soporte: {item['support']} | Resistencia: {item['resistance']}")
    indices_levels_str = "\n".join(indices_levels) if indices_levels else "- Datos no disponibles."

    crypto_levels = []
    for item in analysis["levels_to_watch"].get("Crypto", []):
        crypto_levels.append(f"- **{item['name']}**: Precio: {item['price']} | Soporte: {item['support']} | Resistencia: {item['resistance']}")
    crypto_levels_str = "\n".join(crypto_levels) if crypto_levels else "- Datos no disponibles."

    stocks_levels = []
    for item in analysis["levels_to_watch"].get("Stocks", []):
        stocks_levels.append(f"- **{item['name']}**: Precio: {item['price']} | Soporte: {item['support']} | Resistencia: {item['resistance']}")
    stocks_levels_str = "\n".join(stocks_levels) if stocks_levels else "- Datos no disponibles."

    md = f"""# Daily Market Newspaper

## Date
{date} (America/New_York)

## Market Snapshot
El tono general del mercado se evalúa como **{analysis.get('tone_es', analysis['tone'])}**.
{analysis['market_outlook']}

## Equity Market
- **S&P 500 (`{sp500.get('symbol', '^GSPC')}`):** {fmt_asset(sp500)}
- **Nasdaq Composite (`{nasdaq.get('symbol', '^IXIC')}`):** {fmt_asset(nasdaq)}
- **Dow Jones (`{dow.get('symbol', '^DJI')}`):** {fmt_asset(dow)}

## Crypto Market
- **Bitcoin (`{btc.get('symbol', 'BTC-USD')}`):** {fmt_asset(btc, prefix="$")}
- **Ethereum (`{eth.get('symbol', 'ETH-USD')}`):** {fmt_asset(eth, prefix="$")}

{analysis['btc_outlook']}

## Commodities
- **Gold (`{gold.get('symbol', 'GC=F')}`):** {fmt_asset(gold, prefix="$")}
- **Crude Oil (`{oil.get('symbol', 'CL=F')}`):** {fmt_asset(oil, prefix="$")}

## Forex / Dollar
- **U.S. Dollar Index (`{usd.get('symbol', 'DX-Y.NYB')}`):** {fmt_asset(usd)}

## Bonds / Yields
- **U.S. 10-Year Treasury Yield (`{yield_10y.get('symbol', '^TNX')}`):** {fmt_asset(yield_10y, suffix="%")}

## Key News or Macro Events
{news_section}

## Short Market Analysis
{analysis['stock_insights']}

## Important Levels to Watch
### Indices
{indices_levels_str}

### Crypto
{crypto_levels_str}

### Stocks
{stocks_levels_str}

## Disclaimer
{DISCLAIMER}
"""
    return md

def update_archive_json(date, tone, summary, target_dir):
    """Updates public/reports/archive.json with the new report details."""
    archive_file = os.path.join(target_dir, "archive.json")
    
    archive = []
    if os.path.exists(archive_file):
        try:
            with open(archive_file, 'r', encoding='utf-8') as f:
                archive = json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load archive.json ({e}). Creating new.")
            
    # Remove existing entry for same date if it exists
    archive = [item for item in archive if item["date"] != date]
    
    # Append new item
    archive.append({
        "date": date,
        "tone": tone,
        "summary": summary[:120] + "..." if len(summary) > 120 else summary,
        "latest": False
    })
    
    # Sort descending by date
    archive.sort(key=lambda x: x["date"], reverse=True)
    
    # Mark first item as latest
    if archive:
        for i, item in enumerate(archive):
            item["latest"] = (i == 0)
            
    with open(archive_file, 'w', encoding='utf-8') as f:
        json.dump(archive, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully updated {archive_file}")

def render_report(date, data, analysis, root_dir):
    """
    Orchestrates the rendering process:
    - Generates markdown report.
    - Compiles HTML files (both home index.html and archive YYYY-MM-DD.html).
    - Updates archive.json index.
    """
    print(f"Compiling report outputs for {date}...")
    
    # Create necessary directories
    reports_dir = os.path.join(root_dir, "reports")
    public_dir = os.path.join(root_dir, "public")
    public_reports_dir = os.path.join(public_dir, "reports")
    templates_dir = os.path.join(public_dir, "templates")
    
    os.makedirs(reports_dir, exist_ok=True)
    os.makedirs(public_reports_dir, exist_ok=True)
    
    # 1. Compile and save Markdown report
    md_content = compile_markdown_report(date, data, analysis)
    md_filepath = os.path.join(reports_dir, f"{date}.md")
    with open(md_filepath, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"Saved Markdown report: {md_filepath}")
    
    # Prepare data for Jinja template
    ticker_items = build_ticker_items(data)
    
    # Combine stock news
    stocks_news = []
    for ticker_name in ["NVDA", "AAPL", "MSFT", "TSLA"]:
        stocks_news.extend(data["news"].get(ticker_name, []))
    # Deduplicate and sort/slice
    seen_links = set()
    unique_stocks_news = []
    for item in stocks_news:
        if item['link'] not in seen_links:
            seen_links.add(item['link'])
            unique_stocks_news.append(item)
    unique_stocks_news = unique_stocks_news[:5]
    
    # Create Jinja Environment
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template("index_template.html")
    
    # 2. Render index.html (Homepage) with relative paths for assets = "./"
    html_home_content = template.render(
        date=date,
        rel_path="./",
        ticker_items=ticker_items,
        tone=analysis["tone"],
        tone_es=analysis.get("tone_es", analysis["tone"]),
        bull_case=analysis["bull_case"],
        bear_case=analysis["bear_case"],
        market_outlook=analysis["market_outlook"],
        btc_outlook=analysis["btc_outlook"],
        stock_insights=analysis["stock_insights"],
        assets=data,
        levels=analysis["levels_to_watch"],
        news_general=data["news"].get("general", [])[:5],
        news_stocks=unique_stocks_news,
        disclaimer=DISCLAIMER
    )
    
    home_filepath = os.path.join(public_dir, "index.html")
    with open(home_filepath, 'w', encoding='utf-8') as f:
        f.write(html_home_content)
    print(f"Saved homepage index.html: {home_filepath}")
    
    # 3. Render public/reports/YYYY-MM-DD.html with relative paths for assets = "../"
    html_archive_content = template.render(
        date=date,
        rel_path="../",
        ticker_items=ticker_items,
        tone=analysis["tone"],
        tone_es=analysis.get("tone_es", analysis["tone"]),
        bull_case=analysis["bull_case"],
        bear_case=analysis["bear_case"],
        market_outlook=analysis["market_outlook"],
        btc_outlook=analysis["btc_outlook"],
        stock_insights=analysis["stock_insights"],
        assets=data,
        levels=analysis["levels_to_watch"],
        news_general=data["news"].get("general", [])[:5],
        news_stocks=unique_stocks_news,
        disclaimer=DISCLAIMER
    )
    
    archive_filepath = os.path.join(public_reports_dir, f"{date}.html")
    with open(archive_filepath, 'w', encoding='utf-8') as f:
        f.write(html_archive_content)
    print(f"Saved historical HTML report: {archive_filepath}")
    
    # 4. Update public/reports/archive.json
    update_archive_json(date, analysis["tone"], analysis["market_outlook"], public_reports_dir)

if __name__ == "__main__":
    # Small test execution with mock values if run directly
    print("This module compiles the reports. Execute generate_report.py to run the full workflow.")
