"""Multilingual UPI complaint-routing application. Run: streamlit run app.py"""
from __future__ import annotations
import os
import json
from collections import Counter
from datetime import datetime
from typing import Optional, Tuple
import joblib
import streamlit as st
import src.upi_engine as upi_engine
from src.upi_engine import analyse_complaint, build_complaint_summary, normalize_text

ROOT = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(ROOT, "models", "step4b_linear_svm.joblib")
VECTORIZER_PATH = os.path.join(ROOT, "models", "step4b_tfidf_vectorizer.joblib")
st.set_page_config(page_title="UPI Complaint Intelligence", page_icon="💳", layout="wide", initial_sidebar_state="expanded")
st.markdown("""<style>
/* Main content: force accessible dark text, independent of browser theme. */
.stApp{background:#f8fafc;color:#172033}.stApp p,.stApp li,.stApp label,.stApp [data-testid="stMarkdownContainer"],.stApp [data-testid="stCaptionContainer"],.stApp [data-testid="stExpander"] summary,.stApp [data-baseweb="tab"]{color:#172033}.block-container{max-width:1180px;padding-top:1.8rem;padding-bottom:3rem}
.hero{background:linear-gradient(120deg,#102a5c 0%,#1d4ed8 58%,#3b82f6 100%);padding:2.35rem 2.5rem;border-radius:20px;color:white;box-shadow:0 16px 38px rgba(30,64,175,.18);margin-bottom:1.5rem}.hero *,.hero h1,.hero p{color:white!important}.hero p{color:#dbeafe!important;margin:.55rem 0 0;font-size:1.04rem}
.card{background:#fff;border:1px solid #dbe4f0;border-radius:16px;padding:1.2rem;min-height:104px;box-shadow:0 5px 18px rgba(15,23,42,.055)}.eyebrow{color:#64748b!important;font-size:.78rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase}.big{color:#1d4ed8!important;font-size:1.28rem;font-weight:750;margin-top:.35rem}.small{color:#475569!important;margin-top:.3rem}.high{color:#b42318!important}.medium{color:#a15c00!important}.low{color:#087443!important}
/* Inputs, buttons, tabs, alerts and code blocks have fixed high-contrast pairs. */
.stApp input,.stApp textarea,.stApp [data-baseweb="select"] input{color:#172033!important;background:#fff!important}.stApp textarea::placeholder,.stApp input::placeholder{color:#64748b!important;opacity:1!important}.stApp [data-baseweb="select"]>div{color:#172033!important;background:#fff!important}.stApp [data-baseweb="tab"][aria-selected="true"]{color:#1d4ed8!important}
.stApp .stButton>button{background:#2563eb!important;color:#fff!important;border:1px solid #1d4ed8!important;border-radius:9px!important}.stApp .stButton>button:hover{background:#1e40af!important;color:#fff!important}.stApp .stButton>button *{color:#fff!important}.stApp [data-testid="stAlert"] *{color:#172033!important}
.stApp pre,.stApp pre code,.stApp [data-testid="stCodeBlock"] pre,.stApp [data-testid="stCodeBlock"] code{background:#0f172a!important;color:#f8fafc!important;text-shadow:none!important}.stApp [data-testid="stCodeBlock"] span{color:#f8fafc!important}
/* Expanders otherwise inherit the browser's dark-surface color in dark mode. */
.stApp [data-testid="stExpander"],.stApp [data-testid="stExpander"] details,.stApp [data-testid="stExpander"] summary{background:#fff!important;border-color:#cbd5e1!important}.stApp [data-testid="stExpander"] summary,.stApp [data-testid="stExpander"] summary *,.stApp [data-testid="stExpander"] [data-testid="stMarkdownContainer"] *{color:#172033!important}
/* Sidebar: a quiet navy surface with one warm safety accent. */
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#10203b 0%,#0d1728 100%);border-right:1px solid #263956}section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] *,section[data-testid="stSidebar"] h1,section[data-testid="stSidebar"] h2,section[data-testid="stSidebar"] h3{color:#f8fafc!important}section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] *,section[data-testid="stSidebar"] small{color:#a9b7cc!important}section[data-testid="stSidebar"] hr{border-color:#2a3d5a!important}section[data-testid="stSidebar"] [data-testid="stAlert"]{background:#fff3cd!important;border:1px solid #f2c96d!important;border-radius:12px!important}section[data-testid="stSidebar"] [data-testid="stAlert"] *,section[data-testid="stSidebar"] [data-testid="stAlert"] p{color:#713f12!important}
</style>""", unsafe_allow_html=True)

@st.cache_resource
def load_baseline() -> Tuple[Optional[object], Optional[object], Optional[str]]:
    """The BANKING77 model is optional and displayed only as a research baseline."""
    try:
        if not (os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH)):
            return None, None, "Model files are not present. UPI rule-based analysis remains available."
        return joblib.load(MODEL_PATH), joblib.load(VECTORIZER_PATH), None
    except Exception as exc:
        return None, None, f"Baseline unavailable: {exc}"

def baseline_prediction(text: str) -> Optional[str]:
    model, vectorizer, _ = load_baseline()
    try:
        return str(model.predict(vectorizer.transform([normalize_text(text)]))[0]) if model is not None and vectorizer is not None else None
    except Exception:
        return None


def follow_up_questions(intent: str):
    """Use new intent questions when available; allow a clean startup after a hot reload."""
    return getattr(upi_engine, "get_follow_up_questions", lambda _intent: ())(intent)


def structured_summary(result, answers: dict) -> str:
    builder = getattr(upi_engine, "build_structured_summary", None)
    return builder(result, answers) if builder else build_complaint_summary(result)


def answer_guidance(result, answers: dict) -> str:
    guidance = getattr(upi_engine, "personalised_guidance", None)
    return guidance(result, answers) if guidance else "Your selected details can be shared through the official support channel."


def key_terms(text: str):
    extractor = getattr(upi_engine, "extract_key_terms", None)
    return extractor(text) if extractor else []


def transcribe_audio(audio, selected_language: str) -> Tuple[Optional[str], Optional[str]]:
    """Transcribe a recorded clip with Google Speech Recognition when installed."""
    try:
        import speech_recognition as sr
        language_code = {
            "English": "en-IN",
            "Hinglish": "en-IN",
            "Hindi": "hi-IN",
            "Malayalam": "ml-IN",
        }.get(selected_language, "en-IN")
        audio.seek(0)
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio) as source:
            recorded_audio = recognizer.record(source)
        return recognizer.recognize_google(recorded_audio, language=language_code), None
    except ImportError:
        return None, "SpeechRecognition is not installed. Run: pip install -r requirements.txt"
    except Exception as error:
        return None, f"Transcription was unavailable: {error}. Please type the complaint instead."


TICKET_STORE_PATH = os.path.join(ROOT, "data", "ticket_history.json")


def load_tickets() -> list:
    """Load locally persisted, already-masked tickets."""
    try:
        with open(TICKET_STORE_PATH, "r", encoding="utf-8") as ticket_file:
            tickets = json.load(ticket_file)
        return tickets if isinstance(tickets, list) else []
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []


def save_tickets(tickets: list) -> None:
    """Atomically save only safe ticket fields to the local project data folder."""
    os.makedirs(os.path.dirname(TICKET_STORE_PATH), exist_ok=True)
    temporary_path = TICKET_STORE_PATH + ".tmp"
    with open(temporary_path, "w", encoding="utf-8") as ticket_file:
        json.dump(tickets, ticket_file, ensure_ascii=False, indent=2)
    os.replace(temporary_path, TICKET_STORE_PATH)


def add_ticket(result) -> None:
    """Store only the safe complaint summary for this browser session."""
    fingerprint = (result.sanitized_text, result.primary_intent)
    if st.session_state.get("last_ticket_fingerprint") == fingerprint:
        return
    ticket_number = len(st.session_state.tickets) + 1
    st.session_state.tickets.append({
        "Ticket ID": f"UPI-{ticket_number:04d}",
        "Created": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "Priority": result.severity,
        "Issue": result.title,
        "Language": result.language,
        "Status": "New",
        "Safe complaint": result.sanitized_text,
    })
    st.session_state.last_ticket_fingerprint = fingerprint
    save_tickets(st.session_state.tickets)

def set_sample(text: str) -> None:
    st.session_state.complaint_text = text
    st.session_state.pop("result", None)

if "complaint_text" not in st.session_state:
    st.session_state.complaint_text = ""
if "tickets" not in st.session_state:
    st.session_state.tickets = load_tickets()
with st.sidebar:
    st.markdown("## 💳 UPI Assistant")
    st.caption("Multilingual complaint support")
    st.divider()
    st.markdown("**Quick guide**")
    st.markdown("""
    - Paste or type the complaint text in any supported language
    - Choose a language manually only if auto-detect looks wrong
    - Review the suggested route, next steps, and safe summary before sharing
    - Use the support dashboard to review masked ticket history locally
    """)
    st.divider()
    st.markdown("**Safety first**")
    st.warning("Never enter or share your UPI PIN, OTP, CVV, full account number, or card number.")
    st.caption("This tool does not submit complaints or make banking decisions.")

st.markdown("""<div class="hero"><h1>💳 UPI Complaint Intelligence</h1><p>Explainable multilingual issue routing for safer, faster UPI support.</p></div>""", unsafe_allow_html=True)
tab_analyze, tab_dashboard, tab_insights, tab_about = st.tabs(["Analyze complaint", "Support dashboard", "Model insights", "Project story"])
with tab_analyze:
    st.markdown("### Sample complaints")
    samples = [
        ("English", "My UPI payment failed but money was deducted from my account."),
        ("Hindi", "मेरा पेमेंट फेल हो गया लेकिन पैसे कट गए"),
        ("Malayalam", "പണം ഡെബിറ്റ് ആയി പക്ഷേ പേയ്മെന്റ് പരാജയപ്പെട്ടു"),
        ("Romanized", "mera payment fail ho gaya lekin paise kat gaye"),
        ("Fraud", "I did not make this UPI transfer. It looks like fraud."),
    ]
    for column, (label, text) in zip(st.columns(5), samples):
        with column:
            if st.button(label, use_container_width=True): set_sample(text)
    if hasattr(st, "audio_input"):
        with st.expander("🎙️ Voice complaint input"):
            st.caption("Recording is optional. When you press Transcribe, the clip is sent to Google Speech Recognition for transcription; type your complaint instead if you do not wish to use this service.")
            voice_language = st.selectbox("Spoken language", ["English", "Hinglish", "Hindi", "Malayalam"], key="voice_language")
            if voice_language == "Malayalam":
                st.caption("Malayalam voice input works best when you speak clearly and avoid background noise.")
            voice_clip = st.audio_input("Record a short complaint", key="voice_clip")
            if voice_clip and st.button("Transcribe recording", key="transcribe_audio"):
                transcript, error = transcribe_audio(voice_clip, voice_language)
                if transcript:
                    st.session_state.complaint_text = transcript
                    st.success("Transcription added to the complaint box. Review it before analysing.")
                else:
                    st.warning(error)
    else:
        st.info("Voice capture requires a newer Streamlit version. Update dependencies to enable it.")
    st.markdown("### Describe the issue")
    col_input, col_options = st.columns([3, 1])
    with col_input:
        st.text_area("Complaint", key="complaint_text", height=150, placeholder="Example: My UPI payment failed but the amount was debited.", label_visibility="collapsed")
    with col_options:
        selected_language = st.selectbox("Language", ["Auto detect", "English", "Hindi", "Hinglish", "Malayalam", "Tamil", "Telugu", "Kannada"])
        st.caption("Auto-detection recognizes common Indian scripts and some Romanized Hindi/Malayalam signals.")
        analyse = st.button("🔎 Analyze complaint", type="primary", use_container_width=True)
    if analyse:
        if not st.session_state.complaint_text.strip(): st.warning("Enter a complaint or choose a sample first.")
        else:
            st.session_state.result = analyse_complaint(st.session_state.complaint_text, selected_language)
            st.session_state.baseline = baseline_prediction(st.session_state.complaint_text)
            add_ticket(st.session_state.result)
    result = st.session_state.get("result")
    if result:
        st.divider(); st.markdown("### Result")
        a, b, c = st.columns(3)
        a.markdown(f'<div class="card"><div class="eyebrow">Issue detected</div><div class="big">{result.title}</div><div class="small">{result.primary_intent}</div></div>', unsafe_allow_html=True)
        b.markdown(f'<div class="card"><div class="eyebrow">Routing confidence</div><div class="big">{result.confidence_label} · {result.confidence_score}%</div><div class="small">Based on clear complaint signals, not a banking probability.</div></div>', unsafe_allow_html=True)
        c.markdown(f'<div class="card"><div class="eyebrow">Recommended urgency</div><div class="big {result.severity.lower()}">{result.severity}</div><div class="small">Use official bank or UPI-app support for account action.</div></div>', unsafe_allow_html=True)
        if result.privacy_flags: st.warning("Privacy protection: potentially sensitive text was hidden in the summary: " + ", ".join(result.privacy_flags) + ". Do not share PINs or OTPs with anyone.")
        if result.confidence_label == "Low": st.info("I need one more detail for a precise route: " + result.clarification)
        left, right = st.columns([1.2, 1])
        with left:
            st.markdown("#### What to do next")
            for index, step in enumerate(result.next_steps, start=1): st.write(f"{index}. {step}")
            if result.primary_intent == "FRAUD_OR_UNAUTHORIZED_TRANSACTION": st.error("Act promptly. Use only verified, official bank or UPI-app contact methods.")
        with right:
            st.markdown("#### Other possible matches")
            for _, title, score in result.top_matches: st.progress(min(100, score * 12), text=f"{title} — matching signals: {score}")
            st.caption("These are transparent rule-match strengths, not model probabilities.")
        questions = follow_up_questions(result.primary_intent)
        answers = {}
        if questions:
            st.markdown("#### Smart follow-up questions")
            st.caption("These questions are selected from the detected intent to collect only the details relevant to support routing.")
            question_columns = st.columns(len(questions))
            for column, (field, prompt, options) in zip(question_columns, questions):
                with column:
                    answers[field] = st.selectbox(prompt, options, key=f"followup_{result.primary_intent}_{field}")
            st.info(answer_guidance(result, answers))
        st.markdown("#### Structured complaint summary")
        st.code(structured_summary(result, answers), language=None)
        st.caption("The summary combines the NLP result and selected follow-up details. It hides UPI IDs and long numeric strings where detected.")
        with st.expander("View NLP processing pipeline"):
            terms = key_terms(st.session_state.complaint_text)
            step_one, step_two, step_three, step_four = st.columns(4)
            step_one.metric("1. Input", "Received")
            step_two.metric("2. Language / script", result.language)
            step_three.metric("3. Writing style", result.writing_style)
            step_four.metric("4. Intent", result.primary_intent)
            st.write("**Normalized safe text:** " + result.sanitized_text)
            st.write("**Key terms extracted:** " + (", ".join(terms) if terms else "No strong lexical terms extracted"))
            st.write("**Why this route:** " + (", ".join(result.matched_signals) if result.matched_signals else "No strong signal; the app requested clarification."))
            if st.session_state.get("baseline"): st.info(f"Research baseline (BANKING77, broad banking data): `{st.session_state.baseline}`. This is shown for comparison only and does not replace the UPI-specific routing result.")
with tab_dashboard:
    st.markdown("### Support-agent dashboard")
    st.caption("Ticket history is saved locally in this project and contains masked complaint text, not raw sensitive information.")
    tickets = st.session_state.tickets
    if not tickets:
        st.info("Analyze a complaint to create the first support ticket.")
    else:
        priority_counts = Counter(ticket["Priority"] for ticket in tickets)
        language_counts = Counter(ticket["Language"] for ticket in tickets)
        fraud_count = sum(ticket["Priority"] == "High" for ticket in tickets)
        metric_one, metric_two, metric_three, metric_four = st.columns(4)
        metric_one.metric("Tickets", len(tickets))
        metric_two.metric("High priority", priority_counts.get("High", 0))
        metric_three.metric("Fraud / urgent", fraud_count)
        metric_four.metric("Languages", len(language_counts))
        selected_priority = st.selectbox("Filter by priority", ["All", "High", "Medium", "Low"], key="ticket_priority_filter")
        visible_tickets = tickets if selected_priority == "All" else [ticket for ticket in tickets if ticket["Priority"] == selected_priority]
        st.dataframe(visible_tickets, use_container_width=True, hide_index=True)
        chart_left, chart_right = st.columns(2)
        with chart_left:
            st.markdown("#### Complaints by priority")
            st.bar_chart({"Priority": list(priority_counts.keys()), "Tickets": list(priority_counts.values())}, x="Priority", y="Tickets")
        with chart_right:
            st.markdown("#### Complaints by language")
            st.bar_chart({"Language": list(language_counts.keys()), "Tickets": list(language_counts.values())}, x="Language", y="Tickets")
        if st.button("Clear saved ticket history"):
            st.session_state.tickets = []
            st.session_state.pop("last_ticket_fingerprint", None)
            save_tickets([])
            st.rerun()
with tab_insights:
    st.markdown("### Research model comparison")
    st.caption("Recorded evaluation on the BANKING77 test set. This is broad banking data, not a UPI-specific benchmark.")
    st.bar_chart({"Model":["Linear SVM", "Logistic Regression", "Naive Bayes", "XLM-RoBERTa"], "Macro F1":[0.8927,0.8403,0.8325,0.8048]}, x="Model", y="Macro F1")
    st.success("Best recorded baseline: TF-IDF + Linear SVM — 89.27% macro F1.")
    st.markdown("#### Why this project matters")
    st.write("Financial-support text is often informal, code-mixed, Romanized, or written in Indian scripts. This project studies how those forms affect complaint classification and demonstrates a safer, explainable UPI-support workflow.")
    with st.expander("Known limitation and next step"): st.write("The bundled ML model uses BANKING77 and includes general banking topics. A production version needs a consented UPI-specific multilingual dataset and formal evaluation by language, intent, and safety outcome.")
with tab_about:
    st.markdown("### From complaint to support route")
    st.markdown("**User complaint** → **language/script detection** → **privacy-aware display** → **explainable UPI issue routing** → **urgency and next steps** → **copyable official-support summary**")
    st.markdown("#### Project notes")
    st.write("1. Designed for Indian-language diversity.  \n2. Every UPI route is explainable through matched signals.  \n3. Results include concrete next steps, not only a label.  \n4. It warns users against sharing PINs and OTPs.  \n5. It transparently distinguishes UPI routing from the BANKING77 research model.")
    st.info("For education and testing only. Always use an official bank, NPCI, or UPI-provider channel for transaction disputes and fraud reports.")
_, _, baseline_status = load_baseline()
if baseline_status: st.caption(baseline_status)
