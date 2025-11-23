import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import os
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Analytics", layout="wide")

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

@st.cache_resource
def setup_sheets_client():
    """Initialize Google Sheets client"""
    creds = None

    if "service_account_info" in st.secrets:
        try:
            creds = Credentials.from_service_account_info(dict(st.secrets["service_account_info"]), scopes=SCOPES)
            return gspread.authorize(creds)
        except Exception as e:
            st.error(f"❌ Error loading credentials from secrets: {e}")
            st.stop()

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

# Page Header
st.title("📊 Team Health Analytics")
st.markdown("Visualize team health trends and insights")

try:
    worksheet = get_worksheet()
    all_data = worksheet.get_all_values()

    if len(all_data) > 1:
        # Parse data
        df = pd.DataFrame(all_data[1:], columns=all_data[0])
        df['Date'] = pd.to_datetime(df['Date'])
        
        numeric_cols = [
            'Risk Taking',
            'Team Dependen',
            'Goals Understan',
            'Work Meaning',
            'Work Impact',
            'Motivation',
            'Product Directio',
            'Manager Appro',
            'Recommend'
        ]
        
        numeric_cols = [col for col in numeric_cols if col in df.columns]
        
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        st.divider()
        st.subheader("📈 Key Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Submissions", len(df))
        
        with col2:
            st.metric("Unique Days", df['Date'].dt.date.nunique())
        
        with col3:
            if 'Teams' in df.columns:
                st.metric("Teams", df['Teams'].nunique())
        
        with col4:
            today = datetime.now().strftime('%Y-%m-%d')
            today_count = len(df[df['Date'].dt.strftime('%Y-%m-%d') == today])
            st.metric("Today's Submissions", today_count)
        
        st.divider()
        
        st.subheader("🔍 Filters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            date_range = st.date_input(
                "Select Date Range",
                value=(df['Date'].min().date(), df['Date'].max().date()),
                key="date_range"
            )
        
        with col2:
            if 'Teams' in df.columns:
                teams = st.multiselect(
                    "Select Teams",
                    options=df['Teams'].unique(),
                    default=df['Teams'].unique(),
                    key="teams"
                )
            else:
                teams = None
        
        filtered_df = df[
            (df['Date'].dt.date >= date_range[0]) & 
            (df['Date'].dt.date <= date_range[1])
        ]
        
        if teams and 'Teams' in df.columns:
            filtered_df = filtered_df[filtered_df['Teams'].isin(teams)]
        
        st.divider()
        
        if len(filtered_df) > 0 and len(numeric_cols) > 0:
            
            st.subheader("📉 Average Scores Over Time")
            
            daily_avg = filtered_df.groupby(filtered_df['Date'].dt.date)[numeric_cols].mean()
            
            fig_trend = go.Figure()
            for col in numeric_cols:
                fig_trend.add_trace(go.Scatter(
                    x=daily_avg.index,
                    y=daily_avg[col],
                    mode='lines+markers',
                    name=col,
                    hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Score: %{y:.2f}<extra></extra>'
                ))
            
            fig_trend.update_layout(
                height=400,
                hovermode='x unified',
                xaxis_title="Date",
                yaxis_title="Average Score (1-5)",
                template="plotly_white"
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)
            
            st.divider()
            
            st.subheader("📊 Current Average Scores")
            
            current_avg = filtered_df[numeric_cols].mean()
            
            fig_bar = go.Figure(data=[
                go.Bar(
                    x=current_avg.index,
                    y=current_avg.values,
                    marker_color=['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#00B4D8', '#00B4D8', '#90E0EF', '#00B4D8'],
                    text=current_avg.values.round(2),
                    textposition='auto',
                    hovertemplate='<b>%{x}</b><br>Average: %{y:.2f}/5<extra></extra>'
                )
            ])
            
            fig_bar.update_layout(
                height=400,
                showlegend=False,
                xaxis_title="Category",
                yaxis_title="Average Score",
                yaxis=dict(range=[0, 5]),
                template="plotly_white"
            )
            
            fig_bar.update_xaxes(tickangle=-45)
            
            st.plotly_chart(fig_bar, use_container_width=True)
            
            st.divider()
            
            if 'Teams' in df.columns and len(teams) > 1:
                st.subheader("🤝 Team Comparison")
                
                team_avg = filtered_df.groupby('Teams')[numeric_cols].mean()
                
                fig_team = go.Figure()
                for col in numeric_cols:
                    fig_team.add_trace(go.Bar(
                        name=col,
                        x=team_avg.index,
                        y=team_avg[col],
                        hovertemplate='<b>%{x}</b><br>%{fullData.name}: %{y:.2f}<extra></extra>'
                    ))
                
                fig_team.update_layout(
                    height=400,
                    barmode='group',
                    xaxis_title="Team",
                    yaxis_title="Average Score",
                    yaxis=dict(range=[0, 5]),
                    template="plotly_white"
                )
                
                st.plotly_chart(fig_team, use_container_width=True)
                
                st.divider()
            
            st.subheader("👔 Manager Approach Distribution")
            
            manager_approach_col = 'Manager Appro'
            if manager_approach_col in df.columns:
                approach_counts = filtered_df[manager_approach_col].value_counts().sort_index()
                approach_labels = {1: "Too directive", 3: "Just right", 5: "Too hands off"}
                
                fig_pie = go.Figure(data=[
                    go.Pie(
                        labels=[approach_labels.get(int(idx), f"Score {idx}") for idx in approach_counts.index],
                        values=approach_counts.values,
                        hovertemplate='<b>%{label}</b><br>Count: %{value}<extra></extra>'
                    )
                ])
                
                fig_pie.update_layout(height=400)
                st.plotly_chart(fig_pie, use_container_width=True)
                
                st.divider()
            
            st.subheader("📋 Detailed Data")
            
            display_cols = ['Date'] + numeric_cols + (['Teams'] if 'Teams' in df.columns else [])
            display_df = filtered_df[display_cols].copy()
            display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d %H:%M')
            
            st.dataframe(
                display_df.sort_values('Date', ascending=False),
                use_container_width=True,
                height=400
            )
        
        else:
            st.warning("No data available for the selected filters")
    
    else:
        st.info("No data available yet. Submit responses to see analytics!")

except Exception as e:
    st.error(f"Error loading analytics: {e}")
    st.write(str(e))