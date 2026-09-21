import json
import os
import sys
from pathlib import Path

ROOT = Path(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "code"))

from app import read_ticket_rows, get_agent, summarize, ticket_csv_path

def main():
    print("Loading agent and initializing ML pipeline...")
    agent = get_agent()
    print("Done loading agent.")
    
    rows = read_ticket_rows()
    print(f"Read {len(rows)} tickets.")
    
    limit = 500
    enriched = []
    
    for index, row in enumerate(rows[: max(1, min(limit, 500))], start=1):
        print(f"Processing row {index}...")
        details = agent.predict_details(row).to_api()
        prediction = details["prediction"]
        ticket = details["ticket"]
        analysis = details["analysis"]
        enriched.append(
            {
                "id": index,
                "subject": ticket["subject"],
                "issue": ticket["issue"],
                "company": ticket["company"] or analysis["company"],
                "status": prediction["status"],
                "product_area": prediction["product_area"],
                "request_type": prediction["request_type"],
                "confidence": analysis["confidence"],
                "top_score": analysis["top_score"],
                "recommendations": details["recommendations"],
                "justification": prediction["justification"],
            }
        )
    
    output = {
        "source": str(ticket_csv_path().name),
        "rows": enriched,
        "summary": summarize(enriched),
    }
    
    out_path = ROOT / "data" / "precomputed_dataset.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"Saved {len(enriched)} rows to {out_path}.")

if __name__ == "__main__":
    main()
