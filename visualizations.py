import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def show_advanced_visualizations(df):
    st.markdown("---")
    st.header("🚀 Advanced Analytics")
    
    # Check required columns or generate synthetic for demo
    if 'date' not in df.columns:
        # Generate synthetic dates for the dataframe if missing
        dates = pd.date_range(end=datetime.now(), periods=len(df), freq='H')
        df['date'] = dates
    
    # 5 New Tabs for 30 Visualizations
    tabs = st.tabs([
        "📈 Sales & Trends", 
        "📦 Product & Inventory", 
        "👥 Customer Insights", 
        "⚙️ Operations", 
        "💹 Financial Health"
    ])
    
    # --- TAB 1: SALES & TRENDS (6 Charts) ---
    with tabs[0]:
        st.subheader("Granular Sales Analysis")
        col1, col2 = st.columns(2)
        
        # 1. Hourly Sales Heatmap
        with col1:
            df['hour'] = df['date'].dt.hour
            df['day_name'] = df['date'].dt.day_name()
            hourly_sales = df.groupby(['day_name', 'hour'])['amount'].sum().reset_index() if 'amount' in df.columns else df.groupby(['day_name', 'hour'])['monthly_sales'].mean().reset_index()
            val_col = 'amount' if 'amount' in df.columns else 'monthly_sales'
            
            fig = px.density_heatmap(hourly_sales, x='hour', y='day_name', z=val_col, 
                                     title="1. Hourly Sales Intensity Heatmap",
                                     color_continuous_scale="Viridis")
            st.plotly_chart(fig, use_container_width=True)

        # 2. Sales Velocity (Rate of Change)
        with col2:
            sales_trend = df.groupby(df['date'].dt.date)[val_col].sum().reset_index()
            sales_trend['velocity'] = sales_trend[val_col].pct_change().fillna(0)
            fig = px.bar(sales_trend, x='date', y='velocity', 
                         title="2. Daily Sales Velocity (Growth Rate)",
                         color='velocity', color_continuous_scale="RdBu")
            st.plotly_chart(fig, use_container_width=True)

        # 3. Weekend vs Weekday Performance
        col3, col4 = st.columns(2)
        with col3:
            df['is_weekend'] = df['date'].dt.dayofweek >= 5
            weekend_perf = df.groupby('is_weekend')[val_col].mean().reset_index()
            weekend_perf['Type'] = weekend_perf['is_weekend'].map({True: 'Weekend', False: 'Weekday'})
            fig = px.pie(weekend_perf, values=val_col, names='Type', title="3. Weekday vs Weekend Revenue Share", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

        # 4. Sales Deviation from Moving Average
        with col4:
            sales_trend['SMA_7'] = sales_trend[val_col].rolling(window=7).mean()
            sales_trend['Deviation'] = sales_trend[val_col] - sales_trend['SMA_7']
            fig = px.area(sales_trend, x='date', y='Deviation', title="4. Sales Deviation from 7-Day Moving Avg")
            st.plotly_chart(fig, use_container_width=True)

        # 5. Forecast vs Actual (Simulated)
        col5, col6 = st.columns(2)
        with col5:
            # Simulate forecast
            sales_trend['Forecast'] = sales_trend[val_col].shift(1) * 1.02
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=sales_trend['date'], y=sales_trend[val_col], name='Actual'))
            fig.add_trace(go.Scatter(x=sales_trend['date'], y=sales_trend['Forecast'], name='Forecast', line=dict(dash='dash')))
            fig.update_layout(title="5. Actual vs Forecasted Sales")
            st.plotly_chart(fig, use_container_width=True)

        # 6. Cumulative Sales Growth
        with col6:
            sales_trend['Cumulative'] = sales_trend[val_col].cumsum()
            fig = px.line(sales_trend, x='date', y='Cumulative', title="6. Cumulative Revenue Trajectory")
            st.plotly_chart(fig, use_container_width=True)

    # --- TAB 2: PRODUCT & INVENTORY (6 Charts) ---
    with tabs[1]:
        st.subheader("Product Performance & Stock Analysis")
        col1, col2 = st.columns(2)
        
        # 7. Pareto Analysis (80/20 Rule)
        with col1:
            # Simulate product data if specific columns missing
            if 'category' not in df.columns:
                categories = ['Electronics', 'Clothing', 'Home', 'Beauty', 'Sports']
                df['category'] = np.random.choice(categories, len(df))
            
            cat_sales = df.groupby('category')[val_col].sum().sort_values(ascending=False).reset_index()
            cat_sales['cumulative_pct'] = cat_sales[val_col].cumsum() / cat_sales[val_col].sum()
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Bar(x=cat_sales['category'], y=cat_sales[val_col], name='Sales'), secondary_y=False)
            fig.add_trace(go.Scatter(x=cat_sales['category'], y=cat_sales['cumulative_pct'], name='Cumulative %', mode='lines+markers'), secondary_y=True)
            fig.update_layout(title="7. Pareto Analysis by Category")
            st.plotly_chart(fig, use_container_width=True)

        # 8. Stock Turn Rate (Simulated)
        with col2:
            cats = df['category'].unique()
            turnover = np.random.uniform(2, 12, len(cats))
            fig = px.bar(x=cats, y=turnover, title="8. Inventory Turnover Ratio by Category", color=turnover)
            st.plotly_chart(fig, use_container_width=True)

        # 9. Stockout Risk Heatmap
        col3, col4 = st.columns(2)
        with col3:
            # Simulated stock levels
            stock_levels = np.random.randint(0, 100, (5, 7)) # 5 categories, 7 locations/days
            fig = px.imshow(stock_levels, title="9. Stockout Risk Intensity", labels=dict(x="Warehouse/Day", y="Category"))
            st.plotly_chart(fig, use_container_width=True)

        # 10. Return Rate Analysis
        with col4:
            return_rates = np.random.uniform(0.01, 0.15, len(cats))
            fig = px.bar(x=cats, y=return_rates, title="10. Product Return Rates", color=return_rates, color_continuous_scale="Reds")
            st.plotly_chart(fig, use_container_width=True)

        # 11. Shelf Velocity
        col5, col6 = st.columns(2)
        with col5:
            velocity = np.random.uniform(10, 100, len(cats))
            fig = px.funnel(x=velocity, y=cats, title="11. Product Movement Velocity")
            st.plotly_chart(fig, use_container_width=True)

        # 12. Aging Inventory
        with col6:
            age_bins = ['0-30 days', '31-60 days', '61-90 days', '90+ days']
            values = np.random.randint(1000, 50000, 4)
            fig = px.pie(values=values, names=age_bins, title="12. Aging Inventory Distribution")
            st.plotly_chart(fig, use_container_width=True)

    # --- TAB 3: CUSTOMER INSIGHTS (6 Charts) ---
    with tabs[2]:
        st.subheader("Customer Behavior Analytics")
        col1, col2 = st.columns(2)
        
        # 13. Customer Segmentation (RFM Simulated)
        with col1:
            segments = ['Champions', 'Loyal', 'At Risk', 'Lost']
            counts = [15, 35, 30, 20]
            fig = px.bar(x=segments, y=counts, title="13. Customer Segmentation (RFM Model)", color=segments)
            st.plotly_chart(fig, use_container_width=True)
            
        # 14. Customer Lifetime Value (CLV) Dist
        with col2:
            clv_data = np.random.lognormal(mean=6, sigma=1, size=1000)
            fig = px.histogram(clv_data, title="14. Customer Lifetime Value Distribution", nbins=30)
            st.plotly_chart(fig, use_container_width=True)
            
        # 15. Acquisition Channel Performance
        col3, col4 = st.columns(2)
        with col3:
            channels = ['Organic', 'Paid Ads', 'Social', 'Email', 'Referral']
            roi = [4.5, 2.1, 3.8, 5.2, 3.0]
            fig = px.scatter(x=channels, y=roi, size=[30, 50, 40, 35, 25], title="15. Marketing Channel ROI Bubble Chart")
            st.plotly_chart(fig, use_container_width=True)
            
        # 16. Churn Rate Trend
        with col4:
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            churn = [5.2, 4.8, 4.5, 4.2, 4.0, 3.8] # Improving trend
            fig = px.line(x=months, y=churn, title="16. Monthly Churn Rate Trend (%)", markers=True)
            st.plotly_chart(fig, use_container_width=True)

        # 17. Sentiment Analysis
        col5, col6 = st.columns(2)
        with col5:
            sentiments = ['Positive', 'Neutral', 'Negative']
            pct = [65, 25, 10]
            fig = px.pie(values=pct, names=sentiments, title="17. Customer Sentiment Analysis", hole=0.6)
            st.plotly_chart(fig, use_container_width=True)

        # 18. Purchase Time Distribution
        with col6:
            hours = list(range(24))
            purchase_freq = np.random.poisson(20, 24)
            fig = px.line(x=hours, y=purchase_freq, title="18. Peak Purchase Time Breakdown")
            st.plotly_chart(fig, use_container_width=True)

    # --- TAB 4: OPERATIONS (6 Charts) ---
    with tabs[3]:
        st.subheader("Operational Efficiency Metrics")
        col1, col2 = st.columns(2)
        
        # 19. Order Processing Time
        with col1:
            process_times = np.random.normal(24, 6, 100)
            fig = px.box(y=process_times, title="19. Order Processing Time (Hours)")
            st.plotly_chart(fig, use_container_width=True)

        # 20. Staff Productivity
        with col2:
            staff = [f'Staff {i}' for i in range(1, 11)]
            tasks = np.random.randint(50, 150, 10)
            fig = px.bar(x=staff, y=tasks, title="20. Tasks Completed by Staff Member", color=tasks)
            st.plotly_chart(fig, use_container_width=True)

        # 21. Utility Usage
        col3, col4 = st.columns(2)
        with col3:
            utils = ['Electricity', 'Water', 'Internet', 'Maintenance']
            cost = [5000, 1200, 2000, 3500]
            fig = px.bar(x=utils, y=cost, title="21. Monthly Utility Consumption Cost")
            st.plotly_chart(fig, use_container_width=True)

        # 22. Delivery Success Rate
        with col4:
            status = ['Delivered Ontime', 'Late', 'Failed']
            counts = [85, 12, 3]
            fig = px.pie(values=counts, names=status, title="22. Last Mile Delivery Performance")
            st.plotly_chart(fig, use_container_width=True)
            
        # 23. Asset Utilization
        col5, col6 = st.columns(2)
        with col5:
            asset = ['Vehicles', 'Computers', 'Machinery', 'Space']
            util = [75, 90, 60, 85]
            # fig = px.radial_bar(r=util, theta=asset, title="23. Asset Utilization (%)") # Removed invalid call
            fig = go.Figure(go.Scatterpolar(r=util, theta=asset, fill='toself'))
            fig.update_layout(title="23. Asset Utilization Radar")
            st.plotly_chart(fig, use_container_width=True)
            
        # 24. Incident Reports
        with col6:
            types = ['Safety', 'Security', 'IT Issues', 'Logistics']
            incidents = [2, 1, 15, 8]
            fig = px.bar(x=types, y=incidents, title="24. Operational Incidents by Category", color=types)
            st.plotly_chart(fig, use_container_width=True)

    # --- TAB 5: FINANCIAL HEALTH (6 Charts) ---
    with tabs[4]:
        st.subheader("Advanced Financial Metrics")
        col1, col2 = st.columns(2)
        
        # 25. Break-Even Analysis
        with col1:
            units = np.linspace(0, 1000, 100)
            fixed_cost = 50000
            variable_cost = 20 * units
            revenue = 80 * units
            total_cost = fixed_cost + variable_cost
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=units, y=revenue, name='Revenue'))
            fig.add_trace(go.Scatter(x=units, y=total_cost, name='Total Cost'))
            fig.update_layout(title="25. Break-Even Point Analysis")
            st.plotly_chart(fig, use_container_width=True)

        # 26. Cash Flow Forecast
        with col2:
            months_f = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            cash_in = np.random.randint(100000, 150000, 6)
            cash_out = np.random.randint(80000, 120000, 6)
            net = cash_in - cash_out
            
            fig = go.Figure(data=[
                go.Bar(name='Cash In', x=months_f, y=cash_in),
                go.Bar(name='Cash Out', x=months_f, y=cash_out),
                go.Scatter(name='Net Flow', x=months_f, y=net, mode='lines+markers', line=dict(color='black'))
            ])
            fig.update_layout(title="26. Cash Flow Forecast (H2)", barmode='group')
            st.plotly_chart(fig, use_container_width=True)

        # 27. Expense Composition
        col3, col4 = st.columns(2)
        with col3:
            expenses = ['Rent', 'Salaries', 'Marketing', 'COGS', 'Misc']
            vals = [25, 35, 15, 20, 5]
            fig = px.treemap(names=expenses, parents=['Expenses']*5, values=vals, title="27. Expense Structure Treemap")
            st.plotly_chart(fig, use_container_width=True)

        # 28. Revenue per Employee Trend
        with col4:
            years = [2020, 2021, 2022, 2023, 2024]
            rpe = [150000, 160000, 155000, 175000, 190000]
            fig = px.area(x=years, y=rpe, title="28. Revenue Per Employee Trend")
            st.plotly_chart(fig, use_container_width=True)
            
        # 29. Debt-to-Equity Forecast
        col5, col6 = st.columns(2)
        with col5:
            years_f = range(2025, 2030)
            ratio = [0.8, 0.75, 0.6, 0.5, 0.4] # Improving leverage
            fig = px.bar(x=years_f, y=ratio, title="29. Projected Debt-to-Equity Ratio")
            st.plotly_chart(fig, use_container_width=True)
            
        # 30. Profit Margin Sensitivity
        with col6:
            price_change = [-10, -5, 0, 5, 10] # % change in price
            margin_impact = [10, 15, 20, 26, 33] # resulting margin %
            fig = px.line(x=price_change, y=margin_impact, title="30. Profit Sensitivity to Price Changes", markers=True)
            fig.update_xaxes(title="% Price Change")
            fig.update_yaxes(title="Proj. Profit Margin %")
            st.plotly_chart(fig, use_container_width=True)


def show_geographic_and_premium_analytics(df):
    st.markdown("---")
    st.markdown("<h2 class='section-header'>🌍 Geographic & Premium Analytics (20+ New Charts)</h2>", unsafe_allow_html=True)
    
    # Ensure necessary columns exist or simulate them
    cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune', 'Ahmedabad']
    states = ['Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'West Bengal', 'Telangana', 'Maharashtra', 'Gujarat']

    if 'city' not in df.columns:
        df['city'] = np.random.choice(cities, len(df))
    if 'state' not in df.columns:
        # Simple mapping for simulation
        city_state_map = dict(zip(cities, states))
        df['state'] = df['city'].map(city_state_map)
    if 'lat' not in df.columns or 'lon' not in df.columns:
         # Approx coords
        coords = {
            'Mumbai': (19.0760, 72.8777), 'Delhi': (28.7041, 77.1025), 'Bangalore': (12.9716, 77.5946),
            'Chennai': (13.0827, 80.2707), 'Kolkata': (22.5726, 88.3639), 'Hyderabad': (17.3850, 78.4867),
            'Pune': (18.5204, 73.8567), 'Ahmedabad': (23.0225, 72.5714)
        }
        df['lat'] = df.apply(lambda row: coords.get(row['city'], (20.5937, 78.9629))[0] if pd.isna(row.get('lat')) else row['lat'], axis=1)
        df['lon'] = df.apply(lambda row: coords.get(row['city'], (20.5937, 78.9629))[1] if pd.isna(row.get('lon')) else row['lon'], axis=1)

    tabs = st.tabs([
        "🗺️ Geographic Intelligence",
        "💎 Premium Financials",
        "📊 Advanced Market Analysis",
        "🤖 AI & Predictive Insights"
    ])

    # --- TAB 1: GEOGRAPHIC INTELLIGENCE (5 Charts) ---
    with tabs[0]:
        col1, col2 = st.columns(2)
        
        # 1. Store Locations Map
        with col1:
            # Group by city and take the first lat/lon found for that city
            if 'monthly_sales' in df.columns:
                val_col = 'monthly_sales'
                agg_dict = {'monthly_sales': 'sum', 'lat': 'first', 'lon': 'first'}
            else:
                val_col = 'amount'
                agg_dict = {'amount': 'sum', 'lat': 'first', 'lon': 'first'}

            sales_by_city = df.groupby('city').agg(agg_dict).reset_index()
            
            fig = px.scatter_mapbox(sales_by_city, lat="lat", lon="lon", hover_name="city",
                                    size=val_col, color=val_col, zoom=3, height=400,
                                    title="1. Sales Concentration by Geolocation")
            fig.update_layout(mapbox_style="open-street-map")
            st.plotly_chart(fig, use_container_width=True)

        # 2. Regional Performance (Density Map)
        with col2:
            fig = px.density_mapbox(df, lat='lat', lon='lon', z=val_col, radius=20,
                                    center=dict(lat=20.5937, lon=78.9629), zoom=3,
                                    mapbox_style="open-street-map", title="2. Regional Revenue Density")
            st.plotly_chart(fig, use_container_width=True)

        col3, col4 = st.columns(2)
        # 3. City-wise Profitability
        with col3:
            profit_col = 'predicted_profit' if 'predicted_profit' in df.columns else val_col
            fig = px.bar(df.groupby('city')[profit_col].mean().reset_index(), 
                         x='city', y=profit_col, color=profit_col, 
                         title="3. Average Profitability by City")
            st.plotly_chart(fig, use_container_width=True)

        # 4. Logistics & Supply Chain Routes (Simulated)
        with col4:
            # Simulate routes from a central warehouse (e.g., Delhi) to cities
            routes_lat = []
            routes_lon = []
            
            # Helper to get coords safely
            def get_coords(city_name):
                return coords.get(city_name, (20.5937, 78.9629))

            hub = get_coords('Delhi')
            
            for city in df['city'].unique():
                dest = get_coords(city)
                # Add route: Hub -> Dest -> None (to break line)
                routes_lat.extend([hub[0], dest[0], None])
                routes_lon.extend([hub[1], dest[1], None])
            
            fig = go.Figure(go.Scattermapbox(
                mode = "lines", lon = routes_lon, lat = routes_lat,
                marker = {'size': 10}, line=dict(width=1, color='blue')))
            fig.update_layout(mapbox_style="open-street-map", 
                              margin={"r":0,"t":30,"l":0,"b":0},
                              title="4. Supply Chain Logistics Routes", height=400)
            st.plotly_chart(fig, use_container_width=True)
            
        # 5. Market Penetration Bubble Chart
        st.subheader("Market Penetration")
        mp_data = df.groupby('state').agg({val_col: 'sum', 'customer_rating': 'mean'}).reset_index() if 'customer_rating' in df.columns else df.groupby('state')[val_col].sum().reset_index()
        if 'customer_rating' not in mp_data.columns: mp_data['customer_rating'] = np.random.uniform(3.5, 5, len(mp_data))
        
        fig = px.scatter(mp_data, x=val_col, y='customer_rating', size=val_col, color='state',
                         title="5. Market Penetration vs Customer Satisfaction (State-wise)")
        st.plotly_chart(fig, use_container_width=True)


    # --- TAB 2: PREMIUM FINANCIALS (5 Charts) ---
    with tabs[1]:
        col1, col2 = st.columns(2)
        
        # 6. EBITDA Bridge (Waterfall)
        with col1:
            measures = ["Revenue", "COGS", "Gross Profit", "OpEx", "EBITDA"]
            values = [1000000, -400000, 0, -200000, 0] # Example Base
            fig = go.Figure(go.Waterfall(
                name = "20", orientation = "v",
                measure = ["relative", "relative", "total", "relative", "total"],
                x = measures,
                textposition = "outside",
                text = ["+1M", "-400k", "600k", "-200k", "400k"],
                y = values,
                connector = {"line":{"color":"rgb(63, 63, 63)"}},
            ))
            fig.update_layout(title = "6. EBITDA Bridge Analysis")
            st.plotly_chart(fig, use_container_width=True)

        # 7. Dupont Analysis (Simulated)
        with col2:
            metrics = ['Net Profit Margin', 'Asset Turnover', 'Financial Leverage']
            scores = [0.15, 0.8, 1.2]
            fig = px.bar(x=metrics, y=scores, title="7. Dupont Identity Decomposition", text_auto=True)
            st.plotly_chart(fig, use_container_width=True)

        col3, col4 = st.columns(2)
        # 8. Working Capital Trends
        with col3:
            dates_q = pd.date_range(end=datetime.now(), periods=12, freq='M')
            wc = np.random.randint(50000, 200000, 12)
            fig = px.line(x=dates_q, y=wc, title="8. Monthly Working Capital Trend", markers=True)
            st.plotly_chart(fig, use_container_width=True)

        # 9. Cost of Capital (WACC)
        with col4:
            components = ['Equity Cost', 'Debt Cost']
            wacc_vals = [12, 5]
            fig = px.pie(values=wacc_vals, names=components, title="9. Weighted Average Cost of Capital (WACC)", hole=0.7)
            st.plotly_chart(fig, use_container_width=True)
            
        # 10. Liquidity Ratios
        ratios = ['Current Ratio', 'Quick Ratio', 'Cash Ratio']
        vals_r = [1.5, 1.2, 0.5]
        fig = px.bar(x=ratios, y=vals_r, title="10. Liquidity Ratios Overview", color=ratios)
        st.plotly_chart(fig, use_container_width=True)
        
    # --- TAB 3: ADVANCED MARKET ANALYSIS (5 Charts) ---
    with tabs[2]:
        col1, col2 = st.columns(2)
        
        # 11. Competitor Benchmarking (Simulated)
        with col1:
            competitors = ['Your Biz', 'Comp A', 'Comp B', 'Comp C']
            share = [30, 25, 20, 25]
            fig = px.pie(values=share, names=competitors, title="11. Market Share Distribution")
            st.plotly_chart(fig, use_container_width=True)
            
        # 12. Price Elasticity Curve
        with col2:
            prices = np.linspace(10, 100, 20)
            demand = 1000 - 8 * prices + np.random.normal(0, 10, 20)
            fig = px.scatter(x=prices, y=demand, trendline="ols", title="12. Price Elasticity of Demand")
            st.plotly_chart(fig, use_container_width=True)
            
        # 13. Customer Acquisition Cost (CAC) vs LTV
        col3, col4 = st.columns(2)
        with col3:
            months_l = ['Q1', 'Q2', 'Q3', 'Q4']
            cac = [500, 480, 450, 420]
            ltv = [1500, 1600, 1650, 1800]
            fig = go.Figure()
            fig.add_trace(go.Bar(name='CAC', x=months_l, y=cac))
            fig.add_trace(go.Bar(name='LTV', x=months_l, y=ltv))
            fig.update_layout(title="13. LTV to CAC Ratio Analysis")
            st.plotly_chart(fig, use_container_width=True)
            
        # 14. Brand Sentiment Word Cloud (Simulated Bars)
        with col4:
            words = ['Quality', 'Service', 'Price', 'Delivery', 'Support']
            freq = [50, 30, 45, 25, 40]
            fig = px.bar(y=words, x=freq, orientation='h', title="14. Top Brand Associations (Sentiment)")
            st.plotly_chart(fig, use_container_width=True)
            
        # 15. Market Opportunity Quadrant
        opps = pd.DataFrame({
            'Market Size': np.random.randint(10, 100, 10),
            'Growth Rate': np.random.randint(5, 30, 10),
            'Segment': [f'Seg {i}' for i in range(10)]
        })
        fig = px.scatter(opps, x='Market Size', y='Growth Rate', text='Segment', size='Market Size', 
                         title="15. Market Opportunity Matrix (Growth vs Size)")
        st.plotly_chart(fig, use_container_width=True)
        
    # --- TAB 4: AI & PREDICTIVE INSIGHTS (5 Charts) ---
    with tabs[3]:
        col1, col2 = st.columns(2)
        
        # 16. Anomaly Detection in Transactions
        with col1:
            dates_a = pd.date_range(end=datetime.now(), periods=50)
            trans_vol = np.random.normal(100, 10, 50)
            trans_vol[40] = 200 # Anomaly
            fig = px.line(x=dates_a, y=trans_vol, title="16. Transaction Anomaly Detection")
            st.plotly_chart(fig, use_container_width=True)

        # 17. Churn Prediction Probabilities
        with col2:
            probs = np.random.beta(2, 5, 1000)
            fig = px.histogram(probs, title="17. Customer Churn Probability Distribution", labels={'value': 'Churn Prob'})
            st.plotly_chart(fig, use_container_width=True)
            
        # 18. Sales Decomposition (Trend/Seasonality)
        col3, col4 = st.columns(2)
        with col3:
            t = np.linspace(0, 4*np.pi, 100)
            y = 10 + 0.5*t + np.sin(t)
            fig = px.line(x=t, y=y, title="18. Sales Decomposition (Trend + Seasonality)")
            st.plotly_chart(fig, use_container_width=True)
            
        # 19. Inventory Optimization Curve
        with col4:
            stock = np.linspace(0, 100, 50)
            holding_cost = stock * 2
            stockout_limit = 1000 / (stock + 1)
            total_c = holding_cost + stockout_limit
            fig = px.line(x=stock, y=total_c, title="19. Inventory Cost Optimization Curve")
            st.plotly_chart(fig, use_container_width=True)
            
        # 20. Scenario Simulation Stress Test
        scenarios = ['Base', 'Best Case', 'Worst Case', 'Recession']
        outcomes = [100, 150, 50, 30]
        fig = px.bar(x=scenarios, y=outcomes, color=scenarios, title="20. Stress Test Scenario Outcomes (Profit Index)")
        st.plotly_chart(fig, use_container_width=True)


def show_3d_and_immersive_analytics(df):
    st.markdown("---")
    st.markdown("<h2 class='section-header'>🌟 3D & Immersive Analytics</h2>", unsafe_allow_html=True)

    tabs = st.tabs(["3D Market Terrain", "Network Graphs", "Multidimensional Clustering"])

    with tabs[0]:
        st.subheader("3D Sales Terrain Analysis")
        # 3D Surface Plot of Sales vs Profit vs Customer Rating
        if all(col in df.columns for col in ['customer_rating', 'profit_margin', 'monthly_sales']):
            # Create a meshgrid for surface plot simulation
            x = np.linspace(df['customer_rating'].min(), df['customer_rating'].max(), 50)
            y = np.linspace(df['profit_margin'].min(), df['profit_margin'].max(), 50)
            X, Y = np.meshgrid(x, y)
            # Simulate Z as a function of X and Y (e.g. Sales) with some noise
            Z = (X**2 + Y**2) * 1000 + np.random.normal(0, 100, X.shape)
            
            fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y, colorscale='Viridis')])
            fig.update_layout(title='3D Terrain: Sales Volume by Rating & Margin', autosize=True,
                              scene=dict(xaxis_title='Customer Rating', yaxis_title='Profit Margin', zaxis_title='Sales Vol'))
            st.plotly_chart(fig, use_container_width=True)
            
        col1, col2 = st.columns(2)
        with col1:
             # 3D Scatter with size and color
             if 'employee_efficiency' in df.columns:
                 # Sample data to avoid overload
                 sample_size = min(500, len(df))
                 df_sample = df.sample(sample_size)
                 fig = px.scatter_3d(df_sample, x='monthly_sales', y='operating_cost', z='profit_margin',
                                     color='risk_band' if 'risk_band' in df.columns else None,
                                     size='employee_count', opacity=0.7,
                                     title="3D Operational Metrics Cube")
                 st.plotly_chart(fig, use_container_width=True)
        
        with col2:
             # 3D Line Plot for Trajectory
             t = np.linspace(0, 20, 100)
             x = np.cos(t) * t
             y = np.sin(t) * t
             z = t
             fig = go.Figure(data=[go.Scatter3d(x=x, y=y, z=z, mode='markers', marker=dict(size=5, color=z, colorscale='Viridis'))])
             fig.update_layout(title="3D Growth Trajectory Simulation", scene=dict(xaxis_title="Market Share", yaxis_title="Innovation", zaxis_title="Time"))
             st.plotly_chart(fig, use_container_width=True)

    with tabs[1]:
        st.subheader("Interactive Network Analysis")
        # Simulated Network Graph of Business Relationships
        edge_x = []
        edge_y = []
        node_x = np.random.uniform(0, 10, 50)
        node_y = np.random.uniform(0, 10, 50)
        
        for i in range(50):
            for j in range(i+1, 50):
                if np.random.random() > 0.9: # 10% connection probability
                    edge_x.extend([node_x[i], node_x[j], None])
                    edge_y.extend([node_y[i], node_y[j], None])

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            marker=dict(
                showscale=True,
                colorscale='YlGnBu',
                reversescale=True,
                color=[],
                size=10,
                colorbar=dict(
                    thickness=15,
                    title='node connections',
                    xanchor='left'
                ),
                line_width=2))
        
        node_adjacencies = []
        node_text = []
        # Simplified adjacency calculation for demo
        for i in range(50):
             adj = np.random.randint(1, 10)
             node_adjacencies.append(adj)
             node_text.append(f'Entity {i} (# Connections: {adj})')

        node_trace.marker.color = node_adjacencies
        node_trace.text = node_text
        
        fig = go.Figure(data=[edge_trace, node_trace],
                     layout=go.Layout(
                        title=dict(text='Supplier-Client Network & Interdependencies', font=dict(size=16)),
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20,l=5,r=5,t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                        )
        st.plotly_chart(fig, use_container_width=True)

    with tabs[2]:
        st.subheader("Multidimensional Clustering")
        if 'business_type' in df.columns:
            # Parallel Categories
            fig = px.parallel_categories(df.sample(min(500, len(df))), 
                                         dimensions=['business_type', 'city_tier', 'risk_band'],
                                         color='profit_margin' if 'profit_margin' in df.columns else None, 
                                         color_continuous_scale=px.colors.sequential.Inferno,
                                         title="Multi-Category Flow Analysis")
            st.plotly_chart(fig, use_container_width=True)
            
        # Radar Chart comparison (Simulated)
        categories = ['Innovation', 'Sustainability', 'Employee Sat.', 'Cust. Loyalty', 'Brand Strength']
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
              r=[4, 3, 5, 4, 3],
              theta=categories,
              fill='toself',
              name='Current Year'
        ))
        fig.add_trace(go.Scatterpolar(
              r=[5, 4, 4, 5, 5],
              theta=categories,
              fill='toself',
              name='Projected Next Year'
        ))

        fig.update_layout(
          polar=dict(
            radialaxis=dict(
              visible=True,
              range=[0, 5]
            )),
          title="Strategic KPI Radar Scan",
          showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)


def show_comprehensive_bi_suite(df):
    st.markdown("---")
    st.markdown("<h2 class='section-header'>📈 Comprehensive KPI Dashboard</h2>", unsafe_allow_html=True)
    
    tabs = st.tabs([
        "💰 Revenue Dynamics", 
        "💹 Profitability Matrix", 
        "⚙️ Operational Efficiency", 
        "👥 Customer LTV", 
        "🚚 Supply Chain", 
        "🛡️ Risk & Compliance",
        "🚀 Innovation & Future Growth"
    ])
    
    # ---------------------------------------------------------
    # TAB 1: Revenue Dynamics (5 Charts)
    # ---------------------------------------------------------
    with tabs[0]:
        st.subheader("Revenue & Sales Velocity Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            # 1. Weekly Sales Trend with Forecast
            if 'monthly_sales' in df.columns:
                # Simulate weekly data
                dates = pd.date_range(end=datetime.now(), periods=52, freq='W')
                sales = np.random.normal(df['monthly_sales'].mean()/4, df['monthly_sales'].std()/10, 52)
                forecast = [x * (1 + i*0.01) for i, x in enumerate(sales[-10:])] # Simple growth
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=dates, y=sales, mode='lines+markers', name='Actual Sales'))
                fig.add_trace(go.Scatter(x=pd.date_range(start=dates[-1], periods=10, freq='W'), y=forecast, 
                                        mode='lines', line=dict(dash='dot'), name='Forecast'))
                fig.update_layout(title="Weekly Sales Velocity & Forecast")
                st.plotly_chart(fig, use_container_width=True)
                
            # 2. Revenue by Business Segment (Donut)
            if 'business_type' in df.columns:
                seg_rev = df.groupby('business_type')['monthly_sales'].sum().reset_index()
                fig = px.pie(seg_rev, values='monthly_sales', names='business_type', hole=0.4, 
                             title="Revenue Distribution by Segment")
                st.plotly_chart(fig, use_container_width=True)
                
        with col2:
            # 3. Monthly Growth Rate (Bar)
            growth_rates = np.random.uniform(-5, 15, 12)
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            fig = go.Figure(go.Bar(x=months, y=growth_rates, marker_color=np.where(growth_rates<0, 'red', 'green')))
            fig.update_layout(title="Monthly Revenue Growth Rate (%)")
            st.plotly_chart(fig, use_container_width=True)
            
            # 4. Top 10 High-Value Transactions (Table)
            high_val = df.nlargest(10, 'monthly_sales')[['business_type', 'city', 'monthly_sales', 'profit_margin']]
            fig = go.Figure(data=[go.Table(
                header=dict(values=list(high_val.columns), fill_color='paleturquoise', align='left'),
                cells=dict(values=[high_val.business_type, high_val.city, high_val.monthly_sales, high_val.profit_margin], 
                           fill_color='lavender', align='left'))
            ])
            fig.update_layout(title="Top 10 High-Value Contributors", height=300)
            st.plotly_chart(fig, use_container_width=True)
            
        # 5. Sales Concentration Curve (Lorenz Curve)
        sorted_sales = np.sort(df['monthly_sales'].values)
        lorenz = np.cumsum(sorted_sales) / np.sum(sorted_sales)
        lorenz = np.insert(lorenz, 0, 0) 
        fig = px.line(x=np.linspace(0, 1, len(lorenz)), y=lorenz, title="Sales Concentration (Lorenz Curve)")
        fig.add_shape(type="line", x0=0, y0=0, x1=1, y1=1, line=dict(color="red", dash="dash"))
        st.plotly_chart(fig, use_container_width=True)

    # ---------------------------------------------------------
    # TAB 2: Profitability Matrix (5 Charts)
    # ---------------------------------------------------------
    with tabs[1]:
        st.subheader("Profitability & Cost Structure")
        col1, col2 = st.columns(2)
        
        with col1:
            # 6. Gross vs Net Margin Comparison
            if 'profit_margin' in df.columns:
                # Simulate gross margin being consistently higher
                gross_margin = df['profit_margin'] * 1.5
                fig = go.Figure()
                fig.add_trace(go.Box(y=gross_margin, name='Gross Margin'))
                fig.add_trace(go.Box(y=df['profit_margin'], name='Net Margin'))
                fig.update_layout(title="Margin Analysis Distribution")
                st.plotly_chart(fig, use_container_width=True)
            
            # 7. Cost Breakdown Waterfall
            costs = {
                'Revenue': 1000000,
                'COGS': -400000,
                'Operating Exp': -200000,
                'Marketing': -100000,
                'Taxes': -50000,
                'Net Profit': 250000
            }
            fig = go.Figure(go.Waterfall(
                name = "20", orientation = "v",
                measure = ["relative", "relative", "relative", "relative", "relative", "total"],
                x = list(costs.keys()),
                textposition = "outside",
                text = [f"{v/1000}k" for v in costs.values()],
                y = list(costs.values()),
                connector = {"line":{"color":"rgb(63, 63, 63)"}},
            ))
            fig.update_layout(title="Cost Waterfall Analysis")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # 8. Profit per Employee by Role (Simulated Role)
            roles = ['Manager', 'Sales', 'Support', 'Tech', 'Admin']
            avg_prof = np.random.randint(5000, 50000, 5)
            fig = px.bar(x=roles, y=avg_prof, color=roles, title="Profit Contribution per Role")
            st.plotly_chart(fig, use_container_width=True)

            # 9. Return on Ad Spend (ROAS) Heatmap
            roas_matrix = np.random.uniform(1, 5, (5, 7)) # 5 channels, 7 days
            fig = px.imshow(roas_matrix, labels=dict(x="Day of Week", y="Channel", color="ROAS"),
                           x=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                           y=['Social', 'Search', 'Display', 'Email', 'Affiliate'],
                           title="ROAS Heatmap by Channel & Day")
            st.plotly_chart(fig, use_container_width=True)
            
        # 10. Break-even Analysis Chart
        units = np.linspace(0, 1000, 100)
        fixed_cost = 50000
        variable_cost = 20
        price = 100
        rv = price * units
        tc = fixed_cost + variable_cost * units
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=units, y=rv, name='Revenue'))
        fig.add_trace(go.Scatter(x=units, y=tc, name='Total Cost'))
        fig.add_shape(type="line", x0=625, y0=0, x1=625, y1=62500, line=dict(dash="dot"))
        fig.update_layout(title="Break-even Analysis (BEP)", xaxis_title="Units Sold", yaxis_title="Amount (₹)")
        st.plotly_chart(fig, use_container_width=True)

    # ---------------------------------------------------------
    # TAB 3: Operational Efficiency (5 Charts)
    # ---------------------------------------------------------
    with tabs[2]:
        st.subheader("Operational Excellence Metrics")
        
        # 11. OEE Gauge
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = 85,
            title = {'text': "Overall Equipment Effectiveness (OEE)"},
            gauge = {'axis': {'range': [None, 100]},
                     'steps' : [
                         {'range': [0, 50], 'color': "lightgray"},
                         {'range': [50, 80], 'color': "gray"}],
                     'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 90}}))
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
             # 12. Downtime Causes Pareto Chart
             causes = ['Machine Failure', 'Material Shortage', 'Operator Error', 'Software Glitch', 'Power Outage']
             counts = [50, 30, 15, 4, 1]
             fig = go.Figure([go.Bar(x=causes, y=counts)])
             fig.update_layout(title="Downtime Causes (Pareto Analysis)")
             st.plotly_chart(fig, use_container_width=True)
             
             # 13. Throughput Time Distribution
             times = np.random.gamma(2, 2, 1000)
             fig = px.histogram(times, nbins=30, title="Process Throughput Time Distribution")
             st.plotly_chart(fig, use_container_width=True)
             
        with col2:
             # 14. First Pass Yield Trend
             months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
             yield_pct = [92, 93, 91, 94, 95, 96]
             fig = px.line(x=months, y=yield_pct, markers=True, title="First Pass Yield (Quality Metric)")
             st.plotly_chart(fig, use_container_width=True)
             
             # 15. Capacity Utilization Heatmap
             cap_util = np.random.uniform(70, 100, (5, 24)) # 5 machines, 24 hours
             fig = px.imshow(cap_util, title="Hourly Capacity Utilization per Machine",
                            labels=dict(x="Hour of Day", y="Machine ID", color="Utilization %"))
             st.plotly_chart(fig, use_container_width=True)

    # ---------------------------------------------------------
    # TAB 4: Customer LTV (5 Charts)
    # ---------------------------------------------------------
    with tabs[3]:
        st.subheader("Customer Lifecycle & Value")
        
        col1, col2 = st.columns(2)
        with col1:
            # 16. Cohort Analysis Retention Heatmap
            cohort_data = np.array([
                [100, 80, 70, 60, 50],
                [100, 75, 65, 55, 0],
                [100, 70, 60, 0, 0],
                [100, 65, 0, 0, 0],
                [100, 0, 0, 0, 0]
            ])
            fig = px.imshow(cohort_data, text_auto=True, title="Customer Retention Cohort (%)",
                           labels=dict(x="Months Since Acquisition", y="Cohort Month", color="Retention"))
            st.plotly_chart(fig, use_container_width=True)
            
            # 17. Customer Segmentation (RFM)
            rfm = pd.DataFrame({
                'Recency': np.random.randint(1, 100, 100),
                'Frequency': np.random.randint(1, 20, 100),
                'Monetary': np.random.randint(100, 5000, 100)
            })
            fig = px.scatter_3d(rfm, x='Recency', y='Frequency', z='Monetary', color='Monetary', title="RFM Customer Segmentation")
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            # 18. LTV Prediction Curve
            months = np.arange(1, 25)
            ltv = 100 * np.log(months + 1)
            fig = px.area(x=months, y=ltv, title="Projected Average LTV Growth")
            st.plotly_chart(fig, use_container_width=True)
            
            # 19. Churn Reason Breakdown
            reasons = ['Price', 'Service', 'Competitor', 'Product Fit', 'Other']
            counts = [40, 25, 20, 10, 5]
            fig = px.funnel(y=reasons, x=counts, title="Churn Driver Analysis")
            st.plotly_chart(fig, use_container_width=True)
            
        # 20. Net Promoter Score (NPS) Trend
        nps_dates = pd.date_range(end=datetime.now(), periods=12, freq='M')
        nps_scores = np.random.randint(30, 70, 12)
        fig = px.bar(x=nps_dates, y=nps_scores, title="Monthly Net Promoter Score (NPS) Trend", color=nps_scores)
        st.plotly_chart(fig, use_container_width=True)

    # ---------------------------------------------------------
    # TAB 5: Supply Chain (5 Charts)
    # ---------------------------------------------------------
    with tabs[4]:
        st.subheader("Supply Chain Intelligence")
        
        col1, col2 = st.columns(2)
        with col1:
             # 21. Supplier Performance Rating
             suppliers = ['Sup A', 'Sup B', 'Sup C', 'Sup D', 'Sup E']
             ratings = [4.5, 3.8, 4.2, 2.5, 4.8]
             fig = px.bar(x=suppliers, y=ratings, title="Supplier Reliability Ratings", color=ratings, color_continuous_scale='RdYlGn')
             st.plotly_chart(fig, use_container_width=True)
             
             # 22. Inventory Value Treemap
             if 'business_type' in df.columns:
                 # Group by type and region for simulation
                 treemap_df = df.groupby('business_type').agg({'monthly_sales': 'sum'}).reset_index()
                 treemap_df['inventory_value'] = treemap_df['monthly_sales'] * 0.2
                 fig = px.treemap(treemap_df, path=['business_type'], values='inventory_value', title="Inventory Breakdown by Category")
                 st.plotly_chart(fig, use_container_width=True)
                 
        with col2:
             # 23. Lead Time Variability
             lead_times = np.random.normal(10, 2, 100)
             fig = px.box(y=lead_times, title="Supplier Lead Time Variability (Days)")
             st.plotly_chart(fig, use_container_width=True)
             
             # 24. Order Fulfillment Rate Gauge
             fig = go.Figure(go.Indicator(
                mode="number+delta",
                value=96.5,
                title={"text": "Order Fulfillment Rate (%)"},
                delta={'reference': 95, 'relative': False}
             ))
             fig.update_layout(height=300)
             st.plotly_chart(fig, use_container_width=True)
             
        # 25. Supply Chain Network Map (Sankey)
        fig = go.Figure(data=[go.Sankey(
            node = dict(
              pad = 15,
              thickness = 20,
              line = dict(color = "black", width = 0.5),
              label = ["Raw Material", "Manufacturing", "Distribution", "Retail", "Customer"],
              color = "blue"
            ),
            link = dict(
              source = [0, 1, 2, 3],
              target = [1, 2, 3, 4],
              value = [800, 750, 700, 680]
          ))])
        fig.update_layout(title="Supply Chain Material Flow Analysis")
        st.plotly_chart(fig, use_container_width=True)

    # ---------------------------------------------------------
    # TAB 6: Risk & Compliance (5 Charts)
    # ---------------------------------------------------------
    with tabs[5]:
        st.subheader("Risk Management & Compliance")
        
        col1, col2 = st.columns(2)
        with col1:
            # 26. Risk Exposure Heatmap
            risk_cats = ['Financial', 'Operational', 'Strategic', 'Compliance']
            impact = ['Low', 'Medium', 'High', 'Critical']
            risk_matrix = np.random.randint(1, 10, (4, 4))
            fig = px.imshow(risk_matrix, x=impact, y=risk_cats, title="Enterprise Risk Exposure Heatmap",
                           labels=dict(x="Impact Severity", y="Risk Category", color="Likelihood Score"))
            st.plotly_chart(fig, use_container_width=True)
            
            # 27. Regulatory Compliance Score
            depts = ['HR', 'Finance', 'IT', 'Ops', 'Sales']
            scores = [100, 98, 95, 92, 90]
            fig = px.bar_polar(r=scores, theta=depts, title="Dept. Compliance Scores", color=scores, color_continuous_scale='RdYlGn', range_r=[0,100])
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            # 28. Incident Reporting Trend
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            incidents = [5, 2, 8, 3, 1, 0]
            fig = px.area(x=months, y=incidents, title="Safety/Security Incidents Reported", color_discrete_sequence=['red'])
            st.plotly_chart(fig, use_container_width=True)
            
            # 29. Audit Result Distribution
            audit_status = ['Pass', 'Minor NC', 'Major NC']
            audit_counts = [85, 12, 3]
            fig = px.pie(names=audit_status, values=audit_counts, title="Internal Audit Results")
            st.plotly_chart(fig, use_container_width=True)
            
        # 30. Cybersecurity Threat Monitor (Simulated)
        threat_levels = np.random.randint(1, 100, 24)
        fig = px.area(x=list(range(24)), y=threat_levels, title="24-Hour Network Threat Activity Monitor")
        fig.update_layout(xaxis_title="Hour", yaxis_title="Threat Signals")
        st.plotly_chart(fig, use_container_width=True)
