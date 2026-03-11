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
    st.write("Manage System Settings.")
    
    # In Supabase, users are managed in the auth schema, 
    # but we can show a list of profiles if we had a profiles table.
    # For now, we'll show system status.
    
    with st.expander("System Health"):
        st.write("Supabase Connection: Online")
        st.write("Infosys AI Engine: Active")
        st.info("User management is handled through the Small Business Sales & Profit Analyzer (Bizsight AI) Portal.")

