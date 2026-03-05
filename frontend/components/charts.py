import streamlit as st
import plotly.express as px
import pandas as pd

def render_charts(df):
    """Render analytical charts for the campaign."""
    st.subheader("📈 Campaign Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 1. Status Distribution
        status_counts = df['status'].value_counts().reset_index()
        status_counts.columns = ['status', 'count']
        fig1 = px.pie(status_counts, values='count', names='status', title='Contact Status Distribution',
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig1, use_container_width=True)
        
    with col2:
        # 2. Activity Timeline
        if 'last_activity' in df.columns and not df.empty:
            df['date'] = pd.to_datetime(df['last_activity']).dt.date
            timeline = df.groupby('date').size().reset_index()
            timeline.columns = ['date', 'activities']
            fig2 = px.line(timeline, x='date', y='activities', title='System Activity Timeline')
            st.plotly_chart(fig2, use_container_width=True)
            
    # 3. Company Breakdown
    st.markdown("---")
    if not df.empty:
        company_counts = df['company'].value_counts().head(10).reset_index()
        company_counts.columns = ['company', 'count']
        fig3 = px.bar(company_counts, x='company', y='count', title='Top 10 Target Companies',
                     color='count', color_continuous_scale='Viridis')
        st.plotly_chart(fig3, use_container_width=True)
