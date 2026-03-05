import streamlit as st

def render_contact_table(df):
    """Render a searchable and filterable contact table."""
    st.subheader("👥 Contacts")
    
    # Filters
    f1, f2 = st.columns([2, 1])
    with f1:
        search = st.text_input("Search contacts...", placeholder="Enter name, email, or company")
    with f2:
        filter_status = st.multiselect("Filter Status", 
                                     options=df['status'].unique() if not df.empty else [],
                                     default=df['status'].unique() if not df.empty else [])
    
    if df.empty:
        st.info("No contacts found.")
        return

    # Apply filters
    filtered_df = df[df['status'].isin(filter_status)]
    if search:
        search_mask = (
            filtered_df['name'].str.contains(search, case=False, na=False) |
            filtered_df['email'].str.contains(search, case=False, na=False) |
            filtered_df['company'].str.contains(search, case=False, na=False)
        )
        filtered_df = filtered_df[search_mask]
        
    st.dataframe(
        filtered_df[['name', 'email', 'company', 'status', 'first_email_date', 'followup_date', 'sender_account']],
        use_container_width=True,
        hide_index=True
    )
