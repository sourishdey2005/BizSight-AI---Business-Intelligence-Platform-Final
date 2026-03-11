# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
from datetime import datetime
import warnings
import database
import modules
import visualizations
import forecasting_module
import time
import config

warnings.filterwarnings('ignore')

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Small Business Sales & Profit Analyzer (Bizsight AI)",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# ============================================================
# INTEGRATED AUTH & AUTHORIZATION SYSTEM
# ============================================================

def show_footer():
    """Renders the centralized enterprise footer"""
    st.divider()
    st.markdown("""
    <div style='text-align: center; padding: 2rem 1rem; background: #FFFFFF; border-radius: 20px; margin-top: 40px;'>
        <div style='max-width: 800px; margin: 0 auto;'>
            <!-- Action Buttons -->
            <div style='display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; margin-bottom: 40px;'>
                <a href='https://sourishdeyportfolio.vercel.app/' target='_blank' 
                   style='background: #EA4643; color: white; text-decoration: none; font-weight: 700; 
                          padding: 15px 35px; border-radius: 15px; transition: 0.3s; box-shadow: 0 10px 20px rgba(234, 70, 67, 0.2);'>
                   👨‍💻 Developed by Sourish Dey - View Portfolio
                </a>
                <a href='https://github.com' target='_blank' 
                   style='background: #1A202C; color: white; text-decoration: none; font-weight: 700; 
                          padding: 15px 35px; border-radius: 15px; transition: 0.3s; box-shadow: 0 10px 20px rgba(0,0,0,0.1);'>
                   💻 View Repository
                </a>
            </div>
            <!-- Corporate Info -->
            <div style='border-top: 1px solid #E2E8F0; padding-top: 30px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;'>
                <p style='color: #718096; font-size: 12px; margin: 5px 0;'>Powered by Infosys Strategic Ecosystem</p>
                <p style='color: #A0AEC0; font-size: 12px; margin: 5px 0;'>© 2026 Small Business Sales & Profit Analyzer (Bizsight AI). Infrastructure secured by Supabase AWS.</p>
            </div>
            <!-- Platform Capabilities -->
            <div style='margin-top: 20px;'>
                <span style='color: #EA4643; font-weight: 800; font-size: 10px; text-transform: uppercase; letter-spacing: 2px;'>
                    48+ Visualizations • Neural Forecasting • Real-time Gating
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_integrated_auth():
    """Gated high-end Authentication & Authorization Center"""
    c1, mid, c2 = st.columns([1, 4, 1])
    with mid:
        st.image("https://upload.wikimedia.org/wikipedia/commons/9/95/Infosys_logo.svg", width=200)
        st.markdown("<h1 style='color:#1A202C; font-weight:900; font-size:42px; text-align:center;'>Small Business Sales & Profit Analyzer</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color:#EA4643; font-size:18px; font-weight:700; text-align:center; margin-top:-20px;'>(Bizsight AI)</p>", unsafe_allow_html=True)
        st.markdown("<p style='color:#718096; font-size:18px; margin-bottom:40px; text-align:center;'>Strategic Business Intelligence Gateway</p>", unsafe_allow_html=True)

        tab_l, tab_r = st.tabs(["🔒 SECURE LOGIN", "📝 ENTERPRISE REGISTRATION"])

        with tab_l:
            with st.form("main_login"):
                email = st.text_input("Operational Email ID")
                password = st.text_input("Access Security Key", type="password")
                if st.form_submit_button("VALIDATE & ENTER DASHBOARD", type="primary", use_container_width=True):
                    user = database.verify_user(email, password)
                    if user:
                        st.session_state.user = {
                            "id": user.id,
                            "email": user.email,
                            "username": user.email.split('@')[0].capitalize(),
                            "role": user.user_metadata.get('role', 'Owner')
                        }
                        st.success("✅ Credentials Verified. Syncing Digital Ecosystem...")
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error("❌ Identity Mismatch. Please verify credentials.")

        with tab_r:
            with st.form("main_register"):
                r_name = st.text_input("Authorized User Name")
                r_email = st.text_input("Corporate Email")
                r_pass = st.text_input("Master Access Key", type="password")
                r_biz = st.text_input("Legal Entity Name")
                r_role = st.selectbox("Designation", ["Owner", "Managing Director", "System Accountant"])
                
                if st.form_submit_button("PROVISION NEW ACCOUNT", type="primary", use_container_width=True):
                    if r_email and r_pass:
                        success = database.create_user(r_email, r_pass, r_role, r_biz, "HQ", "Central", "N/A", "N/A")
                        if success:
                            st.success("✅ Enterprise Provisioning Complete. Please Login.")
                        else:
                            st.error("❌ Registration Blocked. Contact System Admin.")
                    else:
                        st.warning("⚠️ Critical security fields missing.")
        
        st.caption("© 2026 Small Business Sales & Profit Analyzer (Bizsight AI) | Part of the Infosys Limited")

# AUTHENTICATION GATING
if 'user' not in st.session_state or st.session_state.user is None:
    show_integrated_auth()
    st.stop()

database.init_db()

# Main Navigation
with st.sidebar:
    # 1. Primary Logout at the very top
    if st.button("🚪 LOGOUT", type="primary", use_container_width=True, help="Terminate session and return to login gate"):
        try:
            database.supabase.auth.sign_out()
        except:
            pass
        st.session_state.clear()
        st.query_params.clear()
        st.rerun()

    st.markdown("---")
    st.image("https://upload.wikimedia.org/wikipedia/commons/9/95/Infosys_logo.svg", width=120)
    st.markdown(f"**Executive:** {st.session_state.user['username']}")
    st.caption(f"**Access Level:** {st.session_state.user['role']}")
    
    # Connection Status indicator
    if getattr(database, 'USE_SUPABASE', False):
        st.sidebar.success("📡 Cloud Engine: Connected")
    else:
        st.sidebar.warning("🔌 Local Engine: Offline Mode")
    
    st.markdown("---")
    
    st.markdown("---")
    st.markdown("### 🧭 Navigation")
    
    user_role = st.session_state.user['role']
    
    # Define available modules based on role (Requested: Dashboard, Transaction Management, Inventory Management, Advanced Analytics, Reports, Settings)
    if user_role == "Owner":
        options = ["Dashboard", "Transaction Management", "Inventory Management", "Advanced Analytics", "Demand Forecasting", "Reports", "Settings"]
    elif user_role == "Accountant":
        options = ["Dashboard", "Transaction Management", "Inventory Management", "Demand Forecasting", "Reports"]
    else: # Staff
        options = ["Dashboard", "Transaction Management", "Inventory Management"]
        
    selected_module = st.radio("Go to:", options)

    st.markdown("---")
    if st.button("🔓 End Session", type="secondary", use_container_width=True):
        st.session_state.clear()
        st.query_params.clear()
        st.rerun()

# Routing Logic
# Routing Logic
show_advanced_analytics = False
show_demand_forecasting = False

if selected_module == "Transaction Management":
    modules.data_entry_page()
    show_footer()
    st.stop()
elif selected_module == "Inventory Management":
    modules.inventory_page()
    show_footer()
    st.stop()
elif selected_module == "Reports":
    modules.reports_page()
    show_footer()
    st.stop()
elif selected_module == "Settings":
    modules.admin_page()
    show_footer()
    st.stop()
elif selected_module == "Advanced Analytics":
    show_advanced_analytics = True
    # We fall through to load data, but will skip main dashboard rendering
elif selected_module == "Demand Forecasting":
    show_demand_forecasting = True
    # We fall through to load data
elif selected_module == "Dashboard":
    # If staff/accountant, maybe show specific dashboard?
    if user_role == "Staff":
        st.title("Staff Operational Dashboard")
        st.info("Welcome back! Please navigate to Transaction Management or Inventory Management to perform your daily tasks.")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Pending Tasks", "5")
        with col2:
            st.metric("Inventory Alerts", "2", delta="Low Stock", delta_color="inverse")
        
        st.markdown("---")
        if st.button("🚪 Terminal Logout", type="secondary"):
            st.session_state.clear()
            st.query_params.clear()
            st.rerun()
        show_footer()
        st.stop()

# Logic to handle "Data Loading" for the remaining modules (Dashboard, Advanced Analytics)
# This part falls through to the rest of app.py execution


# ============================================================
# CUSTOM CSS - COMBINED STYLES
# ============================================================
st.markdown("""
<style>
    
    /* --- Core Red & White Design Tokens --- */
    :root {
        --primary: #EA4643;
        --secondary: #EA4643;
        --text-main: #1A202C;
        --text-muted: #718096;
        --bg-main: #FFFFFF;
        --bg-glass: rgba(255, 255, 255, 0.9);
        --border-glass: rgba(234, 70, 67, 0.1);
    }
    
    .stApp {
        background: var(--bg-main);
    }

    /* --- Enhanced Welcome Page Styles --- */
    .welcome-container {
        padding: 60px 20px;
        text-align: center;
        background: var(--bg-glass);
        backdrop-filter: blur(20px);
        border-radius: 40px;
        border: 1px solid var(--border-glass);
        margin-bottom: 40px;
        animation: slideInUp 1s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 20px 50px rgba(0,0,0,0.05);
    }

    .hero-image {
        width: 80%;
        display: block;
        margin: 0 auto 40px;
        border-radius: 30px;
        box-shadow: 0 40px 100px rgba(0,0,0,0.15);
        transition: 0.6s;
    }

    .hero-image:hover {
        transform: translateY(-10px) scale(1.01);
    }

    .feature-card {
        background: white;
        padding: 40px 30px;
        border-radius: 25px;
        border: 1px solid #F1F5F9;
        text-align: center;
        transition: all 0.4s ease;
        height: 100%;
        box-shadow: 0 10px 30px rgba(0,0,0,0.02);
    }

    .feature-card:hover {
        transform: translateY(-15px);
        border-color: var(--primary);
        box-shadow: 0 20px 50px rgba(234, 70, 67, 0.1);
    }

    .feature-icon-box {
        width: 70px;
        height: 70px;
        background: #FFEDED;
        color: var(--primary);
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 30px;
        margin: 0 auto 25px;
        transition: 0.4s;
    }

    .feature-card:hover .feature-icon-box {
        transform: scale(1.1) rotate(5deg);
        background: var(--primary);
        color: white;
    }

    .guide-box {
        background: var(--primary);
        color: white;
        padding: 40px;
        border-radius: 30px;
        margin-top: 50px;
        text-align: left;
    }

    .guide-box h3 {
        color: var(--primary);
        margin-bottom: 25px;
        font-size: 24px;
    }

    .step-list {
        list-style: none;
        padding: 0;
    }

    .step-list li {
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 15px;
        font-size: 16px;
    }

    .step-list li::before {
        content: '\u2713';
        color: var(--primary);
        font-weight: 900;
        background: rgba(234, 70, 67, 0.1);
        width: 25px;
        height: 25px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        font-size: 12px;
    }

    /* --- Flip Card Styles --- */
    .flip-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        justify-content: center;
        margin-top: 40px;
    }

    .flip-card {
        background-color: transparent;
        width: 200px;
        height: 250px;
        perspective: 1000px;
    }

    .flip-card-inner {
        position: relative;
        width: 100%;
        height: 100%;
        text-align: center;
        transition: transform 0.8s;
        transform-style: preserve-3d;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
        border-radius: 20px;
    }

    .flip-card:hover .flip-card-inner {
        transform: rotateY(180deg);
    }

    .flip-card-front, .flip-card-back {
        position: absolute;
        width: 100%;
        height: 100%;
        -webkit-backface-visibility: hidden;
        backface-visibility: hidden;
        border-radius: 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 15px;
    }

    .flip-card-front {
        background-color: #FFFFFF;
        color: #1A202C;
        border: 2px solid #FFEDED;
    }

    .flip-card-back {
        background-color: var(--primary);
        color: white;
        transform: rotateY(180deg);
    }

    .flip-icon {
        font-size: 40px;
        margin-bottom: 15px;
    }

    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(50px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Metric Cards - Existing Improvements */
    .metric-card-v2 {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        color: #1F2937;
        border: 1px solid #E5E7EB;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card-v2::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 5px;
        height: 100%;
        background: linear-gradient(to bottom, var(--primary), #FFEDED);
    }
    
    .metric-card-v2:hover {
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        transform: translateY(-5px);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# COLOR PALETTE - COMBINED
# ============================================================
COLOR_PALETTE = {
    'primary': '#EA4643',
    'secondary': '#1A202C',
    'warning': '#F59E0B',
    'danger': '#EA4643',
    'info': '#718096',
    'dark': '#1A202C',
    'light': '#FFFFFF',
    'success': '#EA4643',
    'purple': '#EA4643',
    'pink': '#EA4643',
    'cyan': '#EA4643',
    'orange': '#EA4643',
    'indigo': '#EA4643',
    'teal': '#EA4643'
}

PLOTLY_COLORS = [
    '#EA4643', '#1A202C', '#718096', '#E2E8F0', '#F1F5F9',
    '#EA4643', '#1A202C', '#718096', '#E2E8F0', '#F1F5F9'
]

# ============================================================
# LOAD MODEL - FROM FIRST CODE
# ============================================================
@st.cache_resource
def load_model():
    # Monkey patch for scikit-learn version compatibility (Fixes _RemainderColsList error)
    import sklearn.compose._column_transformer
    if not hasattr(sklearn.compose._column_transformer, '_RemainderColsList'):
        class _RemainderColsList(list):
            pass
        sklearn.compose._column_transformer._RemainderColsList = _RemainderColsList

    try:
        model = joblib.load("business_sales_profit_pipeline.pkl")
        return model
    except FileNotFoundError:
        st.error("Model file not found. Using demonstration mode.")
        return None
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None

model = load_model()

# ============================================================
# REQUIRED SCHEMA - FROM FIRST CODE
# ============================================================
if model:
    REQUIRED_COLUMNS = model.feature_names_in_.tolist()
else:
    # Default columns if model is not available
    REQUIRED_COLUMNS = [
        "city_tier", "customer_rating", "electricity_cost", "inventory_level",
        "avg_employee_salary", "conversion_rate", "is_festival_season",
        "avg_transaction_value", "avg_daily_footfall", "rent_cost",
        "supplier_cost", "discount_percentage", "business_type", "city",
        "store_size_sqft", "logistics_cost", "years_of_operation",
        "profit_margin", "marketing_roi", "employee_efficiency",
        "marketing_spend", "employee_count"
    ]

DEFAULTS = {
    "city_tier": 1,
    "customer_rating": 4.0,
    "electricity_cost": 8000,
    "inventory_level": 500,
    "avg_employee_salary": 20000,
    "conversion_rate": 0.2,
    "is_festival_season": 0,
    "avg_transaction_value": 900,
    "avg_daily_footfall": 200,
    "rent_cost": 30000,
    "supplier_cost": 50000,
    "discount_percentage": 10,
    "business_type": "General",
    "city": "Unknown",
    "store_size_sqft": 1200,
    "logistics_cost": 15000,
    "years_of_operation": 5,
    "profit_margin": 0.2,
    "marketing_roi": 2.0,
    "employee_efficiency": 50000,
    "marketing_spend": 50000,
    "employee_count": 10,
    "month": 1,
    "year": 2024,
    "monthly_sales": 0
}

def align_schema(df):
    """Ensure the dataframe has all required columns without dropping existing ones"""
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = DEFAULTS.get(col, 0)
    return df

# ============================================================
# SIDEBAR - COMBINED FROM BOTH CODES
# ============================================================
# Sidebar branding removed as per request to eliminate redundant 'blank' or 'duplicate' sections.

st.sidebar.markdown("### Data Upload")
uploaded_file = st.sidebar.file_uploader(
    "Upload business dataset",
    type=["csv", "xlsx"],
    help="Upload CSV or Excel file containing business data"
)

# REMOVED: The default checkbox that was loading sample data automatically
# Now users must explicitly choose an option
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Data Source Selection")

# Use radio buttons to make data source selection explicit
data_source = st.sidebar.radio(
    "Choose data source:",
    ["Upload your own file", "Use sample data (100K records)", "Use advanced sample dataset (50K records)"],
    index=0,
    help="Select how you want to load data for analysis"
)

# Initialize session state from second code
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'df_raw' not in st.session_state:
    st.session_state.df_raw = None
if 'df' not in st.session_state:
    st.session_state.df = None

# ============================================================
# HEADER - SHOW WELCOME MESSAGE UNTIL DATA IS LOADED
# ============================================================
st.markdown("<h1 class='main-header'>Small Business Sales & Profit Analyzer (Bizsight AI)</h1>", unsafe_allow_html=True)

# Check if data is loaded
data_loaded = False
df_raw = None
df = None

# ============================================================
# LOAD AND PROCESS DATA - COMBINED FROM BOTH CODES
# ============================================================
@st.cache_data
def load_data(file=None, sample=False, advanced_sample=False):
    """Load data from uploaded file or generate sample data"""
    if advanced_sample:
        # Advanced sample data from second code
        np.random.seed(42)
        n_samples = 50000
        
        sample_data = {
            'business_id': [f'BUS_{i:06d}' for i in range(n_samples)],
            'city': np.random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 
                                     'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow'], n_samples),
            'state': np.random.choice(['Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'West Bengal',
                                      'Telangana', 'Gujarat', 'Rajasthan', 'Uttar Pradesh'], n_samples),
            'region': np.random.choice(['North', 'South', 'East', 'West', 'Central'], n_samples),
            'city_tier': np.random.choice([1, 2, 3], n_samples, p=[0.3, 0.4, 0.3]),
            'business_type': np.random.choice(['Retail', 'Restaurant', 'Services', 'Manufacturing', 
                                              'E-commerce', 'Healthcare', 'Education', 'Entertainment'], n_samples),
            'years_of_operation': np.random.randint(1, 30, n_samples),
            'store_size_sqft': np.random.randint(500, 10000, n_samples),
            'employee_count': np.random.randint(5, 200, n_samples),
            'employee_efficiency': np.random.randint(20000, 200000, n_samples),
            'avg_employee_salary': np.random.randint(20000, 80000, n_samples),
            'avg_daily_footfall': np.random.randint(50, 2000, n_samples),
            'conversion_rate': np.random.uniform(0.05, 0.5, n_samples),
            'avg_transaction_value': np.random.randint(500, 5000, n_samples),
            'customer_rating': np.random.uniform(2.5, 5.0, n_samples),
            'discount_percentage': np.random.uniform(0, 40, n_samples),
            'rent_cost': np.random.randint(10000, 200000, n_samples),
            'electricity_cost': np.random.randint(5000, 30000, n_samples),
            'logistics_cost': np.random.randint(5000, 50000, n_samples),
            'supplier_cost': np.random.randint(20000, 200000, n_samples),
            'inventory_level': np.random.randint(1000, 100000, n_samples),
            'marketing_spend': np.random.randint(10000, 300000, n_samples),
            'marketing_roi': np.random.uniform(1.0, 5.0, n_samples),
            'is_festival_season': np.random.choice([0, 1], n_samples, p=[0.8, 0.2]),
            'profit_margin': np.random.uniform(-0.1, 0.4, n_samples),
            'monthly_sales': np.random.randint(100000, 2000000, n_samples),
            'operational_cost': np.random.randint(50000, 500000, n_samples),
            'monthly_revenue': np.random.randint(150000, 2500000, n_samples),
            'sales_per_sqft': np.random.randint(100, 2000, n_samples),
            'profit_per_employee': np.random.randint(-5000, 50000, n_samples),
            'cost_to_sales_ratio': np.random.uniform(0.3, 0.8, n_samples),
            'employee_productivity': np.random.randint(10000, 150000, n_samples),
            'risk_category': np.random.choice(['Low', 'Medium', 'High'], n_samples, p=[0.5, 0.3, 0.2]),
            'business_size': np.random.choice(['Small', 'Medium', 'Large'], n_samples, p=[0.4, 0.4, 0.2])
        }
        
        df = pd.DataFrame(sample_data)
        df['profit'] = df['monthly_sales'] * df['profit_margin']
        df['total_cost'] = df['operational_cost'] + df['employee_count'] * df['avg_employee_salary'] / 12
        df['gross_margin'] = (df['monthly_revenue'] - df['operational_cost']) / df['monthly_revenue'].replace(0, 1)
        df['inventory_turnover'] = df['monthly_sales'] / df['inventory_level'].replace(0, 1)
        df['employee_contribution'] = df['profit_per_employee'] * df['employee_count']
        df['marketing_efficiency'] = df['monthly_sales'] / df['marketing_spend'].replace(0, 1)
        df['roi_category'] = pd.cut(df['marketing_roi'], bins=[0, 1.5, 3, 10], labels=['Low', 'Medium', 'High'])
        
    elif sample:
        # Original sample data from first code
        np.random.seed(42)
        n_samples = 100000
        
        sample_data = {
            "city_tier": np.random.choice([1, 2, 3], n_samples, p=[0.4, 0.4, 0.2]),
            "customer_rating": np.random.uniform(3.0, 5.0, n_samples),
            "electricity_cost": np.random.randint(5000, 15000, n_samples),
            "inventory_level": np.random.randint(100, 5000, n_samples),
            "avg_employee_salary": np.random.randint(15000, 40000, n_samples),
            "conversion_rate": np.random.uniform(0.1, 0.4, n_samples),
            "is_festival_season": np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
            "avg_transaction_value": np.random.randint(500, 2000, n_samples),
            "avg_daily_footfall": np.random.randint(50, 500, n_samples),
            "rent_cost": np.random.randint(10000, 50000, n_samples),
            "supplier_cost": np.random.randint(20000, 100000, n_samples),
            "discount_percentage": np.random.randint(0, 30, n_samples),
            "business_type": np.random.choice(["Retail", "Restaurant", "Services", "Manufacturing", "E-commerce"], n_samples),
            "city": np.random.choice(["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad"], n_samples),
            "store_size_sqft": np.random.randint(500, 5000, n_samples),
            "logistics_cost": np.random.randint(5000, 30000, n_samples),
            "years_of_operation": np.random.randint(1, 20, n_samples),
            "profit_margin": np.random.uniform(0.1, 0.4, n_samples),
            "marketing_roi": np.random.uniform(1.5, 4.0, n_samples),
            "employee_efficiency": np.random.randint(20000, 100000, n_samples),
            "marketing_spend": np.random.randint(10000, 200000, n_samples),
            "employee_count": np.random.randint(5, 50, n_samples),
            "month": np.random.randint(1, 13, n_samples),
            "year": np.random.choice([2022, 2023, 2024], n_samples),
        }
        
        df = pd.DataFrame(sample_data)
    else:
        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            return pd.DataFrame()
    
    # Handle missing values robustly
    df = df.ffill()
    
    # Fill remaining NaNs with 0 only for numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)
    
    # Fill remaining NaNs for non-numeric columns
    for col in df.select_dtypes(exclude=['number']).columns:
        if df[col].isnull().any():
            if hasattr(df[col], 'cat'): # Categorical
                if 'Unknown' not in df[col].cat.categories:
                    df[col] = df[col].cat.add_categories(['Unknown'])
                df[col] = df[col].fillna('Unknown')
            else:
                df[col] = df[col].fillna('Unknown')
    
    return df

# Load data based on user selection
if data_source == "Upload your own file":
    if uploaded_file is not None:
        df_raw = load_data(uploaded_file)
        if df_raw is not None and not df_raw.empty:
            data_loaded = True
            st.sidebar.success("✅ Your data has been loaded successfully!")
        else:
            st.sidebar.warning("⚠️ Please upload a valid dataset file")
    else:
        # Show welcome message when no file is uploaded
        # Show welcome message when no file is uploaded
        st.markdown("<img src='https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=2070' class='hero-image'>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class='welcome-container'>
            <h2 style='font-size: 36px; font-weight: 900; color: #1A202C;'>Welcome to BizSight AI! 🚀</h2>
            <p style='font-size: 18px; color: #718096; margin-bottom: 20px;'>
                Your comprehensive Business Intelligence Platform for data-driven decision making
            </p>
            <p style='font-size: 16px; color: #718096; margin-bottom: 20px;'>
                To get started, follow these tactical deployment stages:
            </p>
            
        <div class='flip-grid'>
            <div class='flip-card'>
                <div class='flip-card-inner'>
                    <div class='flip-card-front'>
                        <div class='flip-icon'>🧭</div>
                        <h4 style='font-weight:700;'>Navigation</h4>
                    </div>
                    <div class='flip-card-back'>
                        <p style='font-size:14px;'>Open the navigation sidebar on the left to access all modules.</p>
                    </div>
                </div>
            </div>
            <div class='flip-card'>
                <div class='flip-card-inner'>
                    <div class='flip-card-front'>
                        <div class='flip-icon'>📤</div>
                        <h4 style='font-weight:700;'>Data Ingress</h4>
                    </div>
                    <div class='flip-card-back'>
                        <p style='font-size:14px;'>Upload your corporate CSV or Excel dataset securely.</p>
                    </div>
                </div>
            </div>
            <div class='flip-card'>
                <div class='flip-card-inner'>
                    <div class='flip-card-front'>
                        <div class='flip-icon'>🏢</div>
                        <h4 style='font-weight:700;'>Sample Assets</h4>
                    </div>
                    <div class='flip-card-back'>
                        <p style='font-size:14px;'>Alternatively, select a high-scale sample dataset to explore.</p>
                    </div>
                </div>
            </div>
            <div class='flip-card'>
                <div class='flip-card-inner'>
                    <div class='flip-card-front'>
                        <div class='flip-icon'>🔍</div>
                        <h4 style='font-weight:700;'>Intelligence</h4>
                    </div>
                    <div class='flip-card-back'>
                        <p style='font-size:14px;'>Apply granular filters to isolate key growth metrics.</p>
                    </div>
                </div>
            </div>
            <div class='flip-card'>
                <div class='flip-card-inner'>
                    <div class='flip-card-front'>
                        <div class='flip-icon'>🚀</div>
                        <h4 style='font-weight:700;'>Simulation</h4>
                    </div>
                    <div class='flip-card-back'>
                        <p style='font-size:14px;'>Launch predictive simulations to forecast profit margins.</p>
                    </div>
                </div>
            </div>
        </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show feature highlights
        st.markdown("<h2 style='text-align:center; font-weight:900; font-size:32px; margin-bottom:40px;'>Ecosystem Capabilities</h2>", unsafe_allow_html=True)
        
        f_col1, f_col2, f_col3 = st.columns(3)
        
        with f_col1:
            st.markdown("""
            <div class='feature-card'>
                <div class='feature-icon-box'>📊</div>
                <h4 style='font-weight:800; font-size:20px; margin-bottom:15px;'>48+ Visualizations</h4>
                <p style='font-size:14px; color:#718096;'>Comprehensive charts and graphs for deep analysis.</p>
            </div>
            """, unsafe_allow_html=True)
            
        with f_col2:
            st.markdown("""
            <div class='feature-card'>
                <div class='feature-icon-box'>🤖</div>
                <h4 style='font-weight:800; font-size:20px; margin-bottom:15px;'>Predictive Analytics</h4>
                <p style='font-size:14px; color:#718096;'>Machine learning models for profit forecasting.</p>
            </div>
            """, unsafe_allow_html=True)
            
        with f_col3:
            st.markdown("""
            <div class='feature-card'>
                <div class='feature-icon-box'>📈</div>
                <h4 style='font-weight:800; font-size:20px; margin-bottom:15px;'>Real-time Simulation</h4>
                <p style='font-size:14px; color:#718096;'>Test business scenarios with instant results.</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<h2 style='text-align:center; font-weight:900; font-size:32px; margin: 60px 0 40px;'>Strategic Quick Actions</h2>", unsafe_allow_html=True)
        
        qa_col1, qa_col2, qa_col3 = st.columns(3)
        with qa_col1:
            if st.button(":bar_chart: Launch Sales Audit", use_container_width=True):
                st.info("Please upload data to begin the audit.")
        with qa_col2:
            if st.button(":money_with_wings: Profit Simulation", use_container_width=True):
                st.info("Simulations require a loaded dataset.")
        with qa_col3:
            if st.button(":shield: Risk Shield Check", use_container_width=True):
                st.info("Load data to evaluate your enterprise risk profile.")
        
        # Stop execution if no data is loaded
        st.stop()

elif data_source == "Use sample data (100K records)":
    df_raw = load_data(sample=True)
    data_loaded = True
    st.sidebar.success("✅ Sample data with 100,000 records loaded")

elif data_source == "Use advanced sample dataset (50K records)":
    df_raw = load_data(sample=True, advanced_sample=True)
    data_loaded = True
    st.sidebar.success("✅ Advanced sample data with 50,000 records loaded")

# Check if data was loaded successfully
if not data_loaded or df_raw is None or df_raw.empty:
    st.error("❌ No data loaded. Please check your selection or upload a valid file.")
    st.stop()

# Process data from first code
df = align_schema(df_raw.copy())

# Calculate monthly_sales ONLY if not present
if "monthly_sales" not in df.columns or df["monthly_sales"].isna().all():
    df["monthly_sales"] = (
        df["avg_daily_footfall"] * df["conversion_rate"] * df["avg_transaction_value"] * 30
    )

# Add derived metrics from first code
df["sales_per_sqft"] = df["monthly_sales"] / df["store_size_sqft"].replace(0, 1)
df["sales_per_employee"] = df["monthly_sales"] / df["employee_count"].replace(0, 1)
df["operating_cost"] = df["rent_cost"] + df["electricity_cost"] + df["logistics_cost"] + df["supplier_cost"]
df["profit_per_employee"] = df["monthly_sales"] * df["profit_margin"] / df["employee_count"].replace(0, 1)
df["cost_to_sales_ratio"] = df["operating_cost"] / df["monthly_sales"].replace(0, 1)
df["roi_per_employee"] = df["employee_efficiency"] / df["avg_employee_salary"].replace(0, 1)

# Add derived metrics from second code if columns exist
if 'operational_cost' in df_raw.columns and 'monthly_revenue' in df_raw.columns:
    df['gross_margin'] = (df_raw['monthly_revenue'] - df_raw['operational_cost']) / df_raw['monthly_revenue'].replace(0, 1)
if 'inventory_level' in df_raw.columns:
    df['inventory_turnover'] = df['monthly_sales'] / df_raw['inventory_level'].replace(0, 1)
if 'employee_productivity' in df_raw.columns:
    df['employee_productivity'] = df_raw['employee_productivity']
if 'profit_per_employee' in df_raw.columns:
    df['profit_per_employee_raw'] = df_raw['profit_per_employee']

# Model prediction from first code
if model:
    df["predicted_profit"] = model.predict(df[REQUIRED_COLUMNS])
else:
    # Generate synthetic predictions for demonstration
    np.random.seed(42)
    base_profit = df["monthly_sales"] * df["profit_margin"] - df["operating_cost"] - df["employee_count"] * df["avg_employee_salary"]
    noise = np.random.normal(0, 0.1 * abs(base_profit).mean(), len(df))
    df["predicted_profit"] = np.maximum(base_profit + noise, 0)  # Ensure non-negative for visualization

df["risk_band"] = pd.qcut(df["predicted_profit"], 3, labels=["Low", "Medium", "High"])

# Add advanced scores from second code
df['profitability_score'] = (df['profit_margin'].clip(-0.5, 0.5) * 0.4 + 
                            (df['customer_rating'].clip(1, 5) / 5) * 0.3 + 
                            (1 - df['cost_to_sales_ratio'].clip(0, 1)) * 0.3) * 100

if 'employee_efficiency' in df.columns:
    emp_eff_norm = df['employee_efficiency'] / df['employee_efficiency'].replace(0, 1).max()
else:
    emp_eff_norm = 0.5

if 'sales_per_sqft' in df.columns:
    sales_sqft_norm = df['sales_per_sqft'] / df['sales_per_sqft'].replace(0, 1).max()
else:
    sales_sqft_norm = 0.5

if 'inventory_turnover' in df.columns:
    inv_turn_norm = df['inventory_turnover'] / df['inventory_turnover'].replace(0, 1).max()
else:
    inv_turn_norm = 0.5

df['efficiency_score'] = (emp_eff_norm * 0.4 +
                         sales_sqft_norm * 0.3 +
                         inv_turn_norm * 0.3) * 100

df['growth_potential'] = ((df['years_of_operation'].clip(0, 30) / 30) * 0.3 +
                         (df['city_tier'].clip(1, 3) / 3) * 0.2 +
                         (df['employee_count'].clip(1, 200) / 200) * 0.3 +
                         (df['store_size_sqft'].clip(500, 10000) / 10000) * 0.2) * 100

# Create performance tiers from second code
if 'predicted_profit' in df.columns and 'monthly_sales' in df.columns and 'employee_efficiency' in df.columns:
    performance_score = (df['predicted_profit'].rank(pct=True) * 0.4 + 
                       df['monthly_sales'].rank(pct=True) * 0.3 + 
                       df['employee_efficiency'].rank(pct=True) * 0.3)
    df['performance_tier'] = pd.qcut(performance_score, 5, 
                                    labels=['Poor', 'Below Avg', 'Average', 'Good', 'Excellent'])
else:
    df['performance_tier'] = 'Average'

# Store in session state for second code features
st.session_state.data_loaded = True
st.session_state.df_raw = df_raw
st.session_state.df = df

# ============================================================
# SIDEBAR FILTERS (ONLY SHOW WHEN DATA IS LOADED)
# ============================================================
if data_loaded:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 Data Filters")
    
    # Risk Level Filter
    if 'risk_band' in df.columns:
        st.sidebar.markdown("##### Risk Level Filter")
        risk_filter = st.sidebar.multiselect(
            "Select Risk Levels",
            ["Low", "Medium", "High"],
            default=["Low", "Medium", "High"],
            key="risk_filter"
        )
    else:
        risk_filter = ["Low", "Medium", "High"]
    
    # Business Type Filter
    if 'business_type' in df.columns:
        st.sidebar.markdown("##### Business Type Filter")
        business_types = ["All"] + sorted(df['business_type'].unique().tolist())
        business_filter = st.sidebar.multiselect(
            "Select Business Types",
            business_types,
            default=["All"],
            key="business_filter"
        )
    else:
        business_filter = ["All"]
    
    # Additional filters from second code
    if 'region' in df.columns:
        st.sidebar.markdown("##### Region Filter")
        region_filter = st.sidebar.multiselect(
            "Select Regions",
            ["All"] + sorted(df['region'].unique().tolist()),
            default=["All"],
            key="region_filter"
        )
    else:
        region_filter = ["All"]
    
    if 'performance_tier' in df.columns:
        st.sidebar.markdown("##### Performance Tier Filter")
        performance_filter = st.sidebar.multiselect(
            "Select Performance Tiers",
            ["All"] + sorted(df['performance_tier'].unique().tolist()),
            default=["All"],
            key="performance_filter"
        )
    else:
        performance_filter = ["All"]
    
    # Apply filters
    if 'risk_band' in df.columns and risk_filter:
        df = df[df['risk_band'].isin(risk_filter)]
    if 'business_type' in df.columns and business_filter and "All" not in business_filter:
        df = df[df['business_type'].isin(business_filter)]
    if 'region' in df.columns and region_filter and "All" not in region_filter:
        df = df[df['region'].isin(region_filter)]
    if 'performance_tier' in df.columns and performance_filter and "All" not in performance_filter:
        df = df[df['performance_tier'].isin(performance_filter)]

# ============================================================
# EXECUTIVE SUMMARY - FROM FIRST CODE (ONLY SHOW WHEN DATA IS LOADED)
# ============================================================
if data_loaded:
    st.markdown("Advanced analytics and predictive insights for business optimization")
    st.divider()

    # Calculate metrics from first code
    avg_profit = df["predicted_profit"].mean()
    avg_sales = df["monthly_sales"].mean()
    risk_percentage = (df["risk_band"] == 'High').mean() * 100 if 'risk_band' in df.columns else 0
    total_records = len(df)
    profit_margin_val = (df['predicted_profit'].sum() / df['monthly_sales'].sum() * 100) if df['monthly_sales'].sum() > 0 else 0
    avg_roi = df['marketing_roi'].mean() if 'marketing_roi' in df.columns else 2.0
    inventory_turnover = (df['monthly_sales'].sum() / df['inventory_level'].sum()) if df['inventory_level'].sum() > 0 else 0
    employee_productivity = df['employee_efficiency'].mean() if 'employee_efficiency' in df.columns else 50000

    # Additional metrics from second code
    avg_rating = df['customer_rating'].mean() if 'customer_rating' in df.columns else 3.0
    avg_conversion = df['conversion_rate'].mean() * 100 if 'conversion_rate' in df.columns else 20
    avg_efficiency = df['employee_efficiency'].mean() if 'employee_efficiency' in df.columns else 50000
    high_performance_pct = (df['performance_tier'].isin(['Good', 'Excellent'])).mean() * 100 if 'performance_tier' in df.columns else 0
    profitability_score_avg = df['profitability_score'].mean() if 'profitability_score' in df.columns else 50
    efficiency_score_avg = df['efficiency_score'].mean() if 'efficiency_score' in df.columns else 50
    growth_potential_avg = df['growth_potential'].mean() if 'growth_potential' in df.columns else 50
    inventory_turnover_avg = df['inventory_turnover'].mean() if 'inventory_turnover' in df.columns else 1.5

    if show_advanced_analytics:
        st.title("🚀 Advanced Analytics Suite")
        
        c1, c2 = st.columns([5, 1])
        with c2:
            if st.button("🚪 Logout Now", key="adv_logout", use_container_width=True):
                st.session_state.clear()
                st.query_params.clear()
                st.rerun()

        visualizations.show_advanced_visualizations(df)
        visualizations.show_geographic_and_premium_analytics(df)
        visualizations.show_3d_and_immersive_analytics(df)
        visualizations.show_comprehensive_bi_suite(df)
        st.sidebar.info("You are viewing the Advanced Analytics Suite. Other modules are hidden.")
        st.stop()

    if show_demand_forecasting:
        forecasting_module.show_forecasting_section(df)
        st.sidebar.info("You are viewing Demand Forecasting & Time Series Analysis.")
        st.stop()
        
    header_col1, header_col2 = st.columns([5, 1])
    with header_col1:
        st.markdown("<h2 class='section-header'>Executive Dashboard</h2>", unsafe_allow_html=True)
    with header_col2:
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            st.session_state.clear()
            st.query_params.clear()
            st.rerun()

    # Row 1: Main Metrics from first code
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class='metric-card-v2'>
            <div class='metric-value'>Rs.{avg_profit:,.0f}</div>
            <div class='metric-label'>Average Monthly Profit</div>
            <div style='font-size: 0.85rem; color: #718096; margin-top: 0.5rem;'>
                :arrow_up: 12.5% from last quarter
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='metric-card-v2'>
            <div class='metric-value'>Rs.{avg_sales:,.0f}</div>
            <div class='metric-label'>Average Monthly Sales</div>
            <div style='font-size: 0.85rem; color: #718096; margin-top: 0.5rem;'>
                :arrow_up: 18.2% from last quarter
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class='metric-card-v2'>
            <div class='metric-value'>{risk_percentage:.1f}%</div>
            <div class='metric-label'>High Risk Businesses</div>
            <div style='font-size: 0.85rem; color: #718096; margin-top: 0.5rem;'>
                :arrow_down: 5.1% from last quarter
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class='metric-card-v2'>
            <div class='metric-value'>{total_records:,}</div>
            <div class='metric-label'>Total Organizations</div>
            <div style='font-size: 0.85rem; color: #EA4643; margin-top: 0.5rem;'>
                :arrow_up: 25,000 new entries
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Row 2: Additional Metrics from first code
    col5, col6, col7, col8 = st.columns(4)

    with col5:
        st.markdown(f"""
        <div class='metric-card' style='border-left: 4px solid #8B5CF6;'>
            <div class='metric-value'>{profit_margin_val:.1f}%</div>
            <div class='metric-label'>Overall Profit Margin</div>
            <div style='font-size: 0.85rem; color: #6B7280; margin-top: 0.5rem;'>
                Target: 25%
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown(f"""
        <div class='metric-card' style='border-left: 4px solid #06B6D4;'>
            <div class='metric-value'>{avg_roi:.2f}x</div>
            <div class='metric-label'>Avg Marketing ROI</div>
            <div style='font-size: 0.85rem; color: #6B7280; margin-top: 0.5rem;'>
                Industry Avg: 2.5x
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col7:
        st.markdown(f"""
        <div class='metric-card' style='border-left: 4px solid #F59E0B;'>
            <div class='metric-value'>{inventory_turnover:.1f}</div>
            <div class='metric-label'>Inventory Turnover</div>
            <div style='font-size: 0.85rem; color: #6B7280; margin-top: 0.5rem;'>
                Target: 2.5
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col8:
        st.markdown(f"""
        <div class='metric-card' style='border-left: 4px solid #EA4643;'>
            <div class='metric-value'>₹{employee_productivity:,.0f}</div>
            <div class='metric-label'>Avg Employee Efficiency</div>
            <div style='font-size: 0.85rem; color: #718096; margin-top: 0.5rem;'>
                ▲ 8.3% YoY
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Calculate metric values from dataset
    # 1. Gross Profit Margin
    gross_profit_margin = df['gross_margin'].mean() * 100 if 'gross_margin' in df.columns else (profit_margin_val * 1.5)
    # 2. Operating Expense Ratio
    operating_expense_ratio = (df['operational_cost'].sum() / df['monthly_sales'].sum() * 100) if 'operational_cost' in df.columns and df['monthly_sales'].sum() > 0 else 42.3
    # 3. Net Profit Margin
    net_profit_margin = profit_margin_val
    # 4. EBITDA
    ebitda_val = df['predicted_profit'].sum() * 1.25 if 'predicted_profit' in df.columns else (avg_profit * total_records * 1.2)
    # 5. Cash Flow Coverage
    cash_flow_coverage = (df['predicted_profit'].mean() / (df['rent_cost'].mean() + 1)) * 5 if 'rent_cost' in df.columns else 1.8
    
    # Financial Stability (Simulated from actual data pointers)
    current_ratio = 1.2 + (df['inventory_level'].mean() / 50000) if 'inventory_level' in df.columns else 1.5
    quick_ratio = current_ratio * 0.8
    debt_equity = 0.2 + (df['risk_band'] == 'High').mean() if 'risk_band' in df.columns else 0.4
    roa = (net_profit_margin * 0.8) + 5
    roe = roa * 1.6
    
    # Customer (Simulated from actual data pointers)
    cac_val = df['marketing_spend'].mean() / (df['avg_daily_footfall'].mean() * 0.1 + 10) if 'marketing_spend' in df.columns else 450
    ltv_val = df['avg_transaction_value'].mean() * 6 if 'avg_transaction_value' in df.columns else 12500
    churn_rate = (1 - df['customer_rating'].mean() / 5) * 15 if 'customer_rating' in df.columns else 4.2
    nps_score = (df['customer_rating'].mean() - 2) * 25 if 'customer_rating' in df.columns else 72
    market_share = (df['monthly_sales'].mean() / 2000000) * 20 if 'monthly_sales' in df.columns else 14.5
    
    # Operational (Simulated from actual data pointers)
    inv_turnover_days = 365 / (inventory_turnover + 0.1)
    order_fulfillment = 92 + (df['conversion_rate'].mean() * 15) if 'conversion_rate' in df.columns else 98.5
    lead_time = 15 - (df['city_tier'].mean() * 2) if 'city_tier' in df.columns else 12
    utilization = 75 + (df['employee_efficiency'].mean() / 250000 * 20) if 'employee_efficiency' in df.columns else 85
    defect_rate = 2.5 - (df['customer_rating'].mean() * 0.4) if 'customer_rating' in df.columns else 0.8
    
    # Growth (Simulated from actual data pointers)
    rev_growth = 15 + (df['is_festival_season'].mean() * 20) if 'is_festival_season' in df.columns else 22.4
    new_prod_rev = 10 + (df['years_of_operation'].mean() / 2) if 'years_of_operation' in df.columns else 15
    digital_sales = 25 + (df['city_tier'].mean() * 10) if 'city_tier' in df.columns else 35
    emp_sat = (df['customer_rating'].mean() * 0.8) + 0.5 if 'customer_rating' in df.columns else 4.2
    sustainability = 70 + (df['years_of_operation'].mean() * 0.5) if 'years_of_operation' in df.columns else 88

    st.markdown("### 📊 Expanded Key Performance Indicators")
    
    # Financial Health
    st.caption("Financial Performance")
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)
    with kpi_col1:
        st.metric("Gross Profit Margin", f"{gross_profit_margin:.1f}%", f"{gross_profit_margin - 32.5:.1f}%")
    with kpi_col2:
        st.metric("Operating Expense Ratio", f"{operating_expense_ratio:.1f}%", f"{45 - operating_expense_ratio:.1f}%", delta_color="inverse")
    with kpi_col3:
        st.metric("Net Profit Margin", f"{net_profit_margin:.1f}%", f"{net_profit_margin - 2.0:.1f}%")
    with kpi_col4:
        st.metric("EBITDA", f"₹{ebitda_val/1000000:.1f}M", "+8.3%")
    with kpi_col5:
        st.metric("Cash Flow Coverage", f"{cash_flow_coverage:.1f}x", "+0.2x")

    kpi_col6, kpi_col7, kpi_col8, kpi_col9, kpi_col10 = st.columns(5)
    with kpi_col6:
        st.metric("Current Ratio", f"{current_ratio:.2f}", "+0.1")
    with kpi_col7:
        st.metric("Quick Ratio", f"{quick_ratio:.2f}", "-0.05", delta_color="inverse")
    with kpi_col8:
        st.metric("Debt-to-Equity", f"{debt_equity:.2f}", "-0.02", delta_color="inverse")
    with kpi_col9:
        st.metric("Return on Assets", f"{roa:.1f}%", "+1.1%")
    with kpi_col10:
        st.metric("Return on Equity", f"{roe:.1f}%", "+2.3%")

    # Customer & Market
    st.caption("Customer & Market Insights")
    kpi_col11, kpi_col12, kpi_col13, kpi_col14, kpi_col15 = st.columns(5)
    with kpi_col11:
        st.metric("Cust. Acquisition Cost", f"₹{cac_val:,.0f}", f"-₹{cac_val*0.05:,.0f}", delta_color="inverse")
    with kpi_col12:
        st.metric("Lifetime Value", f"₹{ltv_val:,.0f}", f"+₹{ltv_val*0.04:,.0f}")
    with kpi_col13:
        st.metric("Churn Rate", f"{churn_rate:.1f}%", f"-{churn_rate*0.1:.1f}%", delta_color="inverse")
    with kpi_col14:
        st.metric("NPS Score", f"{nps_score:.0f}", f"+{nps_score*0.05:.0f}")
    with kpi_col15:
        st.metric("Market Share", f"{market_share:.1f}%", "+0.8%")
    
    # Operational Efficiency
    st.caption("Operational Efficiency")
    kpi_col16, kpi_col17, kpi_col18, kpi_col19, kpi_col20 = st.columns(5)
    with kpi_col16:
        st.metric("Inv. Turnover Days", f"{inv_turnover_days:.0f}", "-3 days", delta_color="inverse")
    with kpi_col17:
        st.metric("Order Fulfillment", f"{order_fulfillment:.1f}%", "+0.5%")
    with kpi_col18:
        st.metric("Supplier Lead Time", f"{lead_time:.0f} days", "-2 days", delta_color="inverse")
    with kpi_col19:
        st.metric("Capacity Utilization", f"{utilization:.1f}%", "+5%")
    with kpi_col20:
        st.metric("Defect Rate", f"{defect_rate:.2f}%", f"-{defect_rate*0.2:.1f}%", delta_color="inverse")
    
    # Growth & Innovation
    st.caption("Growth & Innovation")
    kpi_col21, kpi_col22, kpi_col23, kpi_col24, kpi_col25 = st.columns(5)
    with kpi_col21:
        st.metric("YoY Revenue Growth", f"{rev_growth:.1f}%", "+4.1%")
    with kpi_col22:
        st.metric("New Product Rev %", f"{new_prod_rev:.1f}%", "+2%")
    with kpi_col23:
        st.metric("Digital Sales %", f"{digital_sales:.1f}%", "+8%")
    with kpi_col24:
        st.metric("Employee Satisfaction", f"{emp_sat:.1f}/5", "+0.1")
    with kpi_col25:
        st.metric("Sustainability Index", f"{sustainability:.0f}", "+5")

    # Row 3: Advanced Metrics from second code
    col9, col10, col11, col12 = st.columns(4)

    with col9:
        st.markdown(f"""
        <div class='metric-card-v2'>
            <div class='metric-value-v2'>{profitability_score_avg:.0f}</div>
            <div class='metric-label-v2'>Profitability Score</div>
            <div class='metric-trend {'trend-up' if profitability_score_avg > 60 else 'trend-down'}'>
                {'▲' if profitability_score_avg > 60 else '▼'} Score
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col10:
        st.markdown(f"""
        <div class='metric-card-v2'>
            <div class='metric-value-v2'>{efficiency_score_avg:.0f}</div>
            <div class='metric-label-v2'>Efficiency Score</div>
            <div class='metric-trend {'trend-up' if efficiency_score_avg > 60 else 'trend-down'}'>
                {'▲' if efficiency_score_avg > 60 else '▼'} Score
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col11:
        st.markdown(f"""
        <div class='metric-card-v2'>
            <div class='metric-value-v2'>{growth_potential_avg:.0f}</div>
            <div class='metric-label-v2'>Growth Potential</div>
            <div class='metric-trend {'trend-up' if growth_potential_avg > 50 else 'trend-neutral'}'>
                {'▲' if growth_potential_avg > 50 else '▬'} Potential
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col12:
        st.markdown(f"""
        <div class='metric-card-v2'>
            <div class='metric-value-v2'>{high_performance_pct:.1f}%</div>
            <div class='metric-label-v2'>High Performers</div>
            <div class='metric-trend {'trend-up' if high_performance_pct > 30 else 'trend-down'}'>
                {'▲' if high_performance_pct > 30 else '▼'} {abs(high_performance_pct - 30):.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Quick Stats Row from first code
    st.markdown("### Quick Performance Stats")

    quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)

    with quick_col1:
        total_sales = df['monthly_sales'].sum()
        st.metric("Total Sales Volume", f"₹{total_sales/1e9:.1f}B", "+18.2%")
        
    with quick_col2:
        total_profit = df['predicted_profit'].sum()
        st.metric("Total Profit", f"₹{total_profit/1e9:.1f}B", "+12.5%")
        
    with quick_col3:
        low_risk_pct = (df['risk_band'] == 'Low').mean() * 100 if 'risk_band' in df.columns else 0
        st.metric("Low Risk Businesses", f"{low_risk_pct:.1f}%", "+5.1%")
        
    with quick_col4:
        avg_customer_rating = df['customer_rating'].mean() if 'customer_rating' in df.columns else 4.0
        st.metric("Avg Customer Rating", f"{avg_customer_rating:.1f}/5.0", "+0.3")

    # ============================================================
    # DATA PREVIEW - FROM FIRST CODE
    # ============================================================
    with st.expander("Dataset Overview", expanded=False):
        tab1, tab2, tab3 = st.tabs(["Data Preview", "Statistics", "Data Quality"])
        
        with tab1:
            st.dataframe(df_raw.head(100), use_container_width=True)
        
        with tab2:
            st.dataframe(df_raw.describe(), use_container_width=True)
        
        with tab3:
            missing_df = pd.DataFrame({
                'Column': df_raw.columns,
                'Missing Values': df_raw.isnull().sum(),
                'Missing %': (df_raw.isnull().sum() / len(df_raw) * 100).round(2)
            })
            st.dataframe(missing_df, use_container_width=True)

    # ============================================================
    # STRATEGIC INSIGHTS - FROM FIRST CODE
    # ============================================================
    st.markdown("<h2 class='section-header'>Strategic Insights</h2>", unsafe_allow_html=True)

    insight_col1, insight_col2 = st.columns(2)

    with insight_col1:
        st.markdown("""
        <div class='insight-card'>
            <strong>Performance Drivers</strong><br>
            Employee efficiency shows strong correlation with profitability.
            Businesses with efficiency above ₹50,000 consistently outperform peers.
        </div>
        
        <div class='insight-card'>
            <strong>Marketing Optimization</strong><br>
            Marketing ROI above 2.0 delivers significantly higher profit margins.
            Diminishing returns observed beyond optimal spend levels.
        </div>
        
        <div class='insight-card'>
            <strong>Inventory Management</strong><br>
            Optimal inventory-to-sales ratio identified at 0.8.
            Excess inventory reduces profit margins on average.
        </div>
        """, unsafe_allow_html=True)

    with insight_col2:
        st.markdown("""
        <div class='insight-card'>
            <strong>Cost Structure Analysis</strong><br>
            Rent and logistics account for majority of operational costs.
            Efficient location selection impacts profitability significantly.
        </div>
        
        <div class='insight-card'>
            <strong>Risk Mitigation</strong><br>
            High-risk businesses typically maintain elevated inventory levels.
            Strategic discounting decreases risk exposure.
        </div>
        
        <div class='insight-card'>
            <strong>Seasonal Opportunities</strong><br>
            Festival seasons boost sales significantly.
            Conversion rates increase during promotional periods.
        </div>
        """, unsafe_allow_html=True)

    # ============================================================
    # ADDITIONAL STRATEGIC INSIGHTS - FROM SECOND CODE
    # ============================================================
    st.markdown("<h2 class='section-header'>Advanced Strategic Insights</h2>", unsafe_allow_html=True)

    insight_col3, insight_col4 = st.columns(2)

    with insight_col3:
        top_region = df['region'].value_counts().index[0] if 'region' in df.columns else "Northern"
        st.markdown(f"""
        <div class='insight-card-v2'>
            <h4>🏆 Performance Highlights</h4>
            <p><strong>Top Performing Segment:</strong> Businesses in {top_region} region show 35% higher profitability</p>
            <p><strong>Best ROI Channel:</strong> Digital marketing delivers 2.8x higher returns than traditional channels</p>
            <p><strong>Efficiency Leaders:</strong> Employee training programs have increased productivity by 22%</p>
        </div>
        
        <div class='insight-card-v2'>
            <h4>💰 Profit Optimization</h4>
            <p><strong>Margin Improvement:</strong> Reducing operational costs by 15% could increase profits by ₹2.5M monthly</p>
            <p><strong>Revenue Growth:</strong> Upselling strategies have shown 18% revenue increase in pilot stores</p>
            <p><strong>Cost Control:</strong> Inventory optimization can reduce holding costs by 12%</p>
        </div>
        
        <div class='insight-card-v2'>
            <h4>📊 Sales Excellence</h4>
            <p><strong>Conversion Boost:</strong> Improving website UX could increase conversions by 25%</p>
            <p><strong>Customer Value:</strong> High-rating customers spend 3.2x more than average</p>
            <p><strong>Seasonal Opportunities:</strong> Festival seasons account for 42% of annual sales</p>
        </div>
        """, unsafe_allow_html=True)

    with insight_col4:
        st.markdown("""
        <div class='insight-card-v2'>
            <h4>⚠️ Risk Management</h4>
            <p><strong>Risk Reduction:</strong> High-risk businesses can improve by optimizing inventory levels</p>
            <p><strong>Credit Control:</strong> Tightening credit terms could reduce bad debts by ₹1.2M</p>
            <p><strong>Compliance:</strong> 98% compliance rate across all regulatory requirements</p>
        </div>
        
        <div class='insight-card-v2'>
            <h4>👥 Workforce Analytics</h4>
            <p><strong>Productivity:</strong> Top 20% employees contribute 45% of total output</p>
            <p><strong>Retention:</strong> Employee satisfaction scores increased by 18% with new benefits</p>
            <p><strong>Training ROI:</strong> Every ₹1 spent on training returns ₹3.5 in productivity gains</p>
        </div>
        
        <div class='insight-card-v2'>
            <h4>🚀 Growth Opportunities</h4>
            <p><strong>Market Expansion:</strong> Tier 2 cities show 28% higher growth potential</p>
            <p><strong>Digital Transformation:</strong> E-commerce adoption could increase reach by 300%</p>
            <p><strong>Strategic Partnerships:</strong> Potential partnerships could generate ₹15M in new revenue</p>
        </div>
        """, unsafe_allow_html=True)

    # ============================================================
    # COMPREHENSIVE VISUALIZATION DASHBOARD - FROM FIRST CODE (30 VISUALIZATIONS)
    # ============================================================
    st.markdown("<h2 class='section-header'>Comprehensive Analytics Dashboard </h2>", unsafe_allow_html=True)

    # Create tabs for different visualization categories from first code
    viz_tabs1 = st.tabs([
        "📊 Sales Analytics", 
        "💰 Profit Analytics", 
        "⚠️ Risk Analytics", 
        "📈 Performance Trends",
        "🗺️ Geographic Analysis",
        "🔍 Deep Dive Analysis"
    ])

    # ============================================================
    # TAB 1: SALES ANALYTICS - 8 VISUALIZATIONS FROM FIRST CODE
    # ============================================================
    with viz_tabs1[0]:
        st.markdown("### Sales Performance Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 1. Sales Distribution by Month
            if 'month' in df.columns:
                monthly_sales = df.groupby('month')['monthly_sales'].agg(['mean', 'sum']).reset_index()
                fig = px.bar(monthly_sales, x='month', y='sum',
                            title='Total Sales by Month',
                            labels={'sum': 'Total Sales (₹)', 'month': 'Month'},
                            template='plotly_white',
                            color_discrete_sequence=[COLOR_PALETTE['primary']])
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 2. Sales Conversion Funnel
            if all(col in df.columns for col in ['avg_daily_footfall', 'conversion_rate', 'avg_transaction_value']):
                funnel_data = pd.DataFrame({
                    'Stage': ['Visitors', 'Converted', 'Sales Value'],
                    'Value': [
                        df['avg_daily_footfall'].mean() * 30,
                        df['avg_daily_footfall'].mean() * df['conversion_rate'].mean() * 30,
                        df['avg_daily_footfall'].mean() * df['conversion_rate'].mean() * df['avg_transaction_value'].mean() * 30
                    ]
                })
                fig = px.funnel(funnel_data, x='Value', y='Stage',
                               title='Sales Conversion Funnel',
                               template='plotly_white',
                               color_discrete_sequence=PLOTLY_COLORS)
                st.plotly_chart(fig, use_container_width=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            # 3. Sales Heatmap by Business Type and City Tier
            if all(col in df.columns for col in ['business_type', 'city_tier', 'monthly_sales']):
                heatmap_data = df.groupby(['business_type', 'city_tier'])['monthly_sales'].mean().unstack()
                fig = px.imshow(heatmap_data,
                               title='Sales Heatmap by Business Type & City Tier',
                               labels=dict(x="City Tier", y="Business Type", color="Avg Sales"),
                               template='plotly_white',
                               color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            # 4. Sales Growth Analysis
            if 'years_of_operation' in df.columns:
                growth_data = df.groupby('years_of_operation')['monthly_sales'].mean().reset_index()
                fig = px.line(growth_data, x='years_of_operation', y='monthly_sales',
                             title='Sales Growth by Business Age',
                             labels={'monthly_sales': 'Average Monthly Sales (₹)', 'years_of_operation': 'Years in Operation'},
                             template='plotly_white',
                             markers=True)
                fig.update_traces(line=dict(width=3, color=COLOR_PALETTE['secondary']))
                st.plotly_chart(fig, use_container_width=True)
        
        # 5. Sales Comparison Radar Chart
        st.markdown("##### Multi-dimensional Sales Comparison")
        if 'business_type' in df.columns:
            radar_metrics = df.groupby('business_type').agg({
                'monthly_sales': 'mean',
                'sales_per_sqft': 'mean',
                'sales_per_employee': 'mean',
                'conversion_rate': 'mean',
                'avg_transaction_value': 'mean'
            }).reset_index()
            
            fig = go.Figure()
            for idx, row in radar_metrics.iterrows():
                # Normalize values for radar chart
                normalized_values = [
                    row['monthly_sales'] / radar_metrics['monthly_sales'].max(),
                    row['sales_per_sqft'] / radar_metrics['sales_per_sqft'].max(),
                    row['sales_per_employee'] / radar_metrics['sales_per_employee'].max(),
                    row['conversion_rate'] / radar_metrics['conversion_rate'].max(),
                    row['avg_transaction_value'] / radar_metrics['avg_transaction_value'].max()
                ]
                
                fig.add_trace(go.Scatterpolar(
                    r=normalized_values,
                    theta=['Total Sales', 'Sales/SqFt', 'Sales/Emp', 'Conv Rate', 'Avg Transaction'],
                    fill='toself',
                    name=row['business_type']
                ))
            
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                showlegend=True,
                title='Sales Performance Radar Chart',
                template='plotly_white'
            )
            st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 2: PROFIT ANALYTICS - 8 VISUALIZATIONS FROM FIRST CODE
    # ============================================================
    with viz_tabs1[1]:
        st.markdown("### Profitability Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 6. Profit Margin Distribution
            if 'profit_margin' in df.columns:
                fig = px.histogram(df, x='profit_margin', nbins=30,
                                  title='Profit Margin Distribution',
                                  labels={'profit_margin': 'Profit Margin (%)', 'count': 'Frequency'},
                                  template='plotly_white',
                                  color_discrete_sequence=[COLOR_PALETTE['primary']])
                fig.add_vline(x=df['profit_margin'].mean(), line_dash="dash", line_color="red",
                             annotation_text=f"Mean: {df['profit_margin'].mean():.2%}")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 7. Profit vs Cost Ratio
            df_sample = df.sample(min(2000, len(df)))
            fig = px.scatter(df_sample, x='cost_to_sales_ratio', y='predicted_profit',
                            title='Profit vs Cost-to-Sales Ratio',
                            labels={'predicted_profit': 'Profit (₹)', 'cost_to_sales_ratio': 'Cost/Sales Ratio'},
                            template='plotly_white',
                            color_discrete_sequence=[COLOR_PALETTE['warning']],
                            trendline='ols')
            st.plotly_chart(fig, use_container_width=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            # 8. Profit Contribution by Business Type
            if 'business_type' in df.columns:
                profit_contribution = df.groupby('business_type')['predicted_profit'].sum().reset_index()
                fig = px.pie(profit_contribution, values='predicted_profit', names='business_type',
                            title='Profit Contribution by Business Type',
                            template='plotly_white',
                            hole=0.4,
                            color_discrete_sequence=PLOTLY_COLORS)
                st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            # 9. Profit Efficiency Matrix - FIXED VERSION
            if all(col in df.columns for col in ['employee_efficiency', 'sales_per_sqft', 'predicted_profit']):
                df_sample = df.sample(min(3000, len(df)))
                
                # Use absolute profit values for size to avoid negative values
                profit_sizes = np.abs(df_sample['predicted_profit'])
                # Normalize sizes for better visualization
                normalized_sizes = (profit_sizes - profit_sizes.min()) / (profit_sizes.max() - profit_sizes.min()) * 30 + 5
                
                fig = px.scatter(df_sample, x='employee_efficiency', y='sales_per_sqft',
                                size=normalized_sizes,
                                color='predicted_profit',
                                title='Profit Efficiency Matrix',
                                labels={'employee_efficiency': 'Employee Efficiency', 
                                       'sales_per_sqft': 'Sales per SqFt',
                                       'predicted_profit': 'Profit'},
                                template='plotly_white',
                                color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
        
        # 10. Profit Waterfall Chart
        st.markdown("##### Profit Decomposition Analysis")
        avg_data = df.mean(numeric_only=True)
        waterfall_data = [
            ("Gross Revenue", avg_data['monthly_sales']),
            ("Cost of Goods", -avg_data['supplier_cost']),
            ("Operating Expenses", -(avg_data['rent_cost'] + avg_data['electricity_cost'] + avg_data['logistics_cost'])),
            ("Marketing Costs", -avg_data['marketing_spend']),
            ("Employee Costs", -(avg_data['avg_employee_salary'] * avg_data['employee_count'])),
            ("Net Profit", avg_data['predicted_profit'])
        ]
        
        measures = ["relative", "relative", "relative", "relative", "relative", "total"]
        fig = go.Figure(go.Waterfall(
            name="Profit Analysis",
            orientation="v",
            measure=measures,
            x=[x[0] for x in waterfall_data],
            y=[x[1] for x in waterfall_data],
            text=[f"₹{x[1]:,.0f}" for x in waterfall_data],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
        ))
        
        fig.update_layout(
            title="Average Monthly Profit Waterfall Analysis",
            template='plotly_white',
            showlegend=False,
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 3: RISK ANALYTICS - 8 VISUALIZATIONS FROM FIRST CODE
    # ============================================================
    with viz_tabs1[2]:
        st.markdown("### Risk Assessment Dashboard")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 11. Risk Profile by Business Type
            if all(col in df.columns for col in ['business_type', 'risk_band']):
                risk_profile = pd.crosstab(df['business_type'], df['risk_band'], normalize='index') * 100
                fig = px.bar(risk_profile, 
                            title='Risk Profile by Business Type',
                            labels={'value': 'Percentage (%)', 'business_type': 'Business Type'},
                            template='plotly_white',
                            color_discrete_sequence=[COLOR_PALETTE['secondary'], COLOR_PALETTE['warning'], COLOR_PALETTE['danger']])
                fig.update_layout(barmode='stack')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 12. Risk vs Financial Ratios
            if all(col in df.columns for col in ['risk_band', 'profit_margin', 'cost_to_sales_ratio']):
                fig = px.box(df, x='risk_band', y='profit_margin',
                            title='Profit Margin by Risk Band',
                            labels={'profit_margin': 'Profit Margin', 'risk_band': 'Risk Band'},
                            template='plotly_white',
                            color='risk_band',
                            color_discrete_map={'Low': COLOR_PALETTE['secondary'], 
                                              'Medium': COLOR_PALETTE['warning'],
                                              'High': COLOR_PALETTE['danger']})
                st.plotly_chart(fig, use_container_width=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            # 13. Risk Probability Distribution
            if 'predicted_profit' in df.columns:
                fig = ff.create_distplot([df['predicted_profit']], ['Profit Distribution'],
                                         bin_size=5000, colors=[COLOR_PALETTE['primary']])
                fig.update_layout(
                    title='Profit Distribution with Risk Thresholds',
                    template='plotly_white',
                    xaxis_title='Predicted Profit (₹)',
                    yaxis_title='Density'
                )
                
                # Add risk thresholds
                low_threshold = df['predicted_profit'].quantile(0.33)
                high_threshold = df['predicted_profit'].quantile(0.66)
                
                fig.add_vline(x=low_threshold, line_dash="dash", line_color=COLOR_PALETTE['warning'],
                             annotation_text="Medium Risk Threshold")
                fig.add_vline(x=high_threshold, line_dash="dash", line_color=COLOR_PALETTE['secondary'],
                             annotation_text="Low Risk Threshold")
                
                st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            # 14. Risk Correlation Matrix
            risk_metrics = ['predicted_profit', 'inventory_level', 'marketing_spend', 
                           'employee_count', 'rent_cost', 'conversion_rate']
            available_metrics = [m for m in risk_metrics if m in df.columns]
            
            if len(available_metrics) >= 3:
                corr_matrix = df[available_metrics].corr()
                fig = go.Figure(data=go.Heatmap(
                    z=corr_matrix.values,
                    x=available_metrics,
                    y=available_metrics,
                    colorscale='RdBu',
                    zmin=-1, zmax=1,
                    text=corr_matrix.round(2).values,
                    texttemplate='%{text}',
                    textfont={"size": 10},
                ))
                fig.update_layout(
                    title="Risk Factor Correlation Matrix",
                    template='plotly_white',
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # 15. Risk Cluster Analysis
        st.markdown("##### Risk Cluster Visualization")
        if all(col in df.columns for col in ['predicted_profit', 'monthly_sales', 'risk_band']):
            df_sample = df.sample(min(5000, len(df)))
            fig = px.scatter(df_sample, x='monthly_sales', y='predicted_profit',
                            color='risk_band',
                            title='Risk Clusters: Sales vs Profit',
                            labels={'monthly_sales': 'Monthly Sales (₹)', 
                                   'predicted_profit': 'Predicted Profit (₹)',
                                   'risk_band': 'Risk Band'},
                            template='plotly_white',
                            color_discrete_map={'Low': COLOR_PALETTE['secondary'], 
                                              'Medium': COLOR_PALETTE['warning'],
                                              'High': COLOR_PALETTE['danger']})
            st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 4: PERFORMANCE TRENDS - 8 VISUALIZATIONS FROM FIRST CODE
    # ============================================================
    with viz_tabs1[3]:
        st.markdown("### Performance Trend Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 16. Time Series Profit Analysis
            if 'year' in df.columns:
                yearly_profit = df.groupby('year')['predicted_profit'].agg(['mean', 'std']).reset_index()
                fig = px.line(yearly_profit, x='year', y='mean',
                             error_y='std',
                             title='Yearly Profit Trends with Confidence Intervals',
                             labels={'mean': 'Average Profit (₹)', 'year': 'Year'},
                             template='plotly_white',
                             markers=True)
                fig.update_traces(line=dict(width=3, color=COLOR_PALETTE['primary']))
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 17. Seasonal Performance
            if all(col in df.columns for col in ['month', 'is_festival_season']):
                seasonal_data = df.groupby(['month', 'is_festival_season'])['monthly_sales'].mean().reset_index()
                seasonal_data['Season'] = seasonal_data['is_festival_season'].map({0: 'Regular', 1: 'Festival'})
                
                # Calculate growth rates for demonstration purposes, assuming 'months' and 'growth_rates' are defined
                # For a proper seasonal sales performance, the original px.bar is more suitable.
                # This change is based on the provided instruction snippet which seems to be a different plot.
                # Reverting to a more appropriate bar chart for seasonal performance based on the original intent.
                
                # Original px.bar for seasonal performance:
                # fig = px.bar(seasonal_data, x='month', y='monthly_sales', color='Season',
                #             title='Seasonal Sales Performance',
                #             labels={'monthly_sales': 'Average Sales (₹)', 'month': 'Month'},
                #             template='plotly_white',
                #             barmode='group',
                #             color_discrete_sequence=[COLOR_PALETTE['info'], COLOR_PALETTE['warning']])
                
                # Applying the color change to the original px.bar structure,
                # assuming COLOR_PALETTE['info'] and COLOR_PALETTE['warning'] are not blue/green.
                # If the instruction implies a complete change to a growth rate bar chart,
                # then 'months' and 'growth_rates' would need to be defined.
                # Given the context of "Seasonal Sales Performance", a bar chart of sales by season is expected.
                
                # If the intent was to replace blue/green in the existing color_discrete_sequence:
                # COLOR_PALETTE['info'] is typically a shade of blue.
                # COLOR_PALETTE['warning'] is typically a shade of yellow/orange.
                # Replacing blue with #EA4643 and keeping warning.
                
                fig = px.bar(seasonal_data, x='month', y='monthly_sales', color='Season',
                            title='Seasonal Sales Performance',
                            labels={'monthly_sales': 'Average Sales (₹)', 'month': 'Month'},
                            template='plotly_white',
                            barmode='group',
                            color_discrete_sequence=['#EA4643', COLOR_PALETTE['warning']]) # Replaced blue with #EA4643
                st.plotly_chart(fig, use_container_width=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            # 18. Moving Average Analysis
            if 'month' in df.columns:
                monthly_avg = df.groupby('month')['monthly_sales'].mean().reset_index()
                monthly_avg['Moving_Avg_3'] = monthly_avg['monthly_sales'].rolling(window=3, min_periods=1).mean()
                
                fig = px.line(monthly_avg, x='month', y=['monthly_sales', 'Moving_Avg_3'],
                             title='Sales Trend with 3-Month Moving Average',
                             labels={'value': 'Sales (₹)', 'month': 'Month', 'variable': 'Metric'},
                             template='plotly_white')
                fig.update_traces(line=dict(width=3))
                st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            # 19. Performance Growth Rate
            if 'years_of_operation' in df.columns:
                growth_data = df.groupby('years_of_operation').agg({
                    'monthly_sales': 'mean',
                    'predicted_profit': 'mean',
                    'profit_margin': 'mean'
                }).reset_index()
                
                fig = make_subplots(rows=2, cols=1, subplot_titles=('Sales Growth', 'Profit Margin Growth'))
                
                fig.add_trace(
                    go.Scatter(x=growth_data['years_of_operation'], 
                              y=growth_data['monthly_sales'],
                              name='Sales',
                              line=dict(color=COLOR_PALETTE['primary'], width=3)),
                    row=1, col=1
                )
                
                fig.add_trace(
                    go.Scatter(x=growth_data['years_of_operation'], 
                              y=growth_data['profit_margin'] * 100,
                              name='Profit Margin',
                              line=dict(color=COLOR_PALETTE['secondary'], width=3)),
                    row=2, col=1
                )
                
                fig.update_layout(height=600, template='plotly_white', showlegend=True)
                fig.update_xaxes(title_text="Years in Operation", row=2, col=1)
                fig.update_yaxes(title_text="Sales (₹)", row=1, col=1)
                fig.update_yaxes(title_text="Profit Margin (%)", row=2, col=1)
                
                st.plotly_chart(fig, use_container_width=True)
        
        # 20. Performance Benchmarking
        st.markdown("##### Performance Benchmark Dashboard")
        if 'business_type' in df.columns:
            benchmarks = df.groupby('business_type').agg({
                'monthly_sales': 'mean',
                'predicted_profit': 'mean',
                'profit_margin': 'mean',
                'marketing_roi': 'mean',
                'customer_rating': 'mean'
            }).reset_index()
            
            fig = go.Figure()
            
            for metric in ['monthly_sales', 'predicted_profit', 'profit_margin', 'marketing_roi', 'customer_rating']:
                if metric in benchmarks.columns:
                    normalized = (benchmarks[metric] - benchmarks[metric].min()) / (benchmarks[metric].max() - benchmarks[metric].min())
                    fig.add_trace(go.Box(
                        y=normalized,
                        name=metric.replace('_', ' ').title(),
                        boxpoints='all',
                        marker_color=PLOTLY_COLORS[list(benchmarks.columns).index(metric) % len(PLOTLY_COLORS)]
                    ))
            
            fig.update_layout(
                title="Performance Benchmark Distribution",
                template='plotly_white',
                yaxis_title="Normalized Score",
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 5: GEOGRAPHIC ANALYSIS - 8 VISUALIZATIONS FROM FIRST CODE
    # ============================================================
    with viz_tabs1[4]:
        st.markdown("### Geographic Performance Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 21. Geographic Profit Heatmap
            if 'city' in df.columns:
                city_profit = df.groupby('city')['predicted_profit'].mean().reset_index()
                fig = px.bar(city_profit, x='city', y='predicted_profit',
                            title='Average Profit by City',
                            labels={'predicted_profit': 'Average Profit (₹)', 'city': 'City'},
                            template='plotly_white',
                            color='predicted_profit',
                            color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 22. City Tier Performance Comparison
            if 'city_tier' in df.columns:
                tier_performance = df.groupby('city_tier').agg({
                    'monthly_sales': 'mean',
                    'predicted_profit': 'mean',
                    'rent_cost': 'mean',
                    'customer_rating': 'mean'
                }).reset_index()
                
                fig = make_subplots(
                    rows=2, cols=2,
                    subplot_titles=('Sales', 'Profit', 'Rent Cost', 'Customer Rating'),
                    specs=[[{'type': 'bar'}, {'type': 'bar'}],
                          [{'type': 'bar'}, {'type': 'bar'}]]
                )
                
                metrics = ['monthly_sales', 'predicted_profit', 'rent_cost', 'customer_rating']
                colors = [COLOR_PALETTE['primary'], COLOR_PALETTE['secondary'], 
                         COLOR_PALETTE['warning'], COLOR_PALETTE['danger']]
                
                for idx, metric in enumerate(metrics):
                    if metric in tier_performance.columns:
                        row = idx // 2 + 1
                        col = idx % 2 + 1
                        
                        fig.add_trace(
                            go.Bar(x=tier_performance['city_tier'], 
                                  y=tier_performance[metric],
                                  name=metric.replace('_', ' ').title(),
                                  marker_color=colors[idx]),
                            row=row, col=col
                        )
                
                fig.update_layout(height=600, template='plotly_white', showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        
        # 23. Geographic Distribution Map
        st.markdown("##### Geographic Performance Distribution")
        
        # Create synthetic geographic coordinates for demonstration
        city_coords = {
            'Mumbai': (19.0760, 72.8777),
            'Delhi': (28.7041, 77.1025),
            'Bangalore': (12.9716, 77.5946),
            'Chennai': (13.0827, 80.2707),
            'Kolkata': (22.5726, 88.3639),
            'Hyderabad': (17.3850, 78.4867)
        }
        
        if 'city' in df.columns:
            city_stats = df.groupby('city').agg({
                'monthly_sales': 'mean',
                'predicted_profit': 'mean',
                'customer_rating': 'mean',
                'risk_band': lambda x: (x == 'High').mean() * 100
            }).reset_index()
            
            # Add coordinates
            city_stats['lat'] = city_stats['city'].map(lambda x: city_coords.get(x, (20, 78))[0])
            city_stats['lon'] = city_stats['city'].map(lambda x: city_coords.get(x, (20, 78))[1])
            
            fig = px.scatter_geo(city_stats,
                                lat='lat',
                                lon='lon',
                                size='monthly_sales',
                                color='predicted_profit',
                                hover_name='city',
                                hover_data=['customer_rating', 'risk_band'],
                                title='Geographic Business Performance',
                                template='plotly_white',
                                color_continuous_scale='Viridis',
                                projection='natural earth')
            
            st.plotly_chart(fig, use_container_width=True)
        
        # 24. Geographic Cluster Analysis
        col3, col4 = st.columns(2)
        
        with col3:
            if all(col in df.columns for col in ['city', 'business_type', 'monthly_sales']):
                geo_cluster = df.groupby(['city', 'business_type'])['monthly_sales'].mean().unstack().fillna(0)
                fig = px.imshow(geo_cluster,
                               title='Sales Heatmap: City × Business Type',
                               labels=dict(x="Business Type", y="City", color="Sales (₹)"),
                               template='plotly_white',
                               color_continuous_scale='YlOrRd')
                st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            # 25. Geographic Performance Spider Chart
            if 'city' in df.columns and len(df['city'].unique()) <= 10:
                city_metrics = df.groupby('city').agg({
                    'monthly_sales': 'mean',
                    'predicted_profit': 'mean',
                    'profit_margin': 'mean',
                    'customer_rating': 'mean',
                    'employee_efficiency': 'mean'
                }).reset_index()
                
                fig = go.Figure()
                
                for idx, city in enumerate(city_metrics['city'].unique()[:5]):
                    city_data = city_metrics[city_metrics['city'] == city].iloc[0]
                    metrics = ['monthly_sales', 'predicted_profit', 'profit_margin', 'customer_rating', 'employee_efficiency']
                    values = [city_data[m] for m in metrics]
                    
                    # Normalize values
                    max_vals = city_metrics[metrics].max()
                    normalized = [v/max_vals[m] for v, m in zip(values, metrics)]
                    
                    fig.add_trace(go.Scatterpolar(
                        r=normalized,
                        theta=['Sales', 'Profit', 'Margin', 'Rating', 'Efficiency'],
                        fill='toself',
                        name=city,
                        line_color=PLOTLY_COLORS[idx % len(PLOTLY_COLORS)]
                    ))
                
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                    title='City Performance Spider Chart',
                    template='plotly_white',
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 6: DEEP DIVE ANALYSIS - 8 VISUALIZATIONS FROM FIRST CODE
    # ============================================================
    with viz_tabs1[5]:
        st.markdown("### Deep Dive Analytical Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 26. Customer Value Analysis
            if all(col in df.columns for col in ['customer_rating', 'monthly_sales', 'conversion_rate']):
                df_sample = df.sample(min(2000, len(df)))
                fig = px.scatter_3d(df_sample,
                                   x='customer_rating',
                                   y='conversion_rate',
                                   z='monthly_sales',
                                   color='predicted_profit',
                                   title='3D: Customer Rating × Conversion × Sales',
                                   labels={'customer_rating': 'Customer Rating',
                                          'conversion_rate': 'Conversion Rate',
                                          'monthly_sales': 'Monthly Sales',
                                          'predicted_profit': 'Profit'},
                                   template='plotly_white',
                                   color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 27. Cost Efficiency Analysis
            cost_metrics = ['rent_cost', 'electricity_cost', 'logistics_cost', 'supplier_cost']
            available_costs = [m for m in cost_metrics if m in df.columns]
            
            if available_costs:
                cost_data = df[available_costs].mean().reset_index()
                cost_data.columns = ['Cost Type', 'Average Cost']
                
                fig = px.bar(cost_data, x='Cost Type', y='Average Cost',
                            title='Average Cost Distribution',
                            labels={'Average Cost': 'Average Cost (₹)', 'Cost Type': 'Cost Type'},
                            template='plotly_white',
                            color='Average Cost',
                            color_continuous_scale='RdBu_r')
                st.plotly_chart(fig, use_container_width=True)
        
        # 28. Predictive Model Performance
        st.markdown("##### Model Performance Analysis")
        
        if 'predicted_profit' in df.columns and 'profit_margin' in df.columns:
            actual_profit = df['monthly_sales'] * df['profit_margin'] - df['operating_cost'] - df['employee_count'] * df['avg_employee_salary']
            
            performance_df = pd.DataFrame({
                'Actual': actual_profit,
                'Predicted': df['predicted_profit']
            }).sample(min(5000, len(df)))
            
            fig = make_subplots(rows=1, cols=2,
                               subplot_titles=('Actual vs Predicted', 'Prediction Error Distribution'))
            
            # Scatter plot
            fig.add_trace(
                go.Scatter(x=performance_df['Actual'], y=performance_df['Predicted'],
                          mode='markers',
                          marker=dict(size=5, color=COLOR_PALETTE['primary'], opacity=0.5),
                          name='Predictions'),
                row=1, col=1
            )
            
            # Add perfect prediction line
            max_val = max(performance_df['Actual'].max(), performance_df['Predicted'].max())
            fig.add_trace(
                go.Scatter(x=[0, max_val], y=[0, max_val],
                          mode='lines',
                          line=dict(color='red', dash='dash'),
                          name='Perfect Prediction'),
                row=1, col=1
            )
            
            # Error distribution
            errors = performance_df['Predicted'] - performance_df['Actual']
            fig.add_trace(
                go.Histogram(x=errors,
                            nbinsx=50,
                            marker_color=COLOR_PALETTE['warning'],
                            name='Prediction Errors'),
                row=1, col=2
            )
            
            fig.update_layout(height=400, template='plotly_white', showlegend=True)
            fig.update_xaxes(title_text="Actual Profit", row=1, col=1)
            fig.update_yaxes(title_text="Predicted Profit", row=1, col=1)
            fig.update_xaxes(title_text="Prediction Error", row=1, col=2)
            fig.update_yaxes(title_text="Frequency", row=1, col=2)
            
            st.plotly_chart(fig, use_container_width=True)
        
        # 29. Business Health Scorecard
        st.markdown("##### Business Health Assessment")
        
        if all(col in df.columns for col in ['risk_band', 'profit_margin', 'customer_rating', 'conversion_rate']):
            health_scores = []
            sample_df = df.sample(min(100, len(df)))
            
            for idx, row in sample_df.iterrows():
                # Calculate composite health score (0-100)
                score = (
                    (row['profit_margin'] / 0.3) * 0.3 +  # Profit margin contribution (max 30%)
                    (row['customer_rating'] / 5) * 0.25 +  # Customer rating contribution (max 25%)
                    (row['conversion_rate'] / 0.4) * 0.25 +  # Conversion rate contribution (max 25%)
                    (1 if row['risk_band'] == 'Low' else 0.5 if row['risk_band'] == 'Medium' else 0) * 0.2  # Risk contribution (max 20%)
                ) * 100
                
                health_scores.append(min(score, 100))  # Cap at 100
            
            health_df = pd.DataFrame({'Health Score': health_scores})
            
            fig = make_subplots(rows=1, cols=2,
                               subplot_titles=('Health Score Distribution', 'Health vs Profit'))
            
            fig.add_trace(
                go.Histogram(x=health_scores,
                            nbinsx=20,
                            marker_color=COLOR_PALETTE['secondary'],
                            name='Health Scores'),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=health_scores,
                          y=sample_df['predicted_profit'],
                          mode='markers',
                          marker=dict(size=8, color=COLOR_PALETTE['primary'], opacity=0.7),
                          name='Health vs Profit'),
                row=1, col=2
            )
            
            fig.update_layout(height=400, template='plotly_white', showlegend=True)
            fig.update_xaxes(title_text="Health Score", row=1, col=1)
            fig.update_yaxes(title_text="Frequency", row=1, col=1)
            fig.update_xaxes(title_text="Health Score", row=1, col=2)
            fig.update_yaxes(title_text="Profit (₹)", row=1, col=2)
            
            st.plotly_chart(fig, use_container_width=True)
        
        # 30. Interactive Parallel Coordinates Plot
        st.markdown("##### Multi-dimensional Business Analysis")
        
        if all(col in df.columns for col in ['business_type', 'city_tier', 'risk_band', 'profit_margin', 'customer_rating', 'conversion_rate']):
            parallel_df = df.sample(min(1000, len(df))).copy()
            parallel_df['profit_margin_pct'] = parallel_df['profit_margin'] * 100
            
            dimensions = [
                dict(label='Business Type', values=parallel_df['business_type']),
                dict(label='City Tier', values=parallel_df['city_tier']),
                dict(label='Risk Band', values=parallel_df['risk_band']),
                dict(label='Profit Margin %', values=parallel_df['profit_margin_pct']),
                dict(label='Customer Rating', values=parallel_df['customer_rating']),
                dict(label='Conversion Rate', values=parallel_df['conversion_rate'])
            ]
            
            fig = go.Figure(data=
                go.Parcoords(
                    line=dict(color=parallel_df['profit_margin_pct'],
                             colorscale='Viridis',
                             showscale=True,
                             cmin=parallel_df['profit_margin_pct'].min(),
                             cmax=parallel_df['profit_margin_pct'].max()),
                    dimensions=dimensions
                )
            )
            
            fig.update_layout(
                title="Parallel Coordinates: Multi-dimensional Business Analysis",
                template='plotly_white',
                height=600
            )
            st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # ADVANCED VISUALIZATION DASHBOARD - FROM SECOND CODE (10 TABS)
    # ============================================================
    st.markdown("<h2 class='section-header'>Advanced Analytics Dashboard </h2>", unsafe_allow_html=True)

    # Create comprehensive tabs from second code
    viz_tabs2 = st.tabs([
        "📊 Performance Overview", 
        "💰 Financial Analysis", 
        "📈 Sales Analytics V2", 
        "👥 Workforce Insights",
        "⚠️ Risk Assessment V2", 
        "🗺️ Geographic Analysis V2",
        "📦 Inventory & Operations",
        "🎯 Marketing Efficiency",
        "🤖 Predictive Analytics V2",
        "📋 Executive Summary"
    ])

    # ============================================================
    # TAB 1: PERFORMANCE OVERVIEW - FROM SECOND CODE
    # ============================================================
    with viz_tabs2[0]:
        st.markdown("### Comprehensive Performance Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 31. Performance Distribution Radar Chart
            if all(col in df.columns for col in ['profitability_score', 'efficiency_score', 'growth_potential']):
                avg_scores = df[['profitability_score', 'efficiency_score', 'growth_potential']].mean()
                max_scores = df[['profitability_score', 'efficiency_score', 'growth_potential']].max()
                min_scores = df[['profitability_score', 'efficiency_score', 'growth_potential']].min()
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatterpolar(
                    r=avg_scores.values,
                    theta=['Profitability', 'Efficiency', 'Growth'],
                    fill='toself',
                    name='Average Scores',
                    line_color=COLOR_PALETTE['primary']
                ))
                
                fig.add_trace(go.Scatterpolar(
                    r=max_scores.values,
                    theta=['Profitability', 'Efficiency', 'Growth'],
                    fill='toself',
                    name='Maximum Scores',
                    line_color=COLOR_PALETTE['secondary']
                ))
                
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    showlegend=True,
                    title='Performance Score Distribution',
                    template='plotly_white',
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 32. Business Health Dashboard
            metrics_available = []
            metric_names = []
            current_values = []
            target_values = []
            
            # Check which metrics are available
            if 'profit_margin' in df.columns:
                metrics_available.append('profit_margin')
                metric_names.append('Profit Margin')
                current_values.append(df['profit_margin'].mean() * 100)
                target_values.append(15)
            
            if 'customer_rating' in df.columns:
                metrics_available.append('customer_rating')
                metric_names.append('Customer Rating')
                current_values.append(df['customer_rating'].mean())
                target_values.append(4.0)
            
            if 'conversion_rate' in df.columns:
                metrics_available.append('conversion_rate')
                metric_names.append('Conversion Rate')
                current_values.append(df['conversion_rate'].mean() * 100)
                target_values.append(20)
            
            if 'inventory_turnover' in df.columns:
                metrics_available.append('inventory_turnover')
                metric_names.append('Inventory Turnover')
                current_values.append(df['inventory_turnover'].mean())
                target_values.append(2.0)
            
            if metrics_available:
                fig = go.Figure()
                
                for i, (current, target, name) in enumerate(zip(current_values, target_values, metric_names)):
                    percentage = (current / target * 100) if target > 0 else 0
                    color = COLOR_PALETTE['success'] if percentage >= 100 else COLOR_PALETTE['warning'] if percentage >= 80 else COLOR_PALETTE['danger']
                    
                    fig.add_trace(go.Indicator(
                        mode="gauge+number",
                        value=percentage,
                        title={'text': f"{name}<br>{current:.2f}"},
                        domain={'row': i // 2, 'column': i % 2},
                        gauge={
                            'axis': {'range': [0, 150]},
                            'bar': {'color': color},
                            'steps': [
                                {'range': [0, 80], 'color': COLOR_PALETTE['danger']},
                                {'range': [80, 100], 'color': COLOR_PALETTE['warning']},
                                {'range': [100, 150], 'color': COLOR_PALETTE['success']}
                            ],
                            'threshold': {
                                'line': {'color': "black", 'width': 4},
                                'thickness': 0.75,
                                'value': 100
                            }
                        }
                    ))
                
                rows = (len(metrics_available) + 1) // 2
                fig.update_layout(
                    grid={'rows': rows, 'columns': 2, 'pattern': "independent"},
                    height=rows * 250,
                    template='plotly_white'
                )
                st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 2: FINANCIAL ANALYSIS - FROM SECOND CODE
    # ============================================================
    with viz_tabs2[1]:
        st.markdown("### Financial Performance Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 33. Profit Distribution by Business Type
            if 'business_type' in df.columns and 'predicted_profit' in df.columns:
                profit_by_type = df.groupby('business_type')['predicted_profit'].agg(['mean', 'std', 'count']).reset_index()
                profit_by_type = profit_by_type.sort_values('mean', ascending=False).head(10)
                
                fig = px.bar(profit_by_type, x='business_type', y='mean',
                            error_y='std',
                            title='Average Profit by Business Type',
                            labels={'mean': 'Average Profit (₹)', 'business_type': 'Business Type'},
                            color='mean',
                            color_continuous_scale='Viridis',
                            template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 34. Cost Structure Analysis
            cost_columns = ['rent_cost', 'electricity_cost', 'logistics_cost', 'supplier_cost', 'marketing_spend']
            available_costs = [col for col in cost_columns if col in df.columns]
            
            if available_costs:
                cost_summary = df[available_costs].mean().reset_index()
                cost_summary.columns = ['Cost Type', 'Average Cost']
                cost_summary['Percentage'] = cost_summary['Average Cost'] / cost_summary['Average Cost'].sum() * 100
                
                fig = px.pie(cost_summary, values='Average Cost', names='Cost Type',
                            title='Cost Distribution Analysis',
                            hole=0.4,
                            color_discrete_sequence=PLOTLY_COLORS,
                            template='plotly_white')
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 3: SALES ANALYTICS V2 - FROM SECOND CODE
    # ============================================================
    with viz_tabs2[2]:
        st.markdown("### Sales Performance & Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 35. Sales Distribution by Region
            if 'region' in df.columns and 'monthly_sales' in df.columns:
                region_sales = df.groupby('region')['monthly_sales'].agg(['mean', 'sum']).reset_index()
                
                fig = px.bar(region_sales, x='region', y='sum',
                            title='Total Sales by Region',
                            labels={'sum': 'Total Sales (₹)', 'region': 'Region'},
                            template='plotly_white',
                            color='sum',
                            color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 36. Sales Trend by Business Age
            if 'years_of_operation' in df.columns and 'monthly_sales' in df.columns:
                age_sales = df.groupby('years_of_operation')['monthly_sales'].mean().reset_index()
                
                fig = px.line(age_sales, x='years_of_operation', y='monthly_sales',
                             title='Sales Trend by Business Age',
                             labels={'monthly_sales': 'Average Sales (₹)', 'years_of_operation': 'Years in Operation'},
                             template='plotly_white',
                             markers=True)
                fig.update_traces(line=dict(width=3, color=COLOR_PALETTE['primary']))
                st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 4: WORKFORCE INSIGHTS - FROM SECOND CODE
    # ============================================================
    with viz_tabs2[3]:
        st.markdown("### Workforce Analytics & Productivity")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 37. Employee Productivity by Business Type
            if 'business_type' in df.columns and 'employee_efficiency' in df.columns:
                efficiency_by_type = df.groupby('business_type')['employee_efficiency'].mean().reset_index()
                
                fig = px.bar(efficiency_by_type, x='business_type', y='employee_efficiency',
                            title='Employee Efficiency by Business Type',
                            labels={'employee_efficiency': 'Efficiency Score', 'business_type': 'Business Type'},
                            template='plotly_white',
                            color='employee_efficiency',
                            color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 38. Salary vs Experience Analysis
            if 'avg_employee_salary' in df.columns and 'years_of_operation' in df.columns:
                salary_experience = df.groupby('years_of_operation')['avg_employee_salary'].mean().reset_index()
                
                fig = px.scatter(salary_experience, x='years_of_operation', y='avg_employee_salary',
                                title='Salary vs Business Experience',
                                labels={'avg_employee_salary': 'Average Salary (₹)', 'years_of_operation': 'Years in Operation'},
                                template='plotly_white',
                                trendline='ols')
                st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 5: RISK ASSESSMENT V2 - FROM SECOND CODE
    # ============================================================
    with viz_tabs2[4]:
        st.markdown("### Risk Assessment & Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 39. Risk Distribution
            if 'risk_band' in df.columns:
                risk_dist = df['risk_band'].value_counts().reset_index()
                risk_dist.columns = ['Risk Category', 'Count']
                
                colors = [COLOR_PALETTE['success'], COLOR_PALETTE['warning'], COLOR_PALETTE['danger']]
                
                fig = px.pie(risk_dist, values='Count', names='Risk Category',
                            title='Risk Category Distribution',
                            template='plotly_white',
                            color_discrete_sequence=colors[:len(risk_dist)])
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 40. Risk vs Profit Analysis
            if 'risk_band' in df.columns and 'predicted_profit' in df.columns:
                risk_profit = df.groupby('risk_band')['predicted_profit'].agg(['mean', 'std', 'count']).reset_index()
                
                fig = px.bar(risk_profit, x='risk_band', y='mean',
                            error_y='std',
                            title='Average Profit by Risk Category',
                            labels={'mean': 'Average Profit (₹)', 'risk_band': 'Risk Category'},
                            template='plotly_white',
                            color='risk_band',
                            color_discrete_map={
                                'Low': COLOR_PALETTE['success'],
                                'Medium': COLOR_PALETTE['warning'],
                                'High': COLOR_PALETTE['danger']
                            })
                st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 6: GEOGRAPHIC ANALYSIS V2 - FROM SECOND CODE
    # ============================================================
    with viz_tabs2[5]:
        st.markdown("### Geographic Performance Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 41. Performance by City
            if 'city' in df.columns and 'predicted_profit' in df.columns:
                city_profit = df.groupby('city')['predicted_profit'].mean().reset_index().sort_values('predicted_profit', ascending=False).head(10)
                
                fig = px.bar(city_profit, x='city', y='predicted_profit',
                            title='Top 10 Cities by Average Profit',
                            labels={'predicted_profit': 'Average Profit (₹)', 'city': 'City'},
                            template='plotly_white',
                            color='predicted_profit',
                            color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 42. City Tier Analysis
            if 'city_tier' in df.columns and 'monthly_sales' in df.columns:
                tier_sales = df.groupby('city_tier')['monthly_sales'].mean().reset_index()
                
                fig = px.bar(tier_sales, x='city_tier', y='monthly_sales',
                            title='Sales Performance by City Tier',
                            labels={'monthly_sales': 'Average Sales (₹)', 'city_tier': 'City Tier'},
                            template='plotly_white',
                            color='monthly_sales',
                            color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 7: INVENTORY & OPERATIONS - FROM SECOND CODE
    # ============================================================
    with viz_tabs2[6]:
        st.markdown("### Inventory & Operations Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 43. Inventory Analysis
            if 'inventory_level' in df.columns and 'business_type' in df.columns:
                inventory_by_type = df.groupby('business_type')['inventory_level'].mean().reset_index()
                
                fig = px.bar(inventory_by_type, x='business_type', y='inventory_level',
                            title='Average Inventory by Business Type',
                            labels={'inventory_level': 'Inventory Level', 'business_type': 'Business Type'},
                            template='plotly_white',
                            color='inventory_level',
                            color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 44. Cost Analysis
            if 'operating_cost' in df.columns and 'business_type' in df.columns:
                cost_by_type = df.groupby('business_type')['operating_cost'].mean().reset_index()
                
                fig = px.bar(cost_by_type, x='business_type', y='operating_cost',
                            title='Operational Costs by Business Type',
                            labels={'operating_cost': 'Average Cost (₹)', 'business_type': 'Business Type'},
                            template='plotly_white',
                            color='operating_cost',
                            color_continuous_scale='Reds')
                st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 8: MARKETING EFFICIENCY - FROM SECOND CODE
    # ============================================================
    with viz_tabs2[7]:
        st.markdown("### Marketing Performance & ROI Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 45. Marketing ROI Analysis
            if 'marketing_roi' in df.columns and 'business_type' in df.columns:
                roi_by_type = df.groupby('business_type')['marketing_roi'].mean().reset_index()
                
                fig = px.bar(roi_by_type, x='business_type', y='marketing_roi',
                            title='Marketing ROI by Business Type',
                            labels={'marketing_roi': 'Return on Investment', 'business_type': 'Business Type'},
                            template='plotly_white',
                            color='marketing_roi',
                            color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 46. Marketing Spend vs Sales
            if 'marketing_spend' in df.columns and 'monthly_sales' in df.columns:
                df_sample = df.sample(min(1000, len(df)))
                
                fig = px.scatter(df_sample, x='marketing_spend', y='monthly_sales',
                                title='Marketing Spend vs Sales',
                                labels={'marketing_spend': 'Marketing Spend (₹)', 'monthly_sales': 'Monthly Sales (₹)'},
                                template='plotly_white',
                                trendline='ols')
                st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 9: PREDICTIVE ANALYTICS V2 - FROM SECOND CODE
    # ============================================================
    with viz_tabs2[8]:
        st.markdown("### Predictive Analytics & Forecasting")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 47. Profit Distribution
            if 'predicted_profit' in df.columns:
                fig = px.histogram(df, x='predicted_profit', nbins=50,
                                  title='Profit Distribution',
                                  labels={'predicted_profit': 'Profit (₹)', 'count': 'Frequency'},
                                  template='plotly_white',
                                  color_discrete_sequence=[COLOR_PALETTE['primary']])
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 48. Sales Forecasting
            if 'monthly_sales' in df.columns and 'years_of_operation' in df.columns:
                sales_trend = df.groupby('years_of_operation')['monthly_sales'].mean().reset_index()
                
                # Add trend line
                z = np.polyfit(sales_trend['years_of_operation'], sales_trend['monthly_sales'], 1)
                p = np.poly1d(z)
                sales_trend['trend'] = p(sales_trend['years_of_operation'])
                
                fig = px.line(sales_trend, x='years_of_operation', y=['monthly_sales', 'trend'],
                             title='Sales Trend with Forecast',
                             labels={'value': 'Sales (₹)', 'years_of_operation': 'Years in Operation', 'variable': 'Metric'},
                             template='plotly_white')
                fig.update_traces(line=dict(width=3))
                st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 10: EXECUTIVE SUMMARY - FROM SECOND CODE
    # ============================================================
    with viz_tabs2[9]:
        st.markdown("### Executive Summary & Recommendations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Calculate overall score
            if all(col in df.columns for col in ['profitability_score', 'efficiency_score', 'growth_potential']):
                overall_score = (df['profitability_score'].mean() + df['efficiency_score'].mean() + df['growth_potential'].mean()) / 3
            else:
                overall_score = 50
            
            avg_margin = df['profit_margin'].mean() * 100 if 'profit_margin' in df.columns else 15
            status = "Excellent" if avg_profit > 0 and avg_margin > 15 else "Good" if avg_profit > 0 else "Needs Improvement"
            trend = "Positive" if avg_profit > 0 and avg_margin > 15 else "Stable" if avg_profit > 0 else "Negative"
            
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; padding: 2rem; border-radius: 15px; margin-bottom: 2rem;'>
                <h3 style='color: white; margin-bottom: 1rem;'>📊 Overall Performance</h3>
                <p style='font-size: 1.1rem; margin-bottom: 0.5rem;'>
                    <strong>Overall Score:</strong> {overall_score:.0f}/100
                </p>
                <p style='font-size: 1.1rem; margin-bottom: 0.5rem;'>
                    <strong>Status:</strong> {status}
                </p>
                <p style='font-size: 1.1rem;'>
                    <strong>Trend:</strong> {trend}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            top_segment = df['business_type'].value_counts().index[0] if 'business_type' in df.columns else "Retail"
            
            st.markdown(f"""
            <div class='insight-card-v2'>
                <h4>🎯 Top Recommendations</h4>
                <ol>
                    <li><strong>Optimize Marketing Spend:</strong> Reallocate budget to high-ROI channels</li>
                    <li><strong>Improve Inventory Turnover:</strong> Target 2.5x vs current {inventory_turnover_avg:.1f}x</li>
                    <li><strong>Enhance Customer Experience:</strong> Focus on improving ratings from {avg_rating:.1f} to 4.5</li>
                    <li><strong>Reduce Operational Costs:</strong> Target 15% reduction in non-essential expenses</li>
                    <li><strong>Expand High-Performing Segments:</strong> Focus on {top_segment} business type</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='insight-card-v2'>
                <h4>📈 Key Performance Indicators</h4>
                <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-top: 1rem;'>
                    <div style='background: rgba(234, 70, 67, 0.1); padding: 1rem; border-radius: 8px;'>
                        <div style='font-size: 1.5rem; font-weight: bold; color: #EA4643;'>₹{avg_profit:,.0f}</div>
                        <div style='font-size: 0.9rem; color: #6B7280;'>Monthly Profit</div>
                    </div>
                    <div style='background: rgba(234, 70, 67, 0.1); padding: 1rem; border-radius: 8px;'>
                        <div style='font-size: 1.5rem; font-weight: bold; color: #EA4643;'>{avg_margin:.1f}%</div>
                        <div style='font-size: 0.9rem; color: #6B7280;'>Profit Margin</div>
                    </div>
                    <div style='background: rgba(26, 32, 44, 0.05); padding: 1rem; border-radius: 8px;'>
                        <div style='font-size: 1.5rem; font-weight: bold; color: #1A202C;'>{avg_roi:.2f}x</div>
                        <div style='font-size: 0.9rem; color: #6B7280;'>Marketing ROI</div>
                    </div>
                    <div style='background: rgba(26, 32, 44, 0.05); padding: 1rem; border-radius: 8px;'>
                        <div style='font-size: 1.5rem; font-weight: bold; color: #1A202C;'>{avg_rating:.1f}</div>
                        <div style='font-size: 0.9rem; color: #6B7280;'>Customer Rating</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class='insight-card-v2'>
                <h4>🚀 Strategic Initiatives</h4>
                <ul>
                    <li><strong>Q1 Initiative:</strong> Digital Transformation - Budget: ₹5M, Expected ROI: 3.2x</li>
                    <li><strong>Q2 Initiative:</strong> Market Expansion - Target: Tier 2 Cities, Expected Growth: 25%</li>
                    <li><strong>Q3 Initiative:</strong> Operational Efficiency - Target Savings: ₹2.5M monthly</li>
                    <li><strong>Q4 Initiative:</strong> Talent Development - Training Budget: ₹1.2M, Expected Productivity Gain: 18%</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    # ============================================================
    # PREDICTIVE SIMULATION - FROM FIRST CODE
    # ============================================================
    st.markdown("<h2 class='section-header'>Business Scenario Simulation</h2>", unsafe_allow_html=True)

    with st.container():
        sim_col1, sim_col2, sim_col3 = st.columns(3)
        
        with sim_col1:
            st.markdown("#### Sales Parameters")
            marketing_spend = st.slider("Marketing Spend (₹)", 10000, 200000, 50000, 5000)
            avg_footfall = st.slider("Daily Footfall", 50, 1000, 200, 10)
            conversion_rate = st.slider("Conversion Rate", 0.1, 0.5, 0.2, 0.01)
        
        with sim_col2:
            st.markdown("#### Cost Parameters")
            avg_salary = st.number_input("Average Salary (₹)", 15000, 50000, 25000, 1000)
            rent_cost = st.number_input("Monthly Rent (₹)", 10000, 100000, 30000, 5000)
            inventory_level = st.number_input("Inventory Level", 100, 5000, 1000, 100)
        
        with sim_col3:
            st.markdown("#### Business Profile")
            employee_count = st.slider("Employee Count", 1, 100, 10, 1)
            city_tier = st.select_slider("City Tier", options=[1, 2, 3], value=2)
            discount_pct = st.slider("Discount Percentage", 0, 50, 10, 1)
        
        festival_season = st.checkbox("Festival Season", value=False)
        
        if st.button("Run Predictive Simulation", type="primary"):
            # Create simulation data
            simulation_data = {
                "city_tier": city_tier,
                "avg_employee_salary": avg_salary,
                "inventory_level": inventory_level,
                "conversion_rate": conversion_rate,
                "is_festival_season": 1 if festival_season else 0,
                "avg_transaction_value": 900,
                "avg_daily_footfall": avg_footfall,
                "rent_cost": rent_cost,
                "supplier_cost": 50000,
                "discount_percentage": discount_pct,
                "business_type": "General",
                "store_size_sqft": 1200,
                "logistics_cost": 15000,
                "years_of_operation": 5,
                "profit_margin": 0.2,
                "marketing_roi": 2.0,
                "employee_efficiency": 50000,
                "marketing_spend": marketing_spend,
                "employee_count": employee_count
            }
            
            # Convert to DataFrame and align schema
            sim_df = pd.DataFrame([simulation_data])
            sim_df = align_schema(sim_df)
            
            # Calculate expected metrics
            expected_sales = avg_footfall * conversion_rate * 900 * 30
            operating_cost = rent_cost + 8000 + 15000 + 50000
            salary_cost = avg_salary * employee_count
            
            # Predict profit
            if model:
                predicted_profit = model.predict(sim_df)[0]
            else:
                predicted_profit = expected_sales * 0.2 - marketing_spend - salary_cost
            
            # Allow negative profit for display
            # predicted_profit = max(predicted_profit, 0) # REMOVED CLAMPING
            
            # Display results
            st.markdown("#### Simulation Results")
            
            results_col1, results_col2, results_col3, results_col4 = st.columns(4)
            
            with results_col1:
                st.metric("Expected Monthly Sales", f"₹{expected_sales:,.0f}")
            
            with results_col2:
                st.metric("Predicted Monthly Profit", f"₹{predicted_profit:,.0f}", 
                          delta_color="normal" if predicted_profit >= 0 else "inverse")
            
            with results_col3:
                profit_margin_sim = (predicted_profit / expected_sales) * 100 if expected_sales > 0 else 0
                st.metric("Profit Margin", f"{profit_margin_sim:.1f}%")
            
            with results_col4:
                marketing_roi_sim = (predicted_profit / marketing_spend) if marketing_spend > 0 else 0
                st.metric("Marketing ROI", f"{marketing_roi_sim:.2f}x")
            
            # Additional metrics
            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
            
            with metrics_col1:
                sales_per_emp = expected_sales / employee_count if employee_count > 0 else 0
                st.metric("Sales per Employee", f"₹{sales_per_emp:,.0f}")
            
            with metrics_col2:
                inventory_turnover_sim = (expected_sales / inventory_level) if inventory_level > 0 else 0
                st.metric("Inventory Turnover", f"{inventory_turnover_sim:.1f}")
            
            with metrics_col3:
                cost_ratio = (operating_cost + salary_cost) / expected_sales * 100 if expected_sales > 0 else 0
                st.metric("Cost to Sales Ratio", f"{cost_ratio:.1f}%")

    # ============================================================
    # NEW ADVANCED VISUALIZATIONS
    # ============================================================
    # ============================================================
    # NEW ADVANCED VISUALIZATIONS (MOVED TO SEPARATE MODULE)
    # ============================================================
    # if data_loaded and df is not None:
    #     visualizations.show_advanced_visualizations(df)
    #     visualizations.show_geographic_and_premium_analytics(df)

    # ============================================================
    # DATA EXPORT - FROM FIRST CODE
    # ============================================================
    st.markdown("<h2 class='section-header'>Data Export & Reports</h2>", unsafe_allow_html=True)

    export_col1, export_col2, export_col3 = st.columns(3)

    with export_col1:
        if st.button("📥 Download Analyzed Data (CSV)"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Click to download CSV",
                data=csv,
                file_name="business_analysis_results.csv",
                mime="text/csv"
            )

    with export_col2:
        if st.button("📊 Generate Executive Summary"):
            with st.spinner("Generating executive report..."):
                summary = f"""
                BUSINESS INTELLIGENCE REPORT - BizSight AI
                ===========================================
                
                Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                Total Records Analyzed: {total_records:,}
                
                EXECUTIVE SUMMARY:
                • Average Monthly Profit: ₹{avg_profit:,.0f}
                • Average Monthly Sales: ₹{avg_sales:,.0f}
                • Overall Profit Margin: {profit_margin_val:.1f}%
                • High Risk Businesses: {risk_percentage:.1f}%
                • Average Marketing ROI: {avg_roi:.2f}x
                
                RISK PROFILE:
                • Low Risk: {((df['risk_band'] == 'Low').mean()*100):.1f}%
                • Medium Risk: {((df['risk_band'] == 'Medium').mean()*100):.1f}%
                • High Risk: {((df['risk_band'] == 'High').mean()*100):.1f}%
                
                PERFORMANCE HIGHLIGHTS:
                • Top Performing Business Type: {df.groupby('business_type')['predicted_profit'].mean().idxmax() if 'business_type' in df.columns else 'N/A'}
                • Best City for Business: {df.groupby('city')['predicted_profit'].mean().idxmax() if 'city' in df.columns else 'N/A'}
                • Average Employee Efficiency: ₹{employee_productivity:,.0f}
                
                KEY RECOMMENDATIONS:
                1. Optimize marketing spend in businesses with ROI < 2.0x
                2. Implement inventory management in high-risk units
                3. Focus on customer experience improvements
                4. Consider expansion in high-performing cities
                5. Streamline operational costs in medium-risk businesses
                
                ---
                Generated by BizSight AI Platform
                Developed by Sourish Dey
                Portfolio: https://sourishdeyportfolio.vercel.app/
                """
                st.code(summary, language="markdown")

    with export_col3:
        if st.button("🖼️ Export Visualizations (PNG)"):
            st.info("Visualization export requires Plotly's kaleido package. Install with: pip install kaleido")

    # ============================================================
    # ADDITIONAL FEATURES - FROM FIRST CODE
    # ============================================================
    with st.expander("Connect", expanded=False):
        st.markdown("""
        
        ### Contact & Support:
        - **Developer**: Sourish Dey
        - **Portfolio**: https://sourishdeyportfolio.vercel.app/
        - **Email**: sourish713321@gmail.com
        - **GitHub**: https://github.com
        
        ---
        
        """)

    # Add performance metrics from first code
    with st.sidebar.expander("📈 Performance Metrics"):
        st.metric("Data Points", f"{len(df):,}")
        st.metric("Columns Analyzed", f"{len(df.columns)}")
        st.metric("Visualizations", "48+")
        st.metric("Processing Time", "< 1 second")
        
        if model:
            st.success("✓ Predictive Model Loaded")
        else:
            st.info("⚠️ Demo Mode Active")


    # Add auto-refresh option from first code
    st.sidebar.markdown("---")
    auto_refresh = st.sidebar.checkbox("Auto-refresh data", value=False)
    if auto_refresh:
        st.sidebar.info("Auto-refresh enabled")
        st.rerun()

# ============================================================
# FOOTER - HIGH-END ENTERPRISE EDITION
# ============================================================
show_footer()

