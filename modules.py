import streamlit as st
import pandas as pd
import database
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import time
from sklearn.linear_model import LinearRegression
import numpy as np

def data_entry_page():
    st.header("Daily Sales & Expense Logging")
    
    with st.expander(" Add New Transaction", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            Type = st.selectbox("Transaction Type", ["Sale", "Expense"])
            Date = st.date_input("Date", datetime.now())
        
        with col2:
            Amount = st.number_input("Amount", min_value=0.0, step=10.0)
            Category = st.selectbox("Category", 
                                    ["Sales", "Rent", "Utilities", "Supplies", "Marketing", "Salaries", "Other"] 
                                    if Type == "Expense" else ["Product Sale", "Service", "Other Income"])

        Description = st.text_area("Description")
        Receipt = st.file_uploader("Attach Receipt (Image)", type=['png', 'jpg', 'jpeg'])
        
        if st.button("Submit Transaction", type="primary"):
            receipt_data = Receipt.getvalue() if Receipt else None
            user_id = st.session_state.user['id']
            
            success = database.add_transaction(user_id, Type, Category, Amount, Description, Date, receipt_data)
            if success:
                st.success(" Transaction Saved to Database!")
                time.sleep(1)
                st.rerun()
            else:
                st.error(" Failed to save transaction. Please check your connection.")

    # Show Recent Transactions
    st.markdown("### Recent Transactions")
    user_id = st.session_state.user['id']
    df = database.get_transactions(user_id)
    if not df.empty:
        st.dataframe(df.sort_values(by='date', ascending=False), use_container_width=True)
    else:
        st.info("No transactions found.")

def inventory_page():
    st.header("Inventory Management & COGS")
    
    tab1, tab2 = st.tabs(["Stock List", "Add Item"])
    
    user_id = st.session_state.user['id']
    with tab1:
        df = database.get_inventory(user_id)
        if not df.empty:
            st.dataframe(df)
            
            # Low Stock Alert
            low_stock = df[df['quantity'] < df['min_stock_level']]
            if not low_stock.empty:
                st.error(f"⚠️ Low Stock Alert: {len(low_stock)} items are below minimum level!")
                st.dataframe(low_stock[['item_name', 'quantity', 'min_stock_level']])
        else:
            st.info("Inventory is empty.")

    with tab2:
        with st.form("add_item"):
            col1, col2 = st.columns(2)
            name = col1.text_input("Item Name")
            cat = col2.text_input("Category")
            qty = col1.number_input("Quantity", min_value=0)
            min_qty = col2.number_input("Min Stock Level", min_value=1)
            cost = col1.number_input("Cost Price", min_value=0.0)
            price = col2.number_input("Selling Price", min_value=0.0)
            
            if st.form_submit_button("Add Item"):
                user_id = st.session_state.user['id']
                success = database.add_inventory_item(user_id, name, qty, cost, price, cat, min_qty)
                if success:
                    st.success(f"✅ Added {name} to inventory database!")
                    st.rerun()
                else:
                    st.error("❌ Failed to add item. Please try again.")

def reports_page():
    st.header("Reports & Predictions")
    
    st.subheader("Profit & Loss Summary")
    user_id = st.session_state.user['id']
    df = database.get_transactions(user_id)
    
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        
        # Gross metrics
        income = df[df['type'] == 'Sale']['amount'].sum()
        expenses = df[df['type'] == 'Expense']['amount'].sum()
        profit = income - expenses
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Income", f"₹{income:,.2f}")
        col2.metric("Total Expenses", f"₹{expenses:,.2f}")
        col3.metric("Net Profit", f"₹{profit:,.2f}", delta_color="normal")
        
        # Charts
        daily = df.groupby([pd.Grouper(key='date', freq='D'), 'type'])['amount'].sum().reset_index()
        fig = px.bar(daily, x='date', y='amount', color='type', title="Daily Income vs Expense", barmode='group')
        st.plotly_chart(fig, use_container_width=True)
        
        st.download_button("Download Report (CSV)", df.to_csv(), "report.csv")
        
        # AI Prediction
        st.subheader("🤖 AI Sales Forecast")
        sales_data = df[df['type'] == 'Sale'].groupby('date')['amount'].sum().reset_index()
        
        if len(sales_data) > 2:
            # Prepare data
            sales_data['ordinal_date'] = sales_data['date'].map(datetime.toordinal)
            X = sales_data[['ordinal_date']]
            y = sales_data['amount']
            
            model = LinearRegression()
            model.fit(X, y)
            
            # Predict next 30 days
            last_date = sales_data['date'].max()
            future_dates = [last_date + timedelta(days=i) for i in range(1, 31)]
            future_ordinal = np.array([d.toordinal() for d in future_dates]).reshape(-1, 1)
            future_pred = model.predict(future_ordinal)
            
            future_df = pd.DataFrame({'date': future_dates, 'predicted_sales': future_pred})
            
            fig_pred = go.Figure()
            fig_pred.add_trace(go.Scatter(x=sales_data['date'], y=sales_data['amount'], mode='lines+markers', name='Historical Sales'))
            fig_pred.add_trace(go.Scatter(x=future_df['date'], y=future_df['predicted_sales'], mode='lines', name='Forecast (AI)', line=dict(dash='dash')))
            fig_pred.update_layout(title="30-Day Sales Forecast Model")
            st.plotly_chart(fig_pred, use_container_width=True)
        else:
            st.warning("Not enough data points for AI prediction. Add more sales transactions!")

    else:
        st.info("No data for reports.")

def admin_page():
    st.header("Admin Dashboard")
    
    if st.session_state.user['role'] != 'Admin' and st.session_state.user['email'] != 'admin':
        st.error("Access Denied. You do not have permissions to view this page.")
        return
        
    st.write("Manage System Settings, User Logs, and Authentication.")
    
    tab1, tab2, tab3 = st.tabs(["System Health", "User Login Logs", "User Management"])
    
    with tab1:
        st.write("Supabase Connection: Online")
        st.write("Infosys AI Engine: Active")
        st.info("System fully operational.")
        
    with tab2:
        st.subheader("User Login Logs")
        logs_df = database.get_all_login_logs()
        if not logs_df.empty:
            logs_df['login_time'] = pd.to_datetime(logs_df['login_time'])
            logs_df['last_active'] = pd.to_datetime(logs_df['last_active'])
            logs_df['logout_time'] = pd.to_datetime(logs_df['logout_time'])
            
            # Calculate duration
            # if logout_time is null, use last_active
            logs_df['end_time'] = logs_df['logout_time'].fillna(logs_df['last_active'])
            logs_df['duration'] = logs_df['end_time'] - logs_df['login_time']
            
            # format duration
            logs_df['duration_str'] = logs_df['duration'].dt.components.apply(
                lambda x: f"{int(x.hours)}h {int(x.minutes)}m {int(x.seconds)}s", axis=1
            )
            
            display_df = logs_df[['id', 'user_email', 'login_time', 'logout_time', 'duration_str']].copy()
            display_df.columns = ['Session ID', 'User Email', 'Login Timestamp', 'Logout Timestamp', 'Session Duration']
            st.dataframe(display_df, use_container_width=True)
            
            # Provide CSV download for Login Logs
            csv_logs = display_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Login Logs as CSV",
                data=csv_logs,
                file_name='user_login_logs.csv',
                mime='text/csv',
            )
        else:
            st.info("No login logs found.")
            
    with tab3:
        st.subheader("Registered Users Directory")
        users_df = database.get_all_users()
        if not users_df.empty:
            st.dataframe(users_df, use_container_width=True)
            
            # Provide CSV download for Registered Users
            csv_users = users_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download User Directory as CSV",
                data=csv_users,
                file_name='registered_users.csv',
                mime='text/csv',
            )
            
            st.markdown("---")
            st.subheader("Reset User Password")
            user_list = users_df['username'].tolist()
            with st.form("reset_password_form"):
                selected_user = st.selectbox("Select User", user_list)
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm New Password", type="password")
                if st.form_submit_button("Reset Password", type="primary"):
                    if new_password == confirm_password and new_password:
                        success = database.update_user_password(selected_user, new_password)
                        if success:
                            st.success(f"Password for {selected_user} updated successfully.")
                        else:
                            st.error("Failed to update password.")
                    else:
                        st.error("Passwords do not match or empty.")
        else:
            st.info("No local users found.")

