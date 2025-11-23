import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json
import os

st.set_page_config(page_title="Booking Guild Team Health", layout="centered")

if 'submitted' not in st.session_state:
    st.session_state.submitted = False

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

RESPONSE_SCORES = {
    "Strongly disagree": 1,
    "Disagree": 2,
    "Neutral": 3,
    "Agree": 4,
    "Strongly agree": 5
}

MANAGER_SCORES = {
    "Too directive": 1,
    "Just right": 3,
    "Too hands off": 5
}

TEAM_OPTIONS = ["Flights", "Hotels"]

@st.cache_resource
def setup_sheets_client():
    """Initialize Google Sheets client"""
    creds = None

    # Try 1: Reading from secrets.toml [service_account_info] section (Streamlit Cloud)
    if "service_account_info" in st.secrets:
        try:
            creds = Credentials.from_service_account_info(dict(st.secrets["service_account_info"]), scopes=SCOPES)
            return gspread.authorize(creds)
        except Exception as e:
            st.error(f"❌ Error loading credentials from secrets: {e}")
            st.stop()

    # Try 2: Fall back to local file
    if os.path.exists('service-account.json'):
        try:
            creds = Credentials.from_service_account_file('service-account.json', scopes=SCOPES)
            return gspread.authorize(creds)
        except Exception as e:
            st.error(f"❌ Error loading local credentials: {e}")
            st.stop()

    st.error("❌ No credentials found!")
    st.stop()

def get_worksheet():
    """Get the Scores worksheet"""
    try:
        client = setup_sheets_client()
        spreadsheet_id = os.environ.get("SPREADSHEET_ID") or st.secrets.get("SPREADSHEET_ID")

        if not spreadsheet_id:
            st.error("❌ SPREADSHEET_ID not found in environment or secrets")
            st.stop()

        sheet = client.open_by_key(spreadsheet_id)
        return sheet.worksheet('Scores')
    except Exception as e:
        st.error(f"❌ Error connecting to spreadsheet: {e}")
        st.stop()

def add_score_entry(responses):
    """Add score entry to Google Sheets"""
    try:
        worksheet = get_worksheet()
        date = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        row = [
            date,
            RESPONSE_SCORES.get(responses['risk_taking'], 0),
            RESPONSE_SCORES.get(responses['team_dependence'], 0),
            RESPONSE_SCORES.get(responses['goals_understanding'], 0),
            RESPONSE_SCORES.get(responses['work_meaning'], 0),
            RESPONSE_SCORES.get(responses['work_impact'], 0),
            RESPONSE_SCORES.get(responses['motivation'], 0),
            RESPONSE_SCORES.get(responses['product_direction'], 0),
            MANAGER_SCORES.get(responses['manager_approach'], 0),
            RESPONSE_SCORES.get(responses['recommend'], 0),
            responses['team']
        ]
        worksheet.append_row(row)
        return True
    except Exception as e:
        st.error(f"Error saving to sheet: {e}")
        return False

def initialize_headers():
    """Initialize sheet headers if needed"""
    try:
        worksheet = get_worksheet()
        if worksheet.cell(1, 1).value != 'Date':
            headers = [
                'Date',
                'Risk Taking (1-5)',
                'Team Dependence (1-5)',
                'Goals Understanding (1-5)',
                'Work Meaning (1-5)',
                'Work Impact (1-5)',
                'Motivation (1-5)',
                'Product Direction (1-5)',
                'Manager Approach (1-5)',
                'Recommend (1-5)',
                'Team'
            ]
            worksheet.insert_row(headers, 1)
            st.info("✓ Headers initialized")
    except Exception as e:
        st.warning(f"Could not initialize headers: {e}")

initialize_headers()

# UI
st.title("🏥 Booking Guild Team Health Check")

col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.markdown("Please rate your experience across these dimensions. All responses are confidential.")
with col2:
    st.page_link("pages/analytics.py", label="📊 View Analytics", icon="📊")

with st.form("healthcheck_form"):
    
    st.markdown("### Your Team")
    
    team = st.radio(
        "Are you part of:",
        options=TEAM_OPTIONS,
        label_visibility="collapsed",
        key="q_team"
    )
    
    st.divider()
    
    st.markdown("### Your Responses")
    st.markdown("*Rate each statement from Strongly disagree to Strongly agree*")
    
    st.divider()
    
    st.markdown("**1. I feel I can take risks and make mistakes.**")
    risk_taking = st.radio(
        "Risk Taking",
        options=["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"],
        label_visibility="collapsed",
        key="q1"
    )
    
    st.divider()
    
    st.markdown("**2. I can depend upon my team members.**")
    team_dependence = st.radio(
        "Team Dependence",
        options=["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"],
        label_visibility="collapsed",
        key="q2"
    )
    
    st.divider()
    
    st.markdown("**3. I understand the goals of the company, the team, and how my role helps achieve them.**")
    goals_understanding = st.radio(
        "Goals Understanding",
        options=["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"],
        label_visibility="collapsed",
        key="q3"
    )
    
    st.divider()
    
    st.markdown("**4. I find meaning in the work I do.**")
    work_meaning = st.radio(
        "Work Meaning",
        options=["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"],
        label_visibility="collapsed",
        key="q4"
    )
    
    st.divider()
    
    st.markdown("**5. I believe the work I'm doing makes an impact to the company.**")
    work_impact = st.radio(
        "Work Impact",
        options=["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"],
        label_visibility="collapsed",
        key="q5"
    )
    
    st.divider()
    
    st.markdown("**6. I'm motivated.**")
    motivation = st.radio(
        "Motivation",
        options=["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"],
        label_visibility="collapsed",
        key="q6"
    )
    
    st.divider()
    
    st.markdown("**7. I'm getting the product direction I need.**")
    product_direction = st.radio(
        "Product Direction",
        options=["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"],
        label_visibility="collapsed",
        key="q7"
    )
    
    st.divider()
    
    st.markdown("**8. I find my engineering manager's approach to be:**")
    manager_approach = st.radio(
        "Manager Approach",
        options=["Too directive", "Just right", "Too hands off"],
        label_visibility="collapsed",
        key="q8"
    )
    
    st.divider()
    
    st.markdown("**9. I'd recommend working in the Bookings Guild to my network**")
    recommend = st.radio(
        "Recommend",
        options=["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"],
        label_visibility="collapsed",
        key="q9"
    )
    
    st.divider()
    
    submitted = st.form_submit_button("✅ Submit Health Check", use_container_width=True)
    
    if submitted:
        responses = {
            'risk_taking': risk_taking,
            'team_dependence': team_dependence,
            'goals_understanding': goals_understanding,
            'work_meaning': work_meaning,
            'work_impact': work_impact,
            'motivation': motivation,
            'product_direction': product_direction,
            'manager_approach': manager_approach,
            'recommend': recommend,
            'team': team
        }
        
        if add_score_entry(responses):
            st.session_state.submitted = True
            st.success("✅ Thank you! Your response has been recorded.", icon="✅")
            st.balloons()
        else:
            st.error("Failed to submit. Please try again.")

st.divider()
st.subheader("📊 Session Summary")

try:
    worksheet = get_worksheet()
    all_data = worksheet.get_all_values()

    if len(all_data) > 1:
        today = datetime.now().strftime('%Y-%m-%d')
        today_entries = [row for row in all_data[1:] if row[0].startswith(today)]

        if today_entries:
            st.info(f"✓ {len(today_entries)} team members have submitted today")

            # Calculate and display average scores
            try:
                categories = {
                    '💬 Risk Taking': 1,
                    '🤝 Team Dependence': 2,
                    '🎯 Goals Understanding': 3,
                    '✨ Work Meaning': 4,
                    '📊 Work Impact': 5,
                    '⚡ Motivation': 6,
                    '🧭 Product Direction': 7,
                    '❤️ Recommend': 9
                }
                
                avg_scores = {}
                for label, col_index in categories.items():
                    scores = [float(row[col_index]) for row in today_entries if col_index < len(row) and row[col_index]]
                    if scores:
                        avg_scores[label] = sum(scores) / len(scores)

                # Display in 2 columns
                cols = st.columns(2)
                for idx, (label, score) in enumerate(avg_scores.items()):
                    with cols[idx % 2]:
                        st.metric(label, f"{score:.1f}/5")
                
                # Team breakdown
                st.markdown("**Team Breakdown:**")
                team_counts = {}
                for row in today_entries:
                    team = row[-1] if row[-1] else "Unknown"
                    team_counts[team] = team_counts.get(team, 0) + 1
                
                for team, count in team_counts.items():
                    st.write(f"- {team}: {count} submission(s)")
                    
            except Exception as avg_error:
                st.warning(f"Could not calculate averages: {avg_error}")
        else:
            st.info("No submissions today yet. Be the first to share your feedback!")
    else:
        st.info("Sheet is empty. Be the first to submit!")
except Exception as e:
    st.warning(f"Could not load summary: {e}")