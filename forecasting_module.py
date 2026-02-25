
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from prophet import Prophet
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from datetime import datetime
import hashlib

# --- CACHING ENGINES ---
@st.cache_resource
def get_trained_models(df_json, features_sim):
    """Trains and caches simulation models for zero-lag real-time prediction"""
    df = pd.read_json(df_json)
    
    # Ensure monthly_sales is numeric
    df['monthly_sales'] = pd.to_numeric(df['monthly_sales'], errors='coerce').fillna(0)
    le_biz = LabelEncoder()
    le_city = LabelEncoder()
    
    df['biz_encoded'] = le_biz.fit_transform(df['business_type'].astype(str))
    df['city_encoded'] = le_city.fit_transform(df['city'].astype(str))
    
    # Feature set for simulation (including encoded categoricals)
    X_features = features_sim + ['biz_encoded', 'city_encoded']
    X = df[X_features].fillna(0)
    y = df['monthly_sales']
    
    # Model 1: Linear Regression
    lr = LinearRegression().fit(X, y)
    
    # Model 2: Random Forest
    rf = RandomForestRegressor(n_estimators=50, random_state=42).fit(X, y)
    
    return lr, rf, le_biz, le_city

@st.cache_resource
def get_prophet_model(ts_data_json):
    """Trains and caches the Prophet model for temporal seasonality"""
    ts_data = pd.read_json(ts_data_json)
    # Ensure ds is datetime
    ts_data['ds'] = pd.to_datetime(ts_data['ds'])
    m = Prophet(yearly_seasonality=True if len(ts_data) > 12 else False, 
                daily_seasonality=False, weekly_seasonality=False)
    m.fit(ts_data)
    return m

def show_forecasting_section(df):
    st.markdown("<h2 style='text-align: center; color: #EA4643;'>Time Series Forecasting & Predictive Intelligence</h2>", unsafe_allow_html=True)
    
    if df is None or df.empty:
        st.warning("Please load or upload a dataset first.")
        return

    # Sidebar for dynamic control
    with st.sidebar:
        st.markdown("### 🛠️ Forecast Configuration")
        forecast_horizon = st.slider("Forecast Horizon (Months)", min_value=2, max_value=24, value=12)

    # Date Processing
    df_ts = df.copy()
    if 'month' in df_ts.columns and 'year' in df_ts.columns:
        df_ts['year'] = pd.to_numeric(df_ts['year'], errors='coerce').fillna(2024).astype(int)
        df_ts['month'] = pd.to_numeric(df_ts['month'], errors='coerce').fillna(1).astype(int).clip(1, 12)
        df_ts['date'] = pd.to_datetime(df_ts['year'].astype(str) + '-' + df_ts['month'].astype(str).str.zfill(2) + '-01')
        df_ts = df_ts.dropna(subset=['date'])
    elif 'date' in df_ts.columns:
        df_ts['date'] = pd.to_datetime(df_ts['date'], errors='coerce')
        df_ts = df_ts.dropna(subset=['date'])
    else:
        st.error("Dataset missing time columns.")
        return

    # Aggregation
    ts_data = df_ts.groupby('date')['monthly_sales'].sum().reset_index()
    ts_data.columns = ['ds', 'y']
    ts_data = ts_data.sort_values('ds')
    
    # Handle Sparse
    original_ts_data = ts_data.copy()
    if len(ts_data) < 2 and len(ts_data) > 0:
        first_date = ts_data['ds'].iloc[0]
        prev_date = first_date - pd.DateOffset(months=1)
        prev_val = ts_data['y'].iloc[0] * 0.95
        ts_data = pd.concat([pd.DataFrame({'ds': [prev_date], 'y': [prev_val]}), ts_data], ignore_index=True)

    if len(ts_data) == 0:
        st.error("No valid historical records.")
        return

    # --- MODEL TRAINING (CACHED) ---
    features_sim = [
        "city_tier", "store_size_sqft", "years_of_operation", "month", "year", 
        "is_festival_season", "avg_daily_footfall", "conversion_rate", 
        "avg_transaction_value", "customer_rating", "marketing_spend", 
        "discount_percentage", "inventory_level", "employee_count", "avg_employee_salary"
    ]
    # Ensure all columns exist
    for col in features_sim:
        if col not in df.columns:
            df[col] = 0
            
    with st.spinner("Synchronizing Neural Engines..."):
        # Serialize for caching with ISO date format to prevent overflow
        df_json = df.to_json(date_format='iso')
        ts_json = ts_data.to_json(date_format='iso')
        
        lr_model, rf_model, le_biz, le_city = get_trained_models(df_json, features_sim)
        m_prophet = get_prophet_model(ts_json)
        
        # Trend model (Linear) - non-cached as it's very fast
        ts_data['ordinal'] = ts_data['ds'].apply(lambda x: x.toordinal())
        lr_trend = LinearRegression().fit(ts_data[['ordinal']], ts_data['y'])

    # --- SIMULATOR UI ---
    st.markdown("---")
    st.markdown("### 🔮 Real-Time Enterprise Simulator")
    
    sim_cols = st.columns(3)
    with sim_cols[0]:
        sel_biz = st.selectbox("Business Type", options=le_biz.classes_)
        sel_city = st.selectbox("City", options=le_city.classes_)
        city_tier = st.slider("City Tier", 1, 3, 1)
        store_size = st.number_input("Store Size", value=int(df['store_size_sqft'].mean()))
        years_op = st.number_input("Years Operating", value=int(df['years_of_operation'].mean()))
    
    with sim_cols[1]:
        sel_month = st.slider("Month", 1, 12, datetime.now().month)
        sel_year = st.slider("Year", 2024, 2026, 2025)
        is_fest = st.toggle("Festival Season", value=False)
        footfall = st.number_input("Avg Daily Footfall", value=int(df['avg_daily_footfall'].mean()))
        conv = st.slider("Conversion", 0.0, 1.0, float(df['conversion_rate'].mean()))
        atv = st.number_input("Avg Transaction Value (₹)", value=int(df['avg_transaction_value'].mean()))

    with sim_cols[2]:
        rating = st.slider("Rating", 1.0, 5.0, 4.0)
        mkt = st.number_input("Mkt Spend (₹)", value=int(df['marketing_spend'].mean()))
        disc = st.slider("Discount %", 0, 50, 10)
        inv = st.number_input("Inv Level", value=int(df['inventory_level'].mean()))
        emp = st.number_input("Emp Count", value=int(df['employee_count'].mean()))
        sal = st.number_input("Avg Salary (₹)", value=int(df['avg_employee_salary'].mean()))

    # --- REAL-TIME PREDICTION ---
    # Prepare Input
    input_vals = {
        "city_tier": city_tier, "store_size_sqft": store_size, "years_of_operation": years_op,
        "month": sel_month, "year": sel_year, "is_festival_season": 1 if is_fest else 0,
        "avg_daily_footfall": footfall, "conversion_rate": conv, "avg_transaction_value": atv,
        "customer_rating": rating, "marketing_spend": mkt, "discount_percentage": disc,
        "inventory_level": inv, "employee_count": emp, "avg_employee_salary": sal,
        "biz_encoded": le_biz.transform([sel_biz])[0],
        "city_encoded": le_city.transform([sel_city])[0]
    }
    input_df = pd.DataFrame([input_vals])[features_sim + ['biz_encoded', 'city_encoded']]
    
    # 1. LR Pred
    p_lr = lr_model.predict(input_df)[0]
    # 2. RF Pred
    p_rf = rf_model.predict(input_df)[0]
    # 3. Prophet Pred
    p_prophet = m_prophet.predict(pd.DataFrame({'ds': [pd.to_datetime(f"{sel_year}-{sel_month}-01")]})).iloc[0]['yhat']

    # KPI Metrics
    st.markdown("#### 🎯 Prediction Intelligence ")
    k1, k2, k3 = st.columns(3)
    k1.metric("Scikit-Learn OLS", f"₹{max(0, p_lr):,.2f}", "Baseline")
    k2.metric("Scikit-Learn RF", f"₹{max(0, p_rf):,.2f}", "Ensemble")
    k3.metric("Neural Prophet", f"₹{max(0, p_prophet):,.2f}", "Temporal")

    avg_sim = (p_lr + p_rf + p_prophet) / 3
    st.markdown(f"""
    <div style='background: #1A202C; color: white; padding: 30px; border-radius: 20px; text-align: center; margin: 25px 0; border-bottom: 8px solid #EA4643; box-shadow: 0 15px 35px rgba(234,70,67,0.15);'>
        <p style='color: #718096; margin-bottom: 5px; font-weight: 800; text-transform: uppercase; letter-spacing: 3px; font-size: 12px;'>Unified Intelligence Consensus</p>
        <h2 style='margin: 0; color: #EA4643; font-size: 56px; font-weight: 900; filter: drop-shadow(0 0 10px rgba(234,70,67,0.3));'>₹ {max(0, avg_sim):,.2f}</h2>
        <p style='color: #A0AEC0; margin-top: 15px; font-style: italic;'>Synchronized across statistical, ensemble, and neural architectures.</p>
    </div>
    """, unsafe_allow_html=True)

    # --- TIME SERIES (PROPHET DATAFLOW) ---
    future_df = m_prophet.make_future_dataframe(periods=forecast_horizon, freq='M')
    forecast = m_prophet.predict(future_df)
    forecast['lr_forecast'] = lr_trend.predict(future_df['ds'].apply(lambda x: x.toordinal()).values.reshape(-1, 1))

    # --- THE 10 VISUALISATIONS ---
    st.markdown("### 📊 Strategic Visualisations")
    
    # Grid layout for charts
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("#### 1. Prophet Neural Forecast")
        f1 = go.Figure()
        f1.add_trace(go.Scatter(x=original_ts_data['ds'], y=original_ts_data['y'], name='Actual', line=dict(color='#1A202C', width=2)))
        f1.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name='Forecast', line=dict(color='#EA4643', dash='dash')))
        f1.update_layout(template="plotly_white", margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(f1, use_container_width=True)

        st.markdown("#### 3. Execution Benchmark")
        f3 = go.Figure()
        f3.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name='Prophet', line=dict(color='#EA4643')))
        f3.add_trace(go.Scatter(x=forecast['ds'], y=forecast['lr_forecast'], name='OLS', line=dict(color='#718096', dash='dot')))
        f3.update_layout(template="plotly_white", margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(f3, use_container_width=True)

    with c2:
        st.markdown("#### 2. Regression Trend")
        f2 = px.scatter(original_ts_data, x='ds', y='y', trendline="ols", color_discrete_sequence=['#EA4643'])
        f2.update_layout(template="plotly_white", margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(f2, use_container_width=True)

        st.markdown("#### 4. Critical Drivers")
        imp = pd.DataFrame({'f': features_sim + ['biz_encoded', 'city_encoded'], 'i': rf_model.feature_importances_}).sort_values('i', ascending=False).head(8)
        f4 = px.bar(imp, x='i', y='f', orientation='h', color_discrete_sequence=['#EA4643'])
        f4.update_layout(template="plotly_white", margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(f4, use_container_width=True)

    # Secondary Row
    st.markdown("#### 5. Seasonality Boxplot")
    st.plotly_chart(px.box(df, x='month', y='monthly_sales', color_discrete_sequence=['#EA4643']).update_layout(template="plotly_white"), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown("#### 6. Performance by Vertical")
        v_df = df_ts.groupby(['date', 'business_type'])['monthly_sales'].sum().reset_index()
        st.plotly_chart(px.line(v_df, x='date', y='monthly_sales', color='business_type').update_layout(template="plotly_white"), use_container_width=True)
    
    with c4:
        st.markdown("#### 7. Geographic Stack")
        g_df = df_ts.groupby(['date', 'city'])['monthly_sales'].sum().reset_index()
        st.plotly_chart(px.area(g_df, x='date', y='monthly_sales', color='city').update_layout(template="plotly_white"), use_container_width=True)

    st.markdown("#### 8. Moving Efficiency")
    original_ts_data['rolling'] = original_ts_data['y'].rolling(3).mean()
    f8 = go.Figure()
    f8.add_trace(go.Bar(x=original_ts_data['ds'], y=original_ts_data['y'], name='Sales', marker_color='#E2E8F0'))
    f8.add_trace(go.Scatter(x=original_ts_data['ds'], y=original_ts_data['rolling'], name='3-Month Avg', line=dict(color='#EA4643')))
    st.plotly_chart(f8.update_layout(template="plotly_white"), use_container_width=True)

    c5, c6 = st.columns(2)
    with c5:
        st.markdown("#### 9. Intensity Matrix")
        pivot = df.pivot_table(index='year', columns='month', values='monthly_sales', aggfunc='sum')
        st.plotly_chart(px.imshow(pivot, color_continuous_scale='Reds').update_layout(template="plotly_white"), use_container_width=True)
    
    with c6:
        st.markdown("#### 10. Cumulative Growth")
        original_ts_data['cum'] = original_ts_data['y'].cumsum()
        st.plotly_chart(px.area(original_ts_data, x='ds', y='cum', color_discrete_sequence=['#1A202C']).update_layout(template="plotly_white"), use_container_width=True)
