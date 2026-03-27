import streamlit as st
import sys
import os
from dotenv import load_dotenv

# Ensure src module is accessible when running from terminal
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)

# Explicitly load .env from the root directory FIRST
load_dotenv(os.path.join(root_dir, '.env'))

from src.graph import app, LeadGraphState

def main():
    """Main rendering function for the Streamlit Front-End."""
    st.set_page_config(
        page_title="Multi-Agent B2B Lead Intelligence",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🤖 Multi-Agent B2B Lead Intelligence")
    st.markdown("Generate personalized, data-driven lead intelligence with autonomous AI agents.")
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("🎯 Target Input")
        company_name = st.text_input("Company Name", placeholder="e.g., Acme Corp")
        company_url = st.text_input("Company URL", placeholder="e.g., https://acme.com")
        
        generate_btn = st.button("Generate Intel", use_container_width=True, type="primary")

    if generate_btn:
        if not company_name or not company_url:
            st.error("⚠️ Please provide both the Company Name and the Company URL.")
        else:
            st.success(f"Target accepted: **{company_name}**. Initializing AI Agents...")
            
            # Create initial state dictionary
            initial_state = LeadGraphState(
                company_name=company_name,
                company_url=company_url,
                research_data=None,
                pain_points=None,
                email_draft=None
            )

            # Visually show progress using st.status
            try:
                with st.status("🕵️‍♂️ Agents are analyzing the target...", expanded=True) as status:
                    st.write("1. **Researcher Agent:** Searching the web for news and site data...")
                    st.write("2. **Analyst Agent:** Identifying pain points...")
                    st.write("3. **Copywriter Agent:** Drafting personalized cold email...")
                    
                    # The actual execution happens here (blocking call)
                    result = app.invoke(initial_state)
                    status.update(label="Analysis Complete! Agents finished successfully.", state="complete", expanded=False)
                
                # Layout: Displaying results
                st.header("📩 Generated Email Draft")
                email_draft = result.get("email_draft")
                if email_draft:
                    st.subheader(f"Subject: {email_draft.subject_line}")
                    st.markdown(f"```text\n{email_draft.email_body}\n```")
                else:
                    st.warning("No email draft generated.")
                    
                st.divider()
                st.subheader("🔍 AI Reasoning & Intelligence")
                
                # Hidden reasoning using expanders
                col1, col2 = st.columns(2)
                with col1:
                    with st.expander("🕵️‍♂️ Researcher Output (Company Intel)", expanded=False):
                        res = result.get("research_data")
                        if res:
                            st.write(f"**Summary:** {res.company_summary}")
                            st.write("**Recent News:**")
                            for news in res.recent_news:
                                st.write(f"- {news}")
                        else:
                            st.write("No data available.")
                        
                with col2:
                    with st.expander("🧠 Analyst Output (Pain Points)", expanded=False):
                        analysis = result.get("pain_points")
                        if analysis:
                            for point in analysis.pain_points:
                                st.write(f"🎯 {point}")
                        else:
                            st.write("No pain points identified.")
                        
            except Exception as e:
                st.error(f"An error occurred during execution: {e}")

if __name__ == "__main__":
    main()
