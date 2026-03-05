import streamlit as st

def render_metrics(df):
    """Render high-level metrics for the campaign."""
    st.subheader("📊 Campaign Highlights")
    
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    
    total = len(df)
    pending = len(df[df['status'] == 'pending'])
    sent = len(df[df['status'] == 'sent'])
    followups = len(df[df['status'] == 'followup_sent'])
    replies = len(df[df['status'] == 'replied'])
    bounces = len(df[df['status'] == 'bounce'])
    no_response = len(df[df['status'] == 'no_response'])
    
    col1.metric("Total", total)
    col2.metric("Pending", pending)
    col3.metric("Sent", sent)
    col4.metric("Follow-ups", followups)
    col5.metric("Replies", replies)
    col6.metric("Bounces", bounces)
    col7.metric("No Response", no_response)
    
    # Campaign Health
    st.markdown("---")
    h1, h2, h3 = st.columns(3)
    
    sent_total = sent + followups + replies + no_response
    reply_rate = (replies / sent_total * 100) if sent_total > 0 else 0
    delivery_rate = ((sent_total - bounces) / sent_total * 100) if sent_total > 0 else 100
    progress = (sent_total / total * 100) if total > 0 else 0
    
    h1.write(f"**Reply Rate:** {reply_rate:.1f}%")
    h1.progress(reply_rate / 100)
    
    h2.write(f"**Delivery Rate:** {delivery_rate:.1f}%")
    h2.progress(delivery_rate / 100)
    
    h3.write(f"**Campaign Progress:** {progress:.1f}%")
    h3.progress(progress / 100)
