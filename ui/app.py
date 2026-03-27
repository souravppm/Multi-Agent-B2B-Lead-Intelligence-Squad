import streamlit as st
import sys
import os
import uuid
from dotenv import load_dotenv

# Ensure src module is accessible when running from terminal
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)

# Explicitly load .env from the root directory FIRST
load_dotenv(os.path.join(root_dir, '.env'))

from src.graph import app, LeadGraphState

# Initialize session state for Human-in-the-Loop (HITL) workflow
if 'thread_id' not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if 'phase' not in st.session_state:
    st.session_state.phase = "input"  # Phases: input, review, final
if 'result' not in st.session_state:
    st.session_state.result = None

def main():
    """Main rendering function for the Streamlit Front-End with HITL support."""
    st.set_page_config(
        page_title="Multi-Agent B2B Lead Intelligence",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🤖 Multi-Agent B2B Lead Intelligence (HITL)")
    st.markdown("Autonomous agents with a manual review step for maximum quality.")
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("🎯 Target Input")
        company_name = st.text_input("Company Name", value=st.session_state.get('company_name', ""), placeholder="e.g., Acme Corp")
        company_url = st.text_input("Company URL", value=st.session_state.get('company_url', ""), placeholder="e.g., https://acme.com")
        
        if st.button("Reset Pipeline", use_container_width=True):
            st.session_state.phase = "input"
            st.session_state.result = None
            st.session_state.thread_id = str(uuid.uuid4())
            st.rerun()

        generate_btn = st.button(
            "Generate Intel", 
            use_container_width=True, 
            type="primary", 
            disabled=(st.session_state.phase != "input")
        )

    # Persistence Configuration
    config = {"configurable": {"thread_id": st.session_state.thread_id}}

    # PHASE 1: Research & Analysis
    if generate_btn and st.session_state.phase == "input":
        if not company_name or not company_url:
            st.error("⚠️ Please provide both the Company Name and the Company URL.")
        else:
            st.session_state.company_name = company_name
            st.session_state.company_url = company_url
            
            # Create initial state dictionary
            initial_state = LeadGraphState(
                company_name=company_name,
                company_url=company_url,
                research_data=None,
                pain_points=None,
                email_draft=None
            )

            # Execution happens here (Researcher + Analyst)
            try:
                with st.status("🕵️‍♂️ Agents are analyzing the target...", expanded=True) as status:
                    st.write("1. **Researcher Agent:** Searching the web...")
                    st.write("2. **Analyst Agent:** Identifying pain points...")
                    
                    # Phase 1: Run until the first interrupt (before copywriter)
                    st.session_state.result = app.invoke(initial_state, config=config)
                    st.session_state.phase = "review"
                    
                    status.update(label="Initial Analysis Complete! Pending Review.", state="complete", expanded=False)
                st.rerun()
            except Exception as e:
                st.error(f"An error occurred during execution: {e}")

    # PHASE 2: Manual Review & Approval
    if st.session_state.phase in ["review", "final"]:
        res = st.session_state.result
        st.divider()
        st.subheader("🔍 AI Reasoning & Intelligence (Review Step)")
        
        # Display analysis results for review
        col1, col2 = st.columns(2)
        with col1:
            with st.expander("🕵️‍♂️ Researcher Output (Company Intel)", expanded=True):
                r_data = res.get("research_data")
                if r_data:
                    st.write(f"**Summary:** {r_data.company_summary}")
                    st.write("**Recent News:**")
                    for news in r_data.recent_news:
                        st.write(f"- {news}")
                else:
                    st.write("No data available.")
                        
        with col2:
            with st.expander("🧠 Analyst Output (Pain Points)", expanded=True):
                a_data = res.get("pain_points")
                if a_data:
                    for point in a_data.pain_points:
                        st.write(f"🎯 {point}")
                else:
                    st.write("No pain points identified.")

        if st.session_state.phase == "review":
            st.info("💡 Review the intelligence above. If satisfied, click **Approve** to generate the final email.")
            if st.button("✅ Approve & Draft Email", type="primary", use_container_width=True):
                try:
                    with st.spinner("✍️ Copywriter is drafting the personalized email..."):
                        # Phase 2: Resume graph with None input to pick up where we left off
                        st.session_state.result = app.invoke(None, config=config)
                        st.session_state.phase = "final"
                    st.rerun()
                except Exception as e:
                    st.error(f"Error resuming graph: {e}")

    # PHASE 3: Final Output
    if st.session_state.phase == "final":
        st.divider()
        st.header("📩 Final Email Draft")
        email = st.session_state.result.get("email_draft")
        if email:
            # Professional Subject Line
            st.markdown(f"### 📬 **Subject:** {email.subject_line}")
            
            # Premium styled card for the email body (avoids horizontal scroll)
            body_html = email.email_body.replace('\n', '<br>')
            st.markdown(f"""
                <div style="
                    background-color: #121212; 
                    padding: 2.5rem; 
                    border-radius: 15px; 
                    border-left: 5px solid #ff4b4b;
                    color: #ffffff; 
                    font-size: 1.1rem;
                    line-height: 1.7;
                    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
                    margin: 1.5rem 0;
                    font-family: 'Inter', system-ui, -apple-system, sans-serif;
                    white-space: normal;
                    word-wrap: break-word;
                ">
                    {body_html}
                </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("No email draft generated.")
        
        st.success("✅ Full pipeline completed successfully!")

if __name__ == "__main__":
    main()
