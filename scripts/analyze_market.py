import os
import json
import google.generativeai as genai

def run_rule_based_analysis(data):
    """
    Fallback deterministic analysis when GEMINI_API_KEY is not available.
    Uses stock/crypto returns, news headlines, and technical markers.
    """
    analysis = {}
    
    # Extract asset data safely
    sp500 = data["indices"].get("S&P 500", {})
    nasdaq = data["indices"].get("Nasdaq 100", {})
    dow = data["indices"].get("Dow Jones", {})
    
    nvda = data["stocks"].get("NVIDIA", {})
    aapl = data["stocks"].get("Apple", {})
    msft = data["stocks"].get("Microsoft", {})
    tsla = data["stocks"].get("Tesla", {})
    
    btc = data["crypto"].get("Bitcoin", {})
    eth = data["crypto"].get("Ethereum", {})
    
    gold = data["commodities"].get("Gold", {})
    oil = data["commodities"].get("Crude Oil", {})
    usd = data["forex"].get("US Dollar Index", {})
    yield_10y = data["bonds"].get("10-Year Yield", {})
    
    # 1. Determine Market Tone
    sp500_change = sp500.get("change_pct", 0.0) or 0.0
    nasdaq_change = nasdaq.get("change_pct", 0.0) or 0.0
    btc_change = btc.get("change_pct", 0.0) or 0.0
    gold_change = gold.get("change_pct", 0.0) or 0.0
    
    if sp500_change > 0.3 and nasdaq_change > 0.4:
        tone = "Risk-on"
    elif sp500_change < -0.3 and nasdaq_change < -0.4:
        tone = "Risk-off"
    elif abs(sp500_change) <= 0.3 and abs(nasdaq_change) <= 0.3:
        tone = "Neutral"
    else:
        tone = "Mixed"
    analysis["tone"] = tone

    # 2. Bull and Bear Cases
    bull_case = []
    bear_case = []
    
    # Indices
    if sp500_change > 0:
        bull_case.append(f"Major U.S. indices are exhibiting upward momentum, led by { 'Nasdaq' if nasdaq_change > sp500_change else 'S&P 500' } gains of {max(sp500_change, nasdaq_change):.2f}%.")
    else:
        bear_case.append(f"U.S. equity markets are facing selling pressure today, with the S&P 500 sliding {abs(sp500_change):.2f}%.")
        
    # Crypto
    if btc_change > 1.5:
        bull_case.append(f"Bitcoin shows bullish resilience, surging {btc_change:.2f}% and leading positive crypto sentiment.")
    elif btc_change < -1.5:
        bear_case.append(f"Cryptocurrency markets are undergoing a correction, with Bitcoin falling {abs(btc_change):.2f}%.")
        
    # Individual Stocks
    nvda_change = nvda.get("change_pct", 0.0) or 0.0
    if nvda_change > 2.0:
        bull_case.append(f"NVIDIA is demonstrating notable strength with a {nvda_change:.2f}% advance, driving positive sentiment in the AI and semiconductor sector.")
    elif nvda_change < -2.0:
        bear_case.append(f"NVIDIA is experiencing a pullback of {abs(nvda_change):.2f}%, raising concerns about short-term tech exhaustion.")
        
    # Commodities / Yields / Dollar
    usd_change = usd.get("change_pct", 0.0) or 0.0
    yield_change = yield_10y.get("change_pct", 0.0) or 0.0
    if usd_change > 0.3:
        bear_case.append(f"A stronger US Dollar Index (+{usd_change:.2f}%) is creating headwinds for commodities and multinational equities.")
    elif usd_change < -0.3:
        bull_case.append(f"A softening US Dollar Index ({usd_change:.2f}%) is supporting commodity prices and offering stock tailwinds.")
        
    if yield_change > 1.5:
        bear_case.append(f"The 10-Year Treasury Yield has ticked up to {yield_10y.get('current_price', 0.0):.2f}%, exerting downward pressure on growth stocks.")
    elif yield_change < -1.5:
        bull_case.append(f"Treasury yields are easing down to {yield_10y.get('current_price', 0.0):.2f}%, indicating standard bond buying and risk aversion or relief in borrowing costs.")

    # Fill defaults if empty
    if not bull_case:
        bull_case.append("Defensive assets and interest-rate-sensitive sectors show signs of stabilizing.")
    if not bear_case:
        bear_case.append("Traders remain cautious ahead of upcoming macroeconomic data releases and central bank commentary.")
        
    analysis["bull_case"] = bull_case
    analysis["bear_case"] = bear_case

    # 3. Stock Insights
    stock_notes = []
    for s_name, s_data in [("NVIDIA", nvda), ("Apple", aapl), ("Microsoft", msft), ("Tesla", tsla)]:
        change = s_data.get("change_pct", 0.0) or 0.0
        price = s_data.get("current_price", 0.0) or 0.0
        action = "advancing" if change >= 0 else "declining"
        stock_notes.append(f"**{s_name}** is {action} {abs(change):.2f}% to ${price:,.2f}.")
        
    # Add NVDA focus
    nvda_headlines = [item['title'] for item in data["news"].get("NVDA", [])[:2]]
    nvda_news_str = f" Recent NVIDIA news highlights: '{' | '.join(nvda_headlines)}'." if nvda_headlines else ""
    
    analysis["stock_insights"] = (
        f"In corporate equities, major mega-cap tech stocks show mixed signals. "
        f"{' '.join(stock_notes)} NVIDIA is currently in a {'bullish' if nvda_change >= 0 else 'bearish'} posture. "
        f"{nvda_news_str} The tech sector's performance remains highly correlated with developments in Artificial Intelligence and semiconductor supply chains."
    )

    # 4. Crypto/BTC Focus
    btc_price = btc.get("current_price", 0.0) or 0.0
    btc_direction = "Up" if btc_change >= 0.5 else ("Down" if btc_change <= -0.5 else "Sideways/Consolidating")
    btc_news_titles = [item['title'] for item in data["news"].get("BTC", [])[:2]]
    btc_news_str = f" Top crypto headlines include: '{' | '.join(btc_news_titles)}'." if btc_news_titles else ""
    
    analysis["btc_outlook"] = (
        f"**Bitcoin (BTC-USD)** is trading at ${btc_price:,.2f}, representing a daily change of {btc_change:+.2f}%. "
        f"Based on current price action, Bitcoin's short-term direction appears to be **{btc_direction}**. "
        f"{btc_news_str} Support sits near ${btc_price*0.96:,.0f} with immediate resistance at ${btc_price*1.04:,.0f}."
    )

    # 5. Broader Market Direction Opinion
    if sp500_change > 0.4:
        market_dir = "Up"
        outlook_text = (
            "The broader market indices are exhibiting a bullish posture. Strong buying interest in high-beta tech "
            "and stabilizing yields suggest that buyers are in control of the current session. A continuation "
            "upward is expected, provided macro news remains favorable. Directional Bias: **Up**."
        )
    elif sp500_change < -0.4:
        market_dir = "Down"
        outlook_text = (
            "The broader market displays an active bearish tone. Equity indices are trading below key intraday levels, "
            "with capital rotating into safe havens such as gold or the US dollar. Sellers maintain command, suggesting "
            "further downward pressure in the near term. Directional Bias: **Down**."
        )
    else:
        market_dir = "Sideways/Neutral"
        outlook_text = (
            "The equity market is displaying consolidation behavior. Indecisive trading and mixed sector performance "
            "point to a neutral stance. Market participants appear to be squaring positions and waiting for clear "
            "catalysts (economic releases or earnings). Directional Bias: **Sideways/Neutral**."
        )
        
    analysis["market_outlook"] = outlook_text

    # 6. Levels to Watch (Calculated dynamically)
    analysis["levels_to_watch"] = {}
    for cat_name, cat_dict in [("Indices", "indices"), ("Crypto", "crypto"), ("Stocks", "stocks")]:
        analysis["levels_to_watch"][cat_name] = []
        for name, info in data[cat_dict].items():
            curr = info.get("current_price")
            if curr:
                # Basic pivot levels
                sup = curr * 0.985
                res = curr * 1.015
                analysis["levels_to_watch"][cat_name].append({
                    "name": name,
                    "price": f"${curr:,.2f}" if "Index" not in name and "Yield" not in name and "%" not in name and name != "10-Year Yield" else (f"{curr:.2f}%" if "Yield" in name else f"{curr:.2f}"),
                    "support": f"${sup:,.2f}" if "Index" not in name and "Yield" not in name and "%" not in name and name != "10-Year Yield" else (f"{sup:.2f}%" if "Yield" in name else f"{sup:.2f}"),
                    "resistance": f"${res:,.2f}" if "Index" not in name and "Yield" not in name and "%" not in name and name != "10-Year Yield" else (f"{res:.2f}%" if "Yield" in name else f"{res:.2f}")
                })

    return analysis

def run_ai_analysis(data, api_key):
    """
    Queries Gemini model to generate a rich, professional, and readable financial report.
    Adheres strictly to the guidelines and requested features.
    """
    print("Initializing Gemini API client for professional market analysis...")
    genai.configure(api_key=api_key)
    
    # Select available Flash model
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
    except Exception:
        # Fallback to older gemini model name if needed
        model = genai.GenerativeModel("gemini-1.5-flash")
        
    prompt = f"""
    You are a professional financial market analyst writing a daily market newspaper.
    Analyze the following market data and news headlines collected today:
    
    --- DATA START ---
    {json.dumps(data, indent=2)}
    --- DATA END ---
    
    Analyze the market and generate a JSON object matching this structure EXACTLY. Return ONLY the JSON object, do not wrap it in ```json ... ``` or add markdown:
    
    {{
      "tone": "Risk-on" or "Risk-off" or "Neutral" or "Mixed",
      "bull_case": [
        "Bullish point 1 based on data/news",
        "Bullish point 2 based on data/news",
        "Bullish point 3 based on data/news"
      ],
      "bear_case": [
        "Bearish point 1 based on data/news",
        "Bearish point 2 based on data/news",
        "Bearish point 3 based on data/news"
      ],
      "market_outlook": "Broader market opinion. Give your professional assessment of whether the broader market (S&P 500 / Nasdaq / general indices) will go UP, DOWN, or trade SIDEWAYS/NEUTRAL today or in the very short term. Provide clear reasoning referencing the yields, indices momentum, and macro calendar. Do not guarantee profits or use phrases like 'guaranteed profit' or '100% bullish'. Use words like 'The market appears to...', 'This suggests...', 'Traders should watch...'.",
      "stock_insights": "Analysis of key individual equities, with a strong focus on NVIDIA (NVDA) and its current environment (AI, tech trends, product news), along with insights on AAPL, MSFT, or TSLA based on the data/news. Give a directional bias for these key stocks.",
      "btc_outlook": "Dedicated analysis of Bitcoin (BTC-USD) and general crypto sentiment. You must give a clear opinion on whether BTC is going UP, DOWN, or SIDEWAYS/CONSOLIDATING with specific reasons based on price change, volumes, or news.",
      "levels_to_watch": {{
        "Indices": [
          {{"name": "S&P 500", "price": "current price", "support": "estimated support level", "resistance": "estimated resistance level"}},
          ...
        ],
        "Crypto": [
          {{"name": "Bitcoin", "price": "current price", "support": "estimated support level", "resistance": "estimated resistance level"}},
          ...
        ],
        "Stocks": [
          {{"name": "NVIDIA", "price": "current price", "support": "estimated support level", "resistance": "estimated resistance level"}},
          ...
        ]
      }}
    }}
    
    Requirements:
    1. Write in clear, professional English (or Spanish if requested - but wait, the prompt is in Spanish. Let's output Spanish for the editorial sections since the user requested: 'quiero un periodico de noticias diario ... y dime tu opinion ... en una pagina web'. Output the analysis fields ('market_outlook', 'stock_insights', 'btc_outlook', 'bull_case', 'bear_case') in Spanish to provide a native reading experience for the Spanish-speaking user!).
    2. Output Spanish for the generated text blocks! Ensure it sounds professional, fluent, and objective.
    3. Make sure the directional outlooks are clear and bold (e.g. 'Dirección: ALCISTA', 'Dirección: BAJISTA', 'Dirección: NEUTRAL' or 'CONSOLIDACIÓN').
    4. Adhere to the timezone America/New_York context.
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean potential markdown output if model wrapped in ```json
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text.rsplit("\n", 1)[0]
            text = text.strip()
            
        if text.startswith("json"):
            text = text[4:].strip()
            
        parsed_json = json.loads(text)
        
        # Verify and clean the parsed object has required keys
        required_keys = ["tone", "bull_case", "bear_case", "market_outlook", "stock_insights", "btc_outlook", "levels_to_watch"]
        for key in required_keys:
            if key not in parsed_json:
                raise ValueError(f"Gemini output is missing key: {key}")
                
        return parsed_json
    except Exception as e:
        print(f"Warning: Gemini API analysis failed or returned invalid JSON ({e}). Falling back to rule-based analysis...")
        return run_rule_based_analysis(data)

def analyze_market(data):
    """Main function to analyze market data, checking for API keys first."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        return run_ai_analysis(data, api_key)
    else:
        print("No GEMINI_API_KEY found in environment. Generating report using rule-based analysis (fallback).")
        # Translate to Spanish for fallback if requested by user
        res = run_rule_based_analysis(data)
        # Translate fallback values to Spanish to match the requested language
        res["tone_es"] = {"Risk-on": "Apetito por el Riesgo (Risk-on)", "Risk-off": "Aversión al Riesgo (Risk-off)", "Neutral": "Neutral", "Mixed": "Mixto"}.get(res["tone"], res["tone"])
        
        # Translate rule-based strings to Spanish
        res["bull_case"] = [
            point.replace("Major U.S. indices are exhibiting upward momentum, led by Nasdaq gains", "Los principales índices de EE.UU. muestran impulso alcista, liderados por el Nasdaq")
            .replace("Major U.S. indices are exhibiting upward momentum, led by S&P 500 gains", "Los principales índices de EE.UU. muestran impulso alcista, liderados por el S&P 500")
            .replace("Bitcoin shows bullish resilience, surging", "Bitcoin muestra resiliencia alcista, subiendo un")
            .replace("NVIDIA is demonstrating notable strength with a", "NVIDIA demuestra una fuerza notable con una subida de")
            .replace("A softening US Dollar Index", "Un índice del dólar estadounidense más débil")
            .replace("Treasury yields are easing down", "Los rendimientos de los bonos del Tesoro están bajando")
            for point in res["bull_case"]
        ]
        
        res["bear_case"] = [
            point.replace("U.S. equity markets are facing selling pressure today, with the S&P 500 sliding", "Los mercados de valores de EE.UU. enfrentan presión de venta hoy, con el S&P 500 cayendo")
            .replace("Cryptocurrency markets are undergoing a correction, with Bitcoin falling", "Los mercados de criptomonedas experimentan una corrección, con Bitcoin cayendo")
            .replace("NVIDIA is experiencing a pullback of", "NVIDIA experimenta un retroceso del")
            .replace("A stronger US Dollar Index", "Un índice del dólar estadounidense más fuerte")
            .replace("The 10-Year Treasury Yield has ticked up", "El rendimiento del Tesoro a 10 años ha subido")
            for point in res["bear_case"]
        ]
        
        # Simple Spanish market outlook translation template
        sp500_change = data["indices"].get("S&P 500", {}).get("change_pct", 0.0) or 0.0
        if sp500_change > 0.4:
            res["market_outlook"] = (
                "Los índices del mercado general muestran una postura alcista. El fuerte interés de compra en valores "
                "tecnológicos de beta alto y la estabilización de los rendimientos de los bonos sugieren que los compradores "
                "tienen el control de la sesión actual. Se espera una continuación al alza, siempre que las noticias macroeconómicas "
                "sigan siendo favorables. Sesgo Direccional: **ALCISTA (Subida)**."
            )
        elif sp500_change < -0.4:
            res["market_outlook"] = (
                "El mercado general muestra un tono bajista activo. Los índices cotizan por debajo de niveles clave intradía, "
                "con rotación de capital hacia refugios seguros como el oro o el dólar. Los vendedores mantienen el control, lo que "
                "sugiere una mayor presión a la baja en el corto plazo. Sesgo Direccional: **BAJISTA (Bajada)**."
            )
        else:
            res["market_outlook"] = (
                "El mercado de acciones muestra un comportamiento de consolidación lateral. La negociación indecisa y el "
                "rendimiento mixto de los sectores apuntan a una postura neutral. Los participantes del mercado parecen estar "
                "cerrando posiciones y esperando catalizadores claros (datos macroeconómicos o reportes de ganancias). Sesgo Direccional: **NEUTRAL (Lateral)**."
            )
            
        # NVIDIA and Stock insights translation template
        nvda_change = data["stocks"].get("NVIDIA", {}).get("change_pct", 0.0) or 0.0
        nvda_price = data["stocks"].get("NVIDIA", {}).get("current_price", 0.0) or 0.0
        res["stock_insights"] = (
            f"En el sector de renta variable corporativa, las principales acciones de megacapitalización tecnológica muestran señales mixtas. "
            f"**NVIDIA** cotiza a ${nvda_price:,.2f} ({nvda_change:+.2f}%), mostrando un comportamiento {'alcista en la sesión' if nvda_change >= 0 else 'de retroceso temporal'}. "
            f"El clima de NVIDIA parece {'favorable para seguir subiendo en el mediano plazo debido al fuerte impulso del sector de Inteligencia Artificial' if nvda_change >= 0 else 'cauteloso por la toma de beneficios tras los máximos recientes'}. "
            f"Acciones como Apple, Microsoft y Tesla se mueven en línea con el sentimiento tecnológico general."
        )
        
        # BTC outlook translation template
        btc_change = data["crypto"].get("Bitcoin", {}).get("change_pct", 0.0) or 0.0
        btc_price = data["crypto"].get("Bitcoin", {}).get("current_price", 0.0) or 0.0
        btc_dir = "ALCISTA (Subida)" if btc_change >= 0.5 else ("BAJISTA (Bajada)" if btc_change <= -0.5 else "NEUTRAL (Consolidación)")
        res["btc_outlook"] = (
            f"**Bitcoin (BTC-USD)** cotiza a ${btc_price:,.2f}, registrando un cambio diario de {btc_change:+.2f}%. "
            f"La tendencia de corto plazo para Bitcoin se clasifica como **{btc_dir}**. "
            f"El volumen de negociación y el flujo de noticias recientes influyen en este movimiento. "
            f"Se proyecta un soporte inmediato en los ${btc_price*0.96:,.0f} y la resistencia principal en los ${btc_price*1.04:,.0f}."
        )
        
        return res

if __name__ == "__main__":
    # Test script execution
    test_data = {
        "indices": {
            "S&P 500": {"name": "S&P 500", "symbol": "^GSPC", "current_price": 5350.0, "prev_price": 5300.0, "change_pct": 0.94},
            "Nasdaq 100": {"name": "Nasdaq 100", "symbol": "^IXIC", "current_price": 18500.0, "prev_price": 18300.0, "change_pct": 1.09},
            "Dow Jones": {"name": "Dow Jones", "symbol": "^DJI", "current_price": 39000.0, "prev_price": 38900.0, "change_pct": 0.26}
        },
        "stocks": {
            "NVIDIA": {"name": "NVIDIA", "symbol": "NVDA", "current_price": 120.5, "prev_price": 118.0, "change_pct": 2.12},
            "Apple": {"name": "Apple", "symbol": "AAPL", "current_price": 195.0, "prev_price": 194.5, "change_pct": 0.26},
            "Microsoft": {"name": "Microsoft", "symbol": "MSFT", "current_price": 425.0, "prev_price": 423.0, "change_pct": 0.47},
            "Tesla": {"name": "Tesla", "symbol": "TSLA", "current_price": 175.0, "prev_price": 178.0, "change_pct": -1.69}
        },
        "crypto": {
            "Bitcoin": {"name": "Bitcoin", "symbol": "BTC-USD", "current_price": 69000.0, "prev_price": 68000.0, "change_pct": 1.47},
            "Ethereum": {"name": "Ethereum", "symbol": "ETH-USD", "current_price": 3500.0, "prev_price": 3480.0, "change_pct": 0.57}
        },
        "commodities": {
            "Gold": {"name": "Gold", "symbol": "GC=F", "current_price": 2350.0, "prev_price": 2360.0, "change_pct": -0.42},
            "Crude Oil": {"name": "Crude Oil", "symbol": "CL=F", "current_price": 78.5, "prev_price": 77.8, "change_pct": 0.9}
        },
        "forex": {
            "US Dollar Index": {"name": "US Dollar Index", "symbol": "DX-Y.NYB", "current_price": 104.2, "prev_price": 104.5, "change_pct": -0.29}
        },
        "bonds": {
            "10-Year Yield": {"name": "10-Year Yield", "symbol": "^TNX", "current_price": 4.28, "prev_price": 4.31, "change_pct": -0.69}
        },
        "news": {
            "general": [{"title": "Markets rise on cooling inflation optimism", "link": "#", "pubDate": "", "description": ""}],
            "NVDA": [{"title": "NVIDIA hits record high amid AI chip demands", "link": "#", "pubDate": "", "description": ""}],
            "AAPL": [], "MSFT": [], "TSLA": [], "BTC": []
        }
    }
    
    print(json.dumps(analyze_market(test_data), indent=2))
