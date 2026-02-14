import streamlit as st
import database
import time
import config

def show_auth_system():
    """
    Truly separate, premium Authentication & Authorization System.
    Gated completely from the main Dashboard.
    """
    
    # Premium Custom CSS for the Auth Gateway
    st.markdown("""
    <style>
        /* Hide sidebar during Auth */
        [data-testid="stSidebarNav"] {display: none;}
        
        .stApp {
            background-image: radial-gradient(circle at 20% 30%, rgba(234, 70, 67, 0.05) 0%, transparent 50%),
                              radial-gradient(circle at 80% 70%, rgba(234, 70, 67, 0.05) 0%, transparent 50%),
                              linear-gradient(135deg, #FFFFFF 0%, #F8F9FA 100%);
            background-attachment: fixed;
        }
        
        .auth-card {
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(20px);
            padding: 60px;
            border-radius: 50px;
            border: 1px solid rgba(234, 70, 67, 0.1);
            box-shadow: 0 40px 120px rgba(0, 0, 0, 0.08);
            max-width: 600px;
            margin: auto;
            text-align: center;
        }

        .auth-header h1 {
            background: linear-gradient(90deg, #1A202C, #EA4643);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 42px;
            font-weight: 900;
            margin-bottom: 5px;
        }
        
        .auth-badge {
            background: #FFEDED;
            color: #EA4643;
            padding: 8px 16px;
            border-radius: 100px;
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 2px;
            display: inline-block;
            margin-bottom: 25px;
        }

        .stTabs [data-baseweb="tab-list"] {
            justify-content: center;
            border-bottom: 2px solid #F1F5F9;
            margin-bottom: 30px;
        }

        .stTabs [data-baseweb="tab"] {
            font-weight: 700;
            padding: 10px 40px;
            color: #64748B;
        }

        .stTabs [aria-selected="true"] {
            color: #EA4643 !important;
            border-bottom-color: #EA4643 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 4, 1])
    
    with col2:
        # Header Area - Branding & Identification
        st.markdown('''
        <div style="text-align: center; margin-bottom: 40px;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/9/95/Infosys_logo.svg" width="180" style="margin-bottom: 20px;">
            <div style="background: #FFEDED; color: #EA4643; padding: 8px 16px; border-radius: 100px; font-size: 12px; font-weight: 800; letter-spacing: 2px; display: inline-block; margin-bottom: 20px;">ENTERPRISE COMMAND CENTER</div>
            <h1 style="background: linear-gradient(90deg, #1A202C, #EA4643); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 42px; font-weight: 900; margin-bottom: 5px;">BizSight AI</h1>
            <p style="color: #64748B; font-size: 16px;">Secure Bi-Directional Strategic Handshake</p>
        </div>
        ''', unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["🔐 SECURE LOGIN", "📝 STRATEGIC JOIN"])

        with tab_login:
            with st.form("login_center"):
                st.markdown("### Access Identification")
                email = st.text_input("Corporate Email ID", placeholder="executive@company.com")
                password = st.text_input("Access Security Key", type="password", placeholder="••••••••")
                
                spacer1, spacer2 = st.columns([1, 1])
                st.markdown("<br>", unsafe_allow_html=True)
                login_btn = st.form_submit_button("VALIDATE & LAUNCH", type="primary", use_container_width=True)

                if login_btn:
                    if email and password:
                        user = database.verify_user(email, password)
                        if user:
                            st.session_state.user = {
                                "id": user.id,
                                "email": user.email,
                                "username": user.email.split('@')[0].capitalize(),
                                "role": user.user_metadata.get('role', 'Owner')
                            }
                            st.success("✨ Authentication Verified. Initializing Global Modules...")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("🚫 Access Denied: Identification match failed.")
                    else:
                        st.warning("⚠️ Security protocol requires both Email and Key.")

        with tab_register:
            with st.form("register_center"):
                st.markdown("### Strategic Registration")
                reg_name = st.text_input("Full Executive Name")
                reg_email = st.text_input("Operational Email")
                reg_pass = st.text_input("Set Master Key", type="password")
                
                st.markdown("---")
                reg_biz = st.text_input("Corporate Entity Name")
                reg_role = st.selectbox("Strategic Designation", ["Owner", "Managing Director", "Senior Accountant"])
                
                st.markdown("<br>", unsafe_allow_html=True)
                reg_btn = st.form_submit_button("PROVISION ENTERPRISE ACCESS", type="primary", use_container_width=True)

                if reg_btn:
                    if reg_email and reg_pass:
                        success = database.create_user(reg_email, reg_pass, reg_role, reg_biz, "Enterprise", "HQ", "N/A", "N/A")
                        if success:
                            st.success("✅ Protocol complete. Please proceed to Secure Login.")
                        else:
                            st.error("❌ Registration conflict: Entity ID already active.")
                    else:
                        st.error("⚠️ Mandatory fields cannot be null for security.")
        
        
        # Footer link back to main site if needed
        st.markdown(f'<p style="text-align: center; margin-top: 30px;"><a href="{config.LOGIN_PORTAL_URL}" style="color: #64748B; text-decoration: none;">← Return to Global Landing Page</a></p>', unsafe_allow_html=True)
