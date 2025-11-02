import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json

# Page config
st.set_page_config(page_title="Team Healthcheck", layout="centered")

# Initialize session state
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

@st.cache_resource
def setup_sheets_client():
    """Initialize Google Sheets client"""
    try:
        # Try reading from secrets (Streamlit Cloud)
        if "service_account_info" in st.secrets:
            creds = Credentials.from_service_account_info(st.secrets["service_account_info"], scopes=SCOPES)
        else:
            # Fall back to local file
            creds = Credentials.from_service_account_file('service-account.json', scopes=SCOPES)
    except Exception as e:
        st.error(f"Failed to load credentials: {e}")
        raise
    return gspread.authorize(creds)

def get_worksheet():
    """Get the Scores worksheet"""
    client = setup_sheets_client()
    spreadsheet_id = st.secrets.get("SPREADSHEET_ID")
    if not spreadsheet_id:
        st.error("SPREADSHEET_ID not found in secrets")
        st.stop()
    sheet = client.open_by_key(spreadsheet_id)
    return sheet.worksheet('Scores')

def add_score_entry(team_member, scores):
    """Add score entry to Google Sheets"""
    try:
        worksheet = get_worksheet()
        date = datetime.now().strftime('%Y-%m-%d %H:%M')
        row = [
            date,
            team_member,
            scores['communication'],
            scores['collaboration'],
            scores['progress'],
            scores['morale'],
            scores['overall']
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
        if worksheet.cell(1, 1).value is None:
            headers = ['Date', 'Team Member', 'Communication', 'Collaboration', 'Progress', 'Morale', 'Overall']
            worksheet.insert_row(headers, 1)
    except Exception as e:
        st.warning(f"Could not initialize headers: {e}")

# UI
st.title("🏥 Team Healthcheck Meeting")
st.markdown("Please rate how you're feeling across these dimensions (1-5 scale)")

with st.form("healthcheck_form"):
    # Team member name
    team_member = st.text_input(
        "Your Name",
        placeholder="Enter your name",
        help="Your name will be recorded with your scores"
    )

    st.divider()

    # Score inputs
    col1, col2 = st.columns(2)

    with col1:
        communication = st.slider(
            "Communication 💬",
            min_value=1,
            max_value=5,
            value=3,
            help="How well are we communicating as a team?"
        )
        collaboration = st.slider(
            "Collaboration 🤝",
            min_value=1,
            max_value=5,
            value=3,
            help="How well are we working together?"
        )
        progress = st.slider(
            "Progress 📈",
            min_value=1,
            max_value=5,
            value=3,
            help="How much progress are we making?"
        )

    with col2:
        morale = st.slider(
            "Morale 😊",
            min_value=1,
            max_value=5,
            value=3,
            help="How is team morale?"
        )
        overall = st.slider(
            "Overall Health ❤️",
            min_value=1,
            max_value=5,
            value=3,
            help="Overall team health assessment"
        )

    st.divider()

    submitted = st.form_submit_button("Submit Healthcheck", use_container_width=True)

    if submitted:
        if not team_member:
            st.error("Please enter your name")
        else:
            scores = {
                'communication': communication,
                'collaboration': collaboration,
                'progress': progress,
                'morale': morale,
                'overall': overall
            }

            if add_score_entry(team_member, scores):
                st.session_state.submitted = True
                st.success(f"✅ Thank you {team_member}! Your scores have been recorded.", icon="✅")
                st.balloons()
            else:
                st.error("Failed to submit. Please try again.")

# Display current session summary (optional)
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

            # Show average scores
            try:
                avg_scores = {
                    'Communication': sum(float(row[2]) for row in today_entries if row[2]) / len(today_entries),
                    'Collaboration': sum(float(row[3]) for row in today_entries if row[3]) / len(today_entries),
                    'Progress': sum(float(row[4]) for row in today_entries if row[4]) / len(today_entries),
                    'Morale': sum(float(row[5]) for row in today_entries if row[5]) / len(today_entries),
                    'Overall': sum(float(row[6]) for row in today_entries if row[6]) / len(today_entries),
                }

                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("💬 Avg Communication", f"{avg_scores['Communication']:.1f}/5")
                with col2:
                    st.metric("🤝 Avg Collaboration", f"{avg_scores['Collaboration']:.1f}/5")
                with col3:
                    st.metric("📈 Avg Progress", f"{avg_scores['Progress']:.1f}/5")
                with col4:
                    st.metric("😊 Avg Morale", f"{avg_scores['Morale']:.1f}/5")
                with col5:
                    st.metric("❤️ Avg Overall", f"{avg_scores['Overall']:.1f}/5")
            except:
                pass
        else:
            st.info("No submissions today yet")
except Exception as e:
    st.warning(f"Could not load summary: {e}")