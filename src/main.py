import sys
import os
import logging
from dotenv import load_dotenv

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Explicitly load .env from the project root FIRST
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(root_dir, '.env'))

from src.graph import app, LeadGraphState

def main():
    logger.info("==========================================")
    logger.info("    🧠 B2B Lead Intel Agentic Pipeline    ")
    logger.info("==========================================\n")
    
    try:
        company_name = input("Enter Company Name: ").strip()
        company_url = input("Enter Company URL: ").strip()
        
        if not company_name or not company_url:
            logger.error("Error: Company Name and URL are required.")
            return

        logger.info("\n[SYSTEM] Initializing State...")
        
        # Create initial state dictionary
        initial_state = LeadGraphState(
            company_name=company_name,
            company_url=company_url,
            research_data=None,
            pain_points=None,
            email_draft=None
        )

        logger.info("[SYSTEM] Invoking LangGraph Pipeline (Thread ID: 1)...\n")
        
        # Config for persistence
        config = {"configurable": {"thread_id": "1"}}
        
        # Invoke the graph (it will stop before copywriter)
        result = app.invoke(initial_state, config=config)
        
        # Since it interrupts, we'd need a terminal-based way to resume if we wanted to support HITL in CLI
        # But for now, we'll focus on the Streamlit implementation as requested.
        
        logger.info("\n--- Pipeline paused for manual review. ---")
        confirm = input("Approve and generate email? (y/n): ").strip().lower()
        
        if confirm == 'y':
            # Resume graph
            result = app.invoke(None, config=config)
            
            logger.info("\n==========================================")
            logger.info("           📩 Final Email Draft           ")
            logger.info("==========================================\n")
            
            # Extract and print the final email_draft from the resulting state
            email_draft = result.get("email_draft")
            if email_draft:
                logger.info(f"Subject: {email_draft.subject_line}")
                logger.info("-" * 30)
                logger.info(email_draft.email_body)
            else:
                logger.warning("No email draft was generated.")
        else:
            logger.info("Pipeline cancelled by user.")
            
        logger.info("\n==========================================")
        logger.info("           ✅ Pipeline Complete!          ")
        logger.info("==========================================")

    except KeyboardInterrupt:
        logger.info("\n[SYSTEM] Process interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n[ERROR] An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
