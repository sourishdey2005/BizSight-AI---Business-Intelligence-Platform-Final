
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
    df['monthly_sales'] = pd.to_numeric(df['monthly_sales'], errors='coerce').fillna(0)
    le_biz = LabelEncoder()
    le_city = LabelEncoder()
    df['biz_encoded'] = le_biz.fit_transform(df['business_type'].astype(str))
    df['city_encoded'] = le_city.fit_transform(df['city'].astype(str))
    X_features = features_sim + ['biz_encoded', 'city_encoded']
    X = df[X_features].fillna(0)
    y = df['monthly_sales']
    lr = LinearRegression().fit(X, y)
    rf = RandomForestRegressor(n_estimators=50, random_state=42).fit(X, y)
    return lr, rf, le_biz, le_city

@st.cache_resource
def get_prophet_model(ts_data_json):
    """Trains and caches the Prophet model for temporal seasonality"""
    ts_data = pd.read_json(ts_data_json)
    ts_data['ds'] = pd.to_datetime(ts_data['ds'])
    m = Prophet(yearly_seasonality=True if len(ts_data) > 12 else False, 
                daily_seasonality=False, weekly_seasonality=False)
    m.fit(ts_data)
    return m

def show_forecasting_section(df):
    st.markdown("<h2 style='text-align: center; color: #EA4643;'>Enterprise  Strategic Predictive Layers</h2>", unsafe_allow_html=True)
    
    if df is None or df.empty:
        st.warning("Please load or upload a dataset first.")
        return

    with st.sidebar:
        st.markdown("### 🛠️ Global Parameters")
        forecast_horizon = st.slider("Forecast Horizon", 2, 24, 12)

    # Date Processing - Ensure 'date' exists in main df for all 31 visualisations
    if 'month' in df.columns and 'year' in df.columns:
        df['year_tmp'] = pd.to_numeric(df['year'], errors='coerce').fillna(2024).astype(int)
        df['month_tmp'] = pd.to_numeric(df['month'], errors='coerce').fillna(1).astype(int).clip(1, 12)
        df['date'] = pd.to_datetime(df['year_tmp'].astype(str) + '-' + df['month_tmp'].astype(str).str.zfill(2) + '-01')
        df = df.drop(columns=['year_tmp', 'month_tmp'])
    elif 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    if 'date' not in df.columns or df['date'].isna().all():
        st.error("Dataset missing time columns or contains invalid dates.")
        return
    
    df = df.dropna(subset=['date'])
    df_ts = df.copy()

    ts_data = df_ts.groupby('date')['monthly_sales'].sum().reset_index()
    ts_data.columns = ['ds', 'y']
    ts_data = ts_data.sort_values('ds')

    # Handle Sparse Data (Prophet requires at least 2 points)
    original_ts_data = ts_data.copy()
    if len(ts_data) == 0:
        st.error("No non-empty sales data found for the selected filters.")
        return
        
    if len(ts_data) < 2:
        # Augment with a synthetic previous month to satisfy Prophet's 2-point requirement
        first_date = ts_data['ds'].iloc[0]
        prev_date = first_date - pd.DateOffset(months=1)
        prev_val = ts_data['y'].iloc[0] * 0.95
        ts_data = pd.concat([pd.DataFrame({'ds': [prev_date], 'y': [prev_val]}), ts_data], ignore_index=True)

    # --- ENGINES ---
    features_sim = [
        "city_tier", "store_size_sqft", "years_of_operation", "month", "year", 
        "is_festival_season", "avg_daily_footfall", "conversion_rate", 
        "avg_transaction_value", "customer_rating", "marketing_spend", 
        "discount_percentage", "inventory_level", "employee_count", "avg_employee_salary"
    ]
    for col in features_sim:
        if col not in df.columns: df[col] = 0
            
    with st.spinner("Calibrating 31 Visual Layers..."):
        df_json, ts_json = df.to_json(date_format='iso'), ts_data.to_json(date_format='iso')
        lr_model, rf_model, le_biz, le_city = get_trained_models(df_json, features_sim)
        m_prophet = get_prophet_model(ts_json)
        ts_data['ordinal'] = ts_data['ds'].apply(lambda x: x.toordinal())
        lr_trend = LinearRegression().fit(ts_data[['ordinal']], ts_data['y'])

    # --- SIMULATOR ---
    st.markdown("### 🔮 Real-Time Simulation Engine")
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        sel_biz = st.selectbox("Type", options=le_biz.classes_)
        sel_city = st.selectbox("Location", options=le_city.classes_)
        c_tier = st.slider("Tier", 1, 3, 1)
        s_size = st.number_input("Sqft", int(df['store_size_sqft'].mean()))
    with sc2:
        m_sel = st.slider("Mo", 1, 12, datetime.now().month)
        y_sel = st.slider("Yr", 2024, 2026, 2025)
        fest = st.toggle("Festival", False)
        ff = st.number_input("Footfall", int(df['avg_daily_footfall'].mean()))
    with sc3:
        cr = st.slider("Conv", 0.0, 1.0, float(df['conversion_rate'].mean()))
        atv = st.number_input("ATV", int(df['avg_transaction_value'].mean()))
        ms = st.number_input("Spend", int(df['marketing_spend'].mean()))
        inv = st.number_input("Inv", int(df['inventory_level'].mean()))

    # Prediction
    in_v = {
        "city_tier": c_tier,"store_size_sqft": s_size,"years_of_operation": int(df['years_of_operation'].mean()),
        "month": m_sel,"year": y_sel,"is_festival_season": 1 if fest else 0,
        "avg_daily_footfall": ff,"conversion_rate": cr,"avg_transaction_value": atv,
        "customer_rating": 4.0,"marketing_spend": ms,"discount_percentage": 10,
        "inventory_level": inv,"employee_count": int(df['employee_count'].mean()),"avg_employee_salary": int(df['avg_employee_salary'].mean()),
        "biz_encoded": le_biz.transform([sel_biz])[0], "city_encoded": le_city.transform([sel_city])[0]
    }
    i_df = pd.DataFrame([in_v])[features_sim + ['biz_encoded', 'city_encoded']]
    p_lr, p_rf = lr_model.predict(i_df)[0], rf_model.predict(i_df)[0]
    p_pr = m_prophet.predict(pd.DataFrame({'ds': [pd.to_datetime(f"{y_sel}-{m_sel}-01")]})).iloc[0]['yhat']

    k1, k2, k3 = st.columns(3)
    k1.metric("OLS Baseline", f"₹{max(0, p_lr):,.0f}", help="Statistical Multivariate Regression")
    k2.metric("Ensemble Logic", f"₹{max(0, p_rf):,.0f}", help="Random Forest Ensemble Prediction")
    k3.metric("Neural Trace", f"₹{max(0, p_pr):,.0f}", help="Prophet Neural Seasonality")

    # Secondary Business Intelligence KPIs
    avg_sim = (p_lr + p_rf + p_pr) / 3
    historical_avg = df['monthly_sales'].mean()
    growth_pct = ((avg_sim - historical_avg) / historical_avg) * 100 if historical_avg != 0 else 0
    
    # Model Variance (Risk Index)
    preds = np.array([p_lr, p_rf, p_pr])
    variance_pct = (preds.std() / preds.mean()) * 100 if preds.mean() != 0 else 0
    
    st.markdown("#### 📈 Business Intelligence KPIs")
    bk1, bk2, bk3, bk4 = st.columns(4)
    bk1.metric("Daily Runway", f"₹{max(0, avg_sim/30):,.0f}", "Target/Day")
    bk2.metric("Growth Forecast", f"{growth_pct:+.1f}%", "vs History")
    bk3.metric("Efficiency Score", f"{(avg_sim/max(1,s_size)):.1f}", "Rev/Sqft")
    bk4.metric("Model Consensus", f"{100-variance_pct:.1f}%", "Confidence", delta_color="normal")

    st.markdown(f"""
    <div style='background: #1A202C; color: white; padding: 30px; border-radius: 20px; text-align: center; margin: 25px 0; border-bottom: 8px solid #EA4643; box-shadow: 0 15px 35px rgba(234,70,67,0.15);'>
        <p style='color: #718096; margin-bottom: 5px; font-weight: 800; text-transform: uppercase; letter-spacing: 3px; font-size: 11px;'>Weighted Intelligence Consensus</p>
        <h2 style='margin: 0; color: #EA4643; font-size: 56px; font-weight: 900; filter: drop-shadow(0 0 12px rgba(234,70,67,0.4));'>₹ {max(0, avg_sim):,.2f}</h2>
        <div style='display: flex; justify-content: center; gap: 20px; margin-top: 15px;'>
            <span style='background: rgba(255,255,255,0.1); padding: 5px 15px; border-radius: 20px; font-size: 12px; color: #A0AEC0;'>Confidence: {100-variance_pct:.1f}%</span>
            <span style='background: rgba(255,255,255,0.1); padding: 5px 15px; border-radius: 20px; font-size: 12px; color: #A0AEC0;'>Mode: {'Aggressive' if avg_sim > historical_avg else 'Conservative'}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- 36 STRATEGIC VISUALISATIONS ---
    st.markdown("---")
    t = st.tabs(["Neural & Statistical", "Operational Deep-Dive", "Categorical & Spatial", "Advanced Business AI", "Efficiency Metrics", "Demand & Inventory Intelligence"])

    future = m_prophet.make_future_dataframe(periods=forecast_horizon, freq='M')
    fc = m_prophet.predict(future)
    fc['lr_trend'] = lr_trend.predict(future['ds'].apply(lambda x: x.toordinal()).values.reshape(-1,1))

    with t[0]: # 1-6
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 1. Neural Forecast & Uncertainty")
            f1 = go.Figure()
            f1.add_trace(go.Scatter(x=fc['ds'], y=fc['yhat_upper'], fill=None, mode='lines', line_color='rgba(234,70,67,0.2)', name='Confidence+'))
            f1.add_trace(go.Scatter(x=fc['ds'], y=fc['yhat_lower'], fill='tonexty', mode='lines', line_color='rgba(234,70,67,0.2)', name='Confidence-'))
            f1.add_trace(go.Scatter(x=ts_data['ds'], y=ts_data['y'], name='Actual', line=dict(color='#1A202C')))
            f1.add_trace(go.Scatter(x=fc['ds'], y=fc['yhat'], name='Neural', line=dict(color='#EA4643', dash='dash')))
            st.plotly_chart(f1.update_layout(template='plotly_white'), use_container_width=True)
            
            st.markdown("#### 3. Execution Benchmark (Prophet vs OLS)")
            f3 = px.line(fc, x='ds', y=['yhat', 'lr_trend'], color_discrete_map={'yhat':'#EA4643', 'lr_trend':'#718096'})
            st.plotly_chart(f3.update_layout(template='plotly_white'), use_container_width=True)

            st.markdown("#### 5. Component Analysis (Seasonality)")
            f5 = px.line(fc, x='ds', y='trend', title="Isolated Trend Extraction", color_discrete_sequence=['#EA4643'])
            st.plotly_chart(f5.update_layout(template='plotly_white'), use_container_width=True)

        with c2:
            st.markdown("#### 2. Regression Scatter w/ OLS")
            st.plotly_chart(px.scatter(ts_data, x='ds', y='y', trendline="ols", color_discrete_sequence=['#EA4643']).update_layout(template='plotly_white'), use_container_width=True)
            st.markdown("#### 4. Critical Factor Sensitivity")
            imp = pd.DataFrame({'f': features_sim, 'i': rf_model.feature_importances_[:len(features_sim)]}).sort_values('i')
            st.plotly_chart(px.bar(imp, x='i', y='f', orientation='h', color_discrete_sequence=['#EA4643']).update_layout(template='plotly_white'), use_container_width=True)
            st.markdown("#### 6. Error Residual Analysis")
            res = ts_data['y'] - lr_trend.predict(ts_data[['ordinal']])
            st.plotly_chart(px.bar(x=ts_data['ds'], y=res, title="Deviation from Trend", color_discrete_sequence=['#1A202C']).update_layout(template='plotly_white'), use_container_width=True)

    with t[1]: # 7-12
        c3, c4 = st.columns(2)
        with c3:
            st.markdown("#### 7. Cyclical Month Boxplot")
            st.plotly_chart(px.box(df, x='month', y='monthly_sales', color_discrete_sequence=['#EA4643']).update_layout(template='plotly_white'), use_container_width=True)
            st.markdown("#### 9. Velocity Momentum (MoM)")
            ts_data['v'] = ts_data['y'].pct_change()*100
            st.plotly_chart(px.area(ts_data, x='ds', y='v', color_discrete_sequence=['#EA4643']).update_layout(template='plotly_white'), use_container_width=True)
            st.markdown("#### 11. Discount Impact Distribution")
            st.plotly_chart(px.violin(df, y='monthly_sales', x='discount_percentage', box=True, color_discrete_sequence=['#EA4643']).update_layout(template='plotly_white'), use_container_width=True)
        with c4:
            st.markdown("#### 8. Smoothing (Rolling 3-Mo)")
            ts_data['ma'] = ts_data['y'].rolling(3).mean()
            st.plotly_chart(px.line(ts_data, x='ds', y=['y', 'ma']).update_layout(template='plotly_white'), use_container_width=True)
            st.markdown("#### 10. Footfall-Conversion Density")
            st.plotly_chart(px.density_contour(df, x="avg_daily_footfall", y="conversion_rate").update_layout(template='plotly_white'), use_container_width=True)
            st.markdown("#### 12. Inventory Turnover Speed")
            df['turnover'] = df['monthly_sales'] / df['inventory_level'].replace(0,1)
            st.plotly_chart(px.histogram(df, x='turnover', color_discrete_sequence=['#1A202C']).update_layout(template='plotly_white'), use_container_width=True)

    with t[2]: # 13-18
        c5, c6 = st.columns(2)
        with c5:
            st.markdown("#### 13. Portfolio Vertical Mix")
            st.plotly_chart(px.line(df_ts.groupby(['date','business_type'])['monthly_sales'].sum().reset_index(), x='date', y='monthly_sales', color='business_type').update_layout(template='plotly_white'), use_container_width=True)
            st.markdown("#### 15. Geographic Stack")
            st.plotly_chart(px.area(df_ts.groupby(['date','city'])['monthly_sales'].sum().reset_index(), x='date', y='monthly_sales', color='city').update_layout(template='plotly_white'), use_container_width=True)
            st.markdown("#### 17. City Tier Sunburst")
            st.plotly_chart(px.sunburst(df, path=['city_tier', 'city', 'business_type'], values='monthly_sales', color='monthly_sales', color_continuous_scale='Reds'), use_container_width=True)
        with c6:
            st.markdown("#### 14. Temporal Heatmap Matrix")
            p = df.pivot_table(index='year', columns='month', values='monthly_sales', aggfunc='sum')
            st.plotly_chart(px.imshow(p, color_continuous_scale='Reds').update_layout(template='plotly_white'), use_container_width=True)
            st.markdown("#### 16. Cumulative Growth Vector")
            ts_data['c'] = ts_data['y'].cumsum()
            st.plotly_chart(px.area(ts_data, x='ds', y='c', color_discrete_sequence=['#1A202C']).update_layout(template='plotly_white'), use_container_width=True)
            st.markdown("#### 18. Festival vs Baseline Lift")
            st.plotly_chart(px.pie(df, names='is_festival_season', values='monthly_sales', hole=.4, color_discrete_sequence=['#E2E8F0', '#EA4643']), use_container_width=True)

    with t[3]: # 19-25
        c7, c8 = st.columns(2)
        with c7:
            st.markdown("#### 19. 3D Market Volume Mesh")
            st.plotly_chart(go.Figure(data=[go.Mesh3d(x=df['avg_daily_footfall'], y=df['marketing_spend'], z=df['monthly_sales'], color='#EA4643', opacity=0.4)]).update_layout(height=400), use_container_width=True)
            st.markdown("#### 21. Sales Density (Sales/Sqft)")
            df['sd'] = df['monthly_sales'] / df['store_size_sqft']
            st.plotly_chart(px.scatter(df, x='store_size_sqft', y='monthly_sales', size='sd', color='sd', color_continuous_scale='Reds'), use_container_width=True)
            st.markdown("#### 23. Operation Maturity Curve")
            om = df.groupby('years_of_operation')['monthly_sales'].mean().reset_index()
            st.plotly_chart(px.line(om, x='years_of_operation', y='monthly_sales', markers=True, color_discrete_sequence=['#EA4643']), use_container_width=True)
            st.markdown("#### 25. Outlier Detection (Z-Score)")
            ts_data['z'] = (ts_data['y'] - ts_data['y'].mean()) / ts_data['y'].std()
            st.plotly_chart(px.scatter(ts_data, x='ds', y='y', color='z', color_continuous_scale='RdBu_r'), use_container_width=True)
        with c8:
            st.markdown("#### 20. Marketing ROI Scatter")
            st.plotly_chart(px.scatter(df, x='marketing_spend', y='monthly_sales', trendline="ols", color='is_festival_season').update_layout(template='plotly_white'), use_container_width=True)
            st.markdown("#### 22. Feature Correlation Heatmap")
            corr = df[features_sim].corr()
            st.plotly_chart(px.imshow(corr, color_continuous_scale='RdBu_r', text_auto=True).update_layout(height=450), use_container_width=True)
            st.markdown("#### 24. Inventory Risk vs Reward")
            st.plotly_chart(px.scatter(df, x='inventory_level', y='monthly_sales', color='customer_rating', color_continuous_scale='Reds'), use_container_width=True)

    with t[4]: # 26-31
        c9, c10 = st.columns(2)
        with c9:
            st.markdown("#### 26. Employee Efficiency Index")
            df['ee'] = df['monthly_sales'] / df['employee_count'].replace(0,1)
            eff_df = df.groupby('date')['ee'].mean().reset_index()
            st.plotly_chart(px.area(eff_df, x='date', y='ee', color_discrete_sequence=['#EA4643']), use_container_width=True)
            st.markdown("#### 28. Salary Burn vs Revenue")
            df['sb'] = (df['employee_count'] * df['avg_employee_salary'])
            st.plotly_chart(px.scatter(df, x='sb', y='monthly_sales', color='business_type').update_layout(template='plotly_white'), use_container_width=True)
            st.markdown("#### 30. Rating Impact Waterfall")
            rw = df.groupby('customer_rating')['monthly_sales'].sum().reset_index()
            st.plotly_chart(px.bar(rw, x='customer_rating', y='monthly_sales', color_discrete_sequence=['#1A202C']), use_container_width=True)
        with c10:
            st.markdown("#### 27. Growth Acceleration (Deriv)")
            ts_data['acc'] = ts_data['v'].diff()
            st.plotly_chart(px.line(ts_data, x='ds', y='acc', color_discrete_sequence=['#1A202C']).update_layout(template='plotly_white'), use_container_width=True)
            st.markdown("#### 29. Store Capacity Stress Test")
            st.plotly_chart(px.density_heatmap(df, x="store_size_sqft", y="avg_daily_footfall", z="monthly_sales", color_continuous_scale='Reds'), use_container_width=True)
            st.markdown("#### 31. Unified Sales Funnel")
            funnel_data = dict(number=[100, 70, 40], stage=["Traffic", "Conversion", "Revenue"])
            st.plotly_chart(px.funnel(funnel_data, x='number', y='stage', color_discrete_sequence=['#EA4643']), use_container_width=True)

    with t[5]: # 32-36 (Demand Forecasting Specialized)
        c11, c12 = st.columns(2)
        with c11:
            st.markdown("#### 32. ABC Analysis: Revenue Concentration")
            abc_data = df.groupby('business_type')['monthly_sales'].sum().sort_values(ascending=False).reset_index()
            abc_data['cum_percentage'] = 100 * abc_data['monthly_sales'].cumsum() / abc_data['monthly_sales'].sum()
            f32 = go.Figure()
            f32.add_trace(go.Bar(x=abc_data['business_type'], y=abc_data['monthly_sales'], name='Revenue', marker_color='#EA4643'))
            f32.add_trace(go.Scatter(x=abc_data['business_type'], y=abc_data['cum_percentage'], name='Cumulative %', yaxis='y2', line=dict(color='#1A202C')))
            f32.update_layout(yaxis2=dict(overlaying='y', side='right', range=[0, 110]), template='plotly_white')
            st.plotly_chart(f32, use_container_width=True)

            st.markdown("#### 34. Demand Volatility Index (CV)")
            # Coefficient of Variation = std / mean
            vol_df = df.groupby('business_type')['monthly_sales'].agg(['std', 'mean']).reset_index()
            vol_df['cv'] = vol_df['std'] / vol_df['mean']
            st.plotly_chart(px.bar(vol_df, x='business_type', y='cv', title="Relative Demand Fluctuation", color_discrete_sequence=['#1A202C']).update_layout(template='plotly_white'), use_container_width=True)

            st.markdown("#### 36. Inventory Strategy: Safety Stock Rec")
            # Safety Stock Estimate = Factor * StdDev of Demand
            vol_df['safety_stock'] = 1.65 * vol_df['std'] # 95% service level factor
            st.plotly_chart(px.bar(vol_df, x='business_type', y='safety_stock', title="Recommended Buffer Units", color_discrete_sequence=['#EA4643']).update_layout(template='plotly_white'), use_container_width=True)

        with c12:
            st.markdown("#### 33. Demand Seasonality Radar")
            s_data = df.groupby('month')['monthly_sales'].sum().reset_index()
            f33 = px.line_polar(s_data, r='monthly_sales', theta='month', line_close=True, color_discrete_sequence=['#EA4643'])
            f33.update_traces(fill='toself')
            st.plotly_chart(f33.update_layout(template='plotly_white'), use_container_width=True)

            st.markdown("#### 35. Lead-Lag Scatter Matrix")
            ll_df = df[['marketing_spend', 'avg_daily_footfall', 'monthly_sales', 'inventory_level']]
            st.plotly_chart(px.scatter_matrix(ll_df, dimensions=['marketing_spend', 'avg_daily_footfall', 'monthly_sales'], color='monthly_sales', color_continuous_scale='Reds').update_layout(height=500), use_container_width=True)
