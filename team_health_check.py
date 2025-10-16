import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Team Health Check",
    page_icon="📊",
    layout="wide"
)

# Health areas configuration
HEALTH_AREAS = [
    {
        'id': 'release',
        'name': 'Easy to Release',
        'question': 'Is releasing risky and painful or simple and safe?',
        'low': 'Risky & painful',
        'high': 'Simple & safe'
    },
    {
        'id': 'process',
        'name': 'Suitable Process',
        'question': 'Do the ways of working suck or fit the team perfectly?',
        'low': 'Ways of working suck',
        'high': 'Fit perfectly'
    },
    {
        'id': 'tech',
        'name': 'Tech Quality',
        'question': 'Is technical debt raging or is the team proud of code quality?',
        'low': 'Debt out of control',
        'high': 'Proud of quality'
    },
    {
        'id': 'value',
        'name': 'Value',
        'question': 'Is your team proud of the value they deliver?',
        'low': 'Not proud',
        'high': 'Very proud'
    },
    {
        'id': 'speed',
        'name': 'Speed',
        'question': 'Is your team getting stuff done quickly or getting stuck?',
        'low': 'Getting stuck',
        'high': 'Moving quickly'
    },
    {
        'id': 'mission',
        'name': 'Mission',
        'question': 'Is the mission unclear and uninspiring or clear and motivating?',
        'low': 'Unclear & uninspiring',
        'high': 'Clear & motivating'
    },
    {
        'id': 'fun',
        'name': 'Fun',
        'question': 'Is your team bored or having great fun working together?',
        'low': 'Bored',
        'high': 'Great fun'
    },
    {
        'id': 'learning',
        'name': 'Learning',
        'question': 'Does your team have time to learn?',
        'low': 'No time',
        'high': 'Plenty of time'
    },
    {
        'id': 'support',
        'name': 'Support',
        'question': 'Is your team getting support when they ask for it?',
        'low': 'No support',
        'high': 'Great support'
    },
    {
        'id': 'autonomy',
        'name': 'Pawns or Players',
        'question': 'Does your team feel like pawns or in control of their destiny?',
        'low': 'Pawns in chess',
        'high': 'Players in control'
    }
]

# Initialize session state
if 'ratings' not in st.session_state:
    st.session_state.ratings = {}
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'assessment'

def get_color(value):
    """Return color based on rating value"""
    if value <= 3:
        return '#ef4444'  # red
    elif value <= 6:
        return '#eab308'  # yellow
    else:
        return '#22c55e'  # green

def get_status_emoji(value):
    """Return emoji based on rating value"""
    if value <= 3:
        return '⚠️'
    elif value <= 6:
        return '📈'
    else:
        return '✅'

def calculate_average():
    """Calculate average score"""
    if st.session_state.ratings:
        return round(sum(st.session_state.ratings.values()) / len(st.session_state.ratings), 1)
    return 0

def get_overall_health(avg_score):
    """Get overall health status"""
    if avg_score <= 3:
        return {'text': 'Needs Attention', 'emoji': '🚨', 'color': '#ef4444'}
    elif avg_score <= 6:
        return {'text': 'Making Progress', 'emoji': '📊', 'color': '#eab308'}
    else:
        return {'text': 'Healthy Team', 'emoji': '🎉', 'color': '#22c55e'}

def create_radar_chart():
    """Create radar chart for results"""
    categories = [area['name'] for area in HEALTH_AREAS]
    values = [st.session_state.ratings.get(area['id'], 0) for area in HEALTH_AREAS]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(99, 102, 241, 0.3)',
        line=dict(color='rgb(99, 102, 241)', width=2),
        name='Team Health'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )
        ),
        showlegend=False,
        height=500
    )
    
    return fig

def create_bar_chart():
    """Create horizontal bar chart for results"""
    areas = [area['name'] for area in HEALTH_AREAS]
    values = [st.session_state.ratings.get(area['id'], 0) for area in HEALTH_AREAS]
    colors = [get_color(v) for v in values]
    
    fig = go.Figure(go.Bar(
        x=values,
        y=areas,
        orientation='h',
        marker=dict(color=colors),
        text=values,
        textposition='inside',
        textfont=dict(size=14, color='white')
    ))
    
    fig.update_layout(
        xaxis=dict(range=[0, 10], title='Score'),
        yaxis=dict(title=''),
        height=600,
        margin=dict(l=150, r=50, t=50, b=50)
    )
    
    return fig

def show_assessment_page():
    """Display assessment page"""
    st.title("📊 Team Health Check")
    st.markdown("---")
    
    # Progress indicator
    completed = len(st.session_state.ratings)
    total = len(HEALTH_AREAS)
    progress = completed / total
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.progress(progress)
    with col2:
        st.write(f"**{completed}/{total} completed**")
    
    st.markdown("###")
    
    # Display each health area
    for area in HEALTH_AREAS:
        with st.expander(
            f"{'✅' if area['id'] in st.session_state.ratings else '⭕'} {area['name']}", 
            expanded=area['id'] not in st.session_state.ratings and completed < total
        ):
            st.markdown(f"**{area['question']}**")
            st.markdown(f"*{area['low']}* ← → *{area['high']}*")
            
            current_value = st.session_state.ratings.get(area['id'], 5)
            
            rating = st.slider(
                "Rate from 1 (low) to 10 (high)",
                min_value=1,
                max_value=10,
                value=current_value,
                key=f"slider_{area['id']}"
            )
            
            if st.button(f"Save Rating: {rating}/10", key=f"btn_{area['id']}"):
                st.session_state.ratings[area['id']] = rating
                st.success(f"Saved! {get_status_emoji(rating)}")
                st.rerun()
    
    st.markdown("---")
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if completed == total:
            if st.button("📈 View Results", type="primary", use_container_width=True):
                st.session_state.current_page = 'results'
                st.rerun()
        else:
            st.info(f"Complete all {total} areas to view results ({total - completed} remaining)")

def show_results_page():
    """Display results page"""
    st.title("📊 Team Health Check Results")
    
    avg_score = calculate_average()
    overall = get_overall_health(avg_score)
    
    # Overall health summary
    st.markdown("###")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Average Score", f"{avg_score}/10")
    with col2:
        st.metric("Overall Health", overall['text'])
    with col3:
        st.metric("Areas Assessed", len(st.session_state.ratings))
    
    st.markdown("---")
    
    # Visualizations
    tab1, tab2, tab3 = st.tabs(["📊 Bar Chart", "🎯 Radar Chart", "📋 Details"])
    
    with tab1:
        st.plotly_chart(create_bar_chart(), use_container_width=True)
    
    with tab2:
        st.plotly_chart(create_radar_chart(), use_container_width=True)
    
    with tab3:
        st.markdown("### Detailed Scores")
        for area in HEALTH_AREAS:
            if area['id'] in st.session_state.ratings:
                score = st.session_state.ratings[area['id']]
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**{area['name']}**")
                    st.caption(area['question'])
                with col2:
                    st.write(f"{get_status_emoji(score)}")
                with col3:
                    st.write(f"**{score}/10**")
                
                st.progress(score / 10)
                st.markdown("---")
    
    # Next steps
    st.markdown("### 💡 Next Steps")
    st.info("""
    - Share these results with your team to start a conversation
    - Focus on the lowest-scoring areas first
    - Create action items to address specific concerns
    - Schedule regular check-ins to track improvements
    """)
    
    # Export and reset buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Create export data
        export_data = pd.DataFrame([
            {
                'Area': area['name'],
                'Score': st.session_state.ratings.get(area['id'], 0),
                'Question': area['question']
            }
            for area in HEALTH_AREAS
        ])
        
        csv = export_data.to_csv(index=False)
        st.download_button(
            "📥 Export CSV",
            csv,
            f"team_health_check_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv",
            use_container_width=True
        )
    
    with col2:
        if st.button("🔄 New Assessment", use_container_width=True):
            st.session_state.ratings = {}
            st.session_state.current_page = 'assessment'
            st.rerun()
    
    with col3:
        if st.button("✏️ Edit Ratings", use_container_width=True):
            st.session_state.current_page = 'assessment'
            st.rerun()

# Main app logic
def main():
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50/6366f1/ffffff?text=Team+Health", use_container_width=True)
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This Team Health Check helps assess your team across 10 key areas.
        
        Rate each area from 1-10 to get insights into your team's current state.
        """)
        st.markdown("---")
        st.markdown("### Tips")
        st.markdown("""
        - Be honest in your assessments
        - Consider recent trends, not just current state
        - Discuss results openly with your team
        - Focus on improvement, not blame
        """)
    
    # Show appropriate page
    if st.session_state.current_page == 'assessment':
        show_assessment_page()
    else:
        show_results_page()

if __name__ == "__main__":
    main()