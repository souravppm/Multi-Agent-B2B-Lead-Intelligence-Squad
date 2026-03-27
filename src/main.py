import sys
import os
from dotenv import load_dotenv

# Explicitly load .env from the project root FIRST
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(root_dir, '.env'))

from src.graph import app, LeadGraphState

def main():
    print("==========================================")
    print("    🧠 B2B Lead Intel Agentic Pipeline    ")
    print("==========================================\n")
    
    try:
        company_name = input("Enter Company Name: ").strip()
        company_url = input("Enter Company URL: ").strip()
        
        if not company_name or not company_url:
            print("Error: Company Name and URL are required.")
            return

        print("\n[SYSTEM] Initializing State...")
        
        # Create initial state dictionary
        initial_state = LeadGraphState(
            company_name=company_name,
            company_url=company_url,
            research_data=None,
            pain_points=None,
            email_draft=None
        )

        print("[SYSTEM] Invoking LangGraph Pipeline...\n")
        
        # Invoke the graph
        result = app.invoke(initial_state)
        
        print("\n==========================================")
        print("           📩 Final Email Draft           ")
        print("==========================================\n")
        
        # Extract and print the final email_draft from the resulting state
        email_draft = result.get("email_draft")
        if email_draft:
            print(f"Subject: {email_draft.subject_line}")
            print("-" * 30)
            print(email_draft.email_body)
        else:
            print("No email draft was generated.")
            
        print("\n==========================================")
        print("           ✅ Pipeline Complete!          ")
        print("==========================================")

    except KeyboardInterrupt:
        print("\n[SYSTEM] Process interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
