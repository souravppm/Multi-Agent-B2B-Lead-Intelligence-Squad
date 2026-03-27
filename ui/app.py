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
from src.utils.database import init_db, save_lead, get_all_leads

# Initialize database
init_db()

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
    
    tab1, tab2 = st.tabs(["🎯 Generate New Lead", "📚 Lead History"])

    with tab1:
        # Lead Generation UI
        st.header("🎯 Target Input")
        col_in1, col_in2 = st.columns(2)
        with col_in1:
            company_name = st.text_input("Company Name", value=st.session_state.get('company_name', ""), placeholder="e.g., Acme Corp")
        with col_in2:
            company_url = st.text_input("Company URL", value=st.session_state.get('company_url', ""), placeholder="e.g., https://acme.com")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Reset Pipeline", use_container_width=True):
                st.session_state.phase = "input"
                st.session_state.result = None
                st.session_state.thread_id = str(uuid.uuid4())
                st.rerun()
        with col_btn2:
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
                    email_draft=None,
                    feedback=None,
                    revision_count=0
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
                        if hasattr(r_data, 'recent_news') and r_data.recent_news:
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

                            # Save lead to local SQLite database comfortably
                            res = st.session_state.result
                            r_data = res.get("research_data")
                            p_data = res.get("pain_points")
                            e_data = res.get("email_draft")
                            eval_data_save = res.get("evaluation")

                            save_lead(
                                company_name=st.session_state.get('company_name', 'N/A'),
                                company_url=st.session_state.get('company_url', 'N/A'),
                                summary=getattr(r_data, 'company_summary', 'N/A') if r_data else "N/A",
                                pain_points=", ".join(getattr(p_data, 'pain_points', [])) if p_data else "N/A",
                                email_draft=getattr(e_data, 'email_body', 'N/A') if e_data else "N/A",
                                score=getattr(eval_data_save, 'score', 0) if eval_data_save else 0
                            )
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error resuming graph: {e}")

        # PHASE 3: Final Output
        if st.session_state.phase == "final":
            state = st.session_state.result
            if state is None:
                st.warning("⚖️ Pipeline state is being initialized. Please wait...")
                return

            st.divider()
            
            # ---------------- ULTR-SAFE RENDERING BLOCK ----------------
            # Safely get variables from the state, defaulting to None if missing
            eval_output = state.get('evaluation', None) # Map evaluation to eval_output to match score lookup
            email_output = state.get('email_draft', None)
            revisions = state.get('revision_count', 0)

            # Render Evaluator Feedback Safely
            st.subheader("⚖️ AI Judge Evaluation")
            if eval_output is not None:
                # Handle both Pydantic model and standard dictionary cases
                score_val = getattr(eval_output, 'score', 'N/A') if not isinstance(eval_output, dict) else eval_output.get('score', 'N/A')
                feedback_val = getattr(eval_output, 'feedback', 'No feedback.') if not isinstance(eval_output, dict) else eval_output.get('feedback', 'No feedback.')
                
                col1, col2 = st.columns(2)
                col1.metric("Quality Score", f"{score_val}/10")
                col2.metric("Revisions", revisions)
                st.info(f"**Feedback:** {feedback_val}")
            else:
                st.warning("Evaluation data is currently unavailable or generating...")

            # Render Final Email Safely
            st.subheader("📬 Final Email Draft")
            if email_output is not None:
                sub_val = getattr(email_output, 'subject_line', 'No Subject') if not isinstance(email_output, dict) else email_output.get('subject_line', 'No Subject')
                body_val = getattr(email_output, 'email_body', 'No Body') if not isinstance(email_output, dict) else email_output.get('email_body', 'No Body')
                
                st.markdown(f"**Subject:** {sub_val}")
                st.text_area('Email Content', value=body_val, height=300)
            else:
                st.warning("Email draft is currently unavailable or generating...")
            # --- Actions Section ---
            st.divider()
            if st.button("🔄 Regenerate Email", use_container_width=True):
                with st.spinner("🔄 AI is regenerating and evaluating the email..."):
                    try:
                        # 1. Clear old specific state and Rewind to analyst node
                        # This forces the graph to run 'copywriter' next.
                        app.update_state(config, {
                            "email_draft": None,
                            "evaluation": None,
                            "feedback": None,
                            "revision_count": 0
                        }, as_node="analyst")
                        
                        # 2. Re-invoke the LangGraph workflow to continue
                        new_state = app.invoke(None, config=config)
                        
                        # 3. CRUCIAL: Update the Streamlit session state with the new graph output!
                        st.session_state.result = new_state 
                        
                        # 4. Defensive Database Sync (Save the new version)
                        r_data = new_state.get("research_data")
                        p_data = new_state.get("pain_points")
                        e_data = new_state.get("email_draft")
                        ev_data = new_state.get("evaluation")

                        save_lead(
                            company_name=st.session_state.get('company_name', 'N/A'),
                            company_url=st.session_state.get('company_url', 'N/A'),
                            summary=getattr(r_data, 'company_summary', 'N/A') if r_data else 'N/A',
                            pain_points=", ".join(getattr(p_data, 'pain_points', [])) if p_data else 'N/A',
                            email_draft=getattr(e_data, 'email_body', 'N/A') if e_data else 'N/A',
                            score=getattr(ev_data, 'score', 0) if ev_data else 0
                        )
                        
                        # 5. Force Streamlit to re-render the page with the newly generated data
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error regenerating email: {e}")

    with tab2:
        st.header("📚 Lead History")
        leads = get_all_leads()
        
        if not leads:
            st.info("No leads saved yet. Start generating intel in the first tab!")
        else:
            # Table overview
            import pandas as pd
            df = pd.DataFrame(leads)
            # Reorder and format
            display_df = df[['company_name', 'company_url', 'score', 'created_at']].copy()
            st.dataframe(display_df, use_container_width=True)
            
            st.divider()
            st.subheader("🔍 Detailed View")
            for lead in leads:
                # Assuming created_at is at a specific key if returned as dict
                timestamp = lead.get('created_at', 'N/A')
                with st.expander(f"🏢 {lead['company_name']} - {timestamp} (Score: {lead['score']}/10)"):
                    st.write(f"**URL:** {lead['company_url']}")
                    st.write(f"**Insight Summary:** {lead['summary']}")
                    st.write(f"**Key Pain Points:** {lead['pain_points']}")
                    st.markdown("---")
                    st.markdown("#### 💌 Generated Email Draft")
                    st.text_area('Email Draft', value=lead['email_draft'], height=200, key=f"hist_{lead['id']}")

if __name__ == "__main__":
    main()
