import os
import sys
import argparse
from datetime import datetime
import pytz
from dotenv import load_dotenv

# Ensure the parent directory is in python path so scripts can import each other
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.fetch_market_data import fetch_all_market_data
from scripts.analyze_market import analyze_market
from scripts.render_report import render_report

def main():
    # Load environment variables from .env if it exists (for local testing)
    load_dotenv()
    
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Daily Market Newspaper Generator")
    parser.add_argument(
        "--force", 
        action="store_true", 
        help="Force report generation even if it is not 8:00 AM New York time"
    )
    args = parser.parse_args()
    
    # Timezone handling
    tz = pytz.timezone("America/New_York")
    ny_now = datetime.now(tz)
    date_str = ny_now.strftime("%Y-%m-%d")
    hour = ny_now.hour
    minute = ny_now.minute
    
    print(f"Current Time in America/New_York: {ny_now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # 8:00 AM New York check (Cron job runs hourly, so we catch 8:00 AM)
    if not args.force:
        if hour != 8:
            print(f"Skipping generation. Current hour is {hour}, report is scheduled for 8:00 AM Eastern Time.")
            print("Use the '--force' flag to manually trigger generation.")
            sys.exit(0)
        else:
            print("Time check passed. Starting scheduled daily report generation...")
    else:
        print("Force flag detected. Proceeding with manual report generation...")

    # Define root workspace directory (parent of scripts directory)
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Step 1: Fetch data
        print("\n--- STEP 1: Fetching Market Data ---")
        market_data = fetch_all_market_data()
        
        # Step 2: Analyze data
        print("\n--- STEP 2: Running Market Analysis ---")
        analysis = analyze_market(market_data)
        
        # Step 3: Render files (Markdown, index.html, archive HTML, archive JSON)
        print("\n--- STEP 3: Rendering Report & Updating Site ---")
        render_report(date_str, market_data, analysis, root_dir)
        
        print("\nSuccess! Daily Market Newspaper generated and published.")
        
    except Exception as e:
        print(f"\nError during report generation: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
