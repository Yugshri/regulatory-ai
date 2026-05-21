import streamlit as st
import os
import uuid
from dotenv import load_dotenv
from google import genai
from config import APP_NAME, APP_VERSION, STATUS_OPTIONS, AI_MODEL
from extractor import extract_text_from_pdf, validate_circular_text
from ai_engine import extract_maps, validate_completion
from utils import maps_to_excel, get_audit_log_entry
from database import DatabaseManager
from models import MAP, CircularSession

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ---- DATABASE INIT ----
db = DatabaseManager()

# ---- SESSION ID ----
if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(uuid.uuid4())

session_id = st.session_state['session_id']

# ---- PAGE SETUP ----
st.set_page_config(
    page_title="RegAI",
    page_icon="🏦",
    layout="wide"
)

# ---- HEADER ----
col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.title(f"🏦 {APP_NAME}")
    st.caption(f"v{APP_VERSION} · Upload RBI/SEBI circular → Get Measurable Action Points instantly")
with col_h2:
    maps_count = len(db.load_maps(session_id))
    st.metric("Session MAPs", maps_count)

st.divider()

# ---- SIDEBAR ----
with st.sidebar:
    st.header("⚙️ Settings")
    show_risk = st.toggle("Show Compliance Risk", value=True)
    show_effort = st.toggle("Show Estimated Effort", value=True)

    st.divider()
    st.header("📋 Audit Trail")
    audit_logs = db.get_audit_log(session_id)
    if audit_logs:
        for log in audit_logs:
            st.caption(f"🕐 {log['timestamp']}")
            st.caption(f"MAP-{log['map_id']}: {log['old_status']} → {log['new_status']}")
            st.divider()
    else:
        st.caption("No changes yet")

# ---- INPUT TABS ----
tab1, tab2 = st.tabs(["📄 Upload PDF", "📝 Paste Text"])

circular_text = ""

with tab1:
    uploaded_file = st.file_uploader("Upload RBI/SEBI Circular PDF", type="pdf")
    if uploaded_file:
        try:
            text, pages, chars = extract_text_from_pdf(uploaded_file)
            if text:
                circular_text = text
                is_valid, message = validate_circular_text(text)
                st.success(f"PDF loaded! {pages} pages, {chars} characters extracted.")
                st.info(message)
                st.text_area("Extracted Text Preview", text[:500] + "...", height=150, disabled=True)
            else:
                st.error("PDF se text extract nahi hua")
        except Exception as e:
            st.error(str(e))

with tab2:
    pasted_text = st.text_area(
        "Paste Regulatory Circular Here",
        height=200,
        placeholder="Paste RBI / SEBI circular text here..."
    )
    if pasted_text:
        circular_text = pasted_text
        is_valid, message = validate_circular_text(pasted_text)
        st.info(message)

# ---- EXTRACT BUTTON ----
if st.button("🚀 Extract Action Points", type="primary", use_container_width=True):
    if not circular_text.strip():
        st.warning("Bhai kuch paste kar ya PDF upload kar pehle!")
    else:
        with st.spinner("AI analyze kar raha hai..."):
            try:
                maps = extract_maps(circular_text)
                
                # Database mein save karo
                db.save_maps(maps, session_id)
                
                # Session state mein bhi rakho
                st.session_state['maps'] = maps
                st.session_state['circular_text'] = circular_text
                
                st.success(f"✅ {len(maps)} MAPs extracted aur database mein save!")
            except Exception as e:
                st.error(str(e))

# ---- DASHBOARD ----
maps = db.load_maps(session_id)

if maps:
    st.divider()

    main_col, chat_col = st.columns([2, 1])

    with main_col:
        st.subheader("📊 Compliance Dashboard")

        # ---- METRICS ----
        total = len(maps)
        high = len([m for m in maps if m['priority'] == 'High'])
        depts = len(set(m['department'] for m in maps))
        pending = len([m for m in maps if m['status'] == 'Pending'])
        completed = len([m for m in maps if m['status'] == 'Completed'])
        rate = round(completed / total * 100, 1) if total > 0 else 0

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total MAPs", total)
        col2.metric("High Priority", high)
        col3.metric("Departments", depts)
        col4.metric("Pending", pending)
        col5.metric("Completion %", f"{rate}%")

        st.divider()

        # ---- CHARTS ----
        col_c1, col_c2 = st.columns(2)

        with col_c1:
            st.subheader("📈 Status Overview")
            status_data = {}
            for m in maps:
                status_data[m['status']] = status_data.get(m['status'], 0) + 1
            st.bar_chart(status_data)

        with col_c2:
            st.subheader("🏢 By Department")
            dept_data = {}
            for m in maps:
                dept_data[m['department']] = dept_data.get(m['department'], 0) + 1
            st.bar_chart(dept_data)

        st.divider()

        # ---- FILTERS ----
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            all_depts = ["All"] + list(set(m['department'] for m in maps))
            selected_dept = st.selectbox("Filter by Department", all_depts)
        with col_f2:
            selected_priority = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])

        filtered = maps
        if selected_dept != "All":
            filtered = [m for m in filtered if m['department'] == selected_dept]
        if selected_priority != "All":
            filtered = [m for m in filtered if m['priority'] == selected_priority]

        st.caption(f"Showing {len(filtered)} of {len(maps)} MAPs")

        # ---- MAPs LIST ----
        for m in filtered:
            priority_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(m['priority'], "⚪")
            status_icon = {"Pending": "⏳", "In Progress": "🔄", "Completed": "✅", "Overdue": "🚨"}.get(m['status'], "⏳")

            with st.expander(f"{priority_color} MAP-{m['id']} | {m['department']} | {m['deadline']} {status_icon}"):
                col_m1, col_m2 = st.columns([3, 1])

                with col_m1:
                    st.write(f"**Action:** {m['action']}")
                    st.write(f"**Department:** {m['department']}")
                    st.write(f"**Deadline:** {m['deadline']}")
                    if show_risk and m.get('compliance_risk'):
                        st.error(f"⚠️ Risk: {m['compliance_risk']}")
                    if show_effort and m.get('estimated_effort'):
                        st.write(f"**Effort:** {m['estimated_effort']}")

                with col_m2:
                    st.write(f"**Priority:** {m['priority']}")
                    st.write(f"**Status:** {m['status']}")

                    new_status = st.selectbox(
                        "Update Status",
                        STATUS_OPTIONS,
                        key=f"status_{m['id']}",
                        index=STATUS_OPTIONS.index(m['status']) if m['status'] in STATUS_OPTIONS else 0
                    )

                    if new_status != m['status']:
                        # Database mein update karo
                        db.update_map_status(m['id'], new_status, m['status'], session_id)
                        st.success("Updated ✅")
                        st.rerun()

                    if m['status'] == 'Completed':
                        if st.button(f"🔍 Validate", key=f"validate_{m['id']}"):
                            with st.spinner("Validating..."):
                                success, result = validate_completion(m)
                                if success:
                                    for q in result.get('validation_questions', []):
                                        st.write(f"• {q}")

        st.divider()

        # ---- EXPORT ----
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            import json
            excel_buffer = maps_to_excel(maps)
            st.download_button(
                label="⬇️ Download Excel",
                data=excel_buffer,
                file_name=f"regulatory_maps_{len(maps)}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        with col_e2:
            st.download_button(
                label="⬇️ Download JSON",
                data=json.dumps(maps, indent=2),
                file_name=f"regulatory_maps_{len(maps)}.json",
                mime="application/json",
                use_container_width=True
            )

    # ---- CHATBOT ----
    with chat_col:
        st.subheader("💬 AI Compliance Assistant")
        st.caption("MAPs ke baare mein kuch bhi pooch")

        # Chat history database se load karo
        chat_history = db.load_chat_history(session_id)

        # Display chat history
        for msg in chat_history:
            with st.chat_message(msg['role']):
                st.write(msg['content'])

        user_question = st.chat_input("Deadline, department, risk kuch bhi pooch...")

        if user_question:
            # User message display
            with st.chat_message('user'):
                st.write(user_question)

            # Database mein save karo
            db.save_chat_message(session_id, 'user', user_question)

            with st.chat_message('assistant'):
                with st.spinner("..."):

                    # Latency fix - sirf relevant MAPs bhejo
                    high_priority_maps = [m for m in maps if m['priority'] == 'High'][:10]

                    prompt = f"""
You are a regulatory compliance assistant for an Indian bank.
Be concise - max 80 words.
Answer in the same language as the question (Hindi/English/Hinglish).

High Priority MAPs for context:
{high_priority_maps}

Total MAPs in system: {len(maps)}

Question: {user_question}
"""
                    response = client.models.generate_content(
                        model=AI_MODEL,
                        contents=prompt
                    )

                    answer = response.text
                    st.write(answer)

                    # Database mein save karo
                    db.save_chat_message(session_id, 'assistant', answer)