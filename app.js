// Supabase Configuration
const SUPABASE_URL = "https://kckawsrcgfzterietkht.supabase.co";
const SUPABASE_KEY = "sb_publishable_9yDAvXAM_AoSgB0wUD2_IQ_-af6ODLr";

// Redirect URL for Streamlit App
const STREAMLIT_URL = "http://localhost:8501";

let supabaseClient;

// DOM Elements
const loader = document.getElementById('loader');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const loginTab = document.getElementById('login-tab');
const registerTab = document.getElementById('register-tab');

// Utility Functions
function showLoader() { if (loader) loader.style.display = 'flex'; }
function hideLoader() { if (loader) loader.style.display = 'none'; }

// Initialize and Check Auth
async function initAuth() {
    try {
        if (typeof supabase === 'undefined') {
            console.warn("Supabase not found yet, waiting...");
            return;
        }

        supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
        const { data: { session } } = await supabaseClient.auth.getSession();

        if (session) {
            window.location.href = STREAMLIT_URL;
        }
    } catch (err) {
        console.error("Auth init error:", err);
    } finally {
        hideLoader();
    }
}

// Start everything
document.addEventListener('DOMContentLoaded', () => {
    // Force hide loader immediately on load to prevent stuck spinner
    hideLoader();

    // Tiny delay to ensure external CDN scripts are ready
    setTimeout(initAuth, 100);
});

// Tab Switching
if (loginTab && registerTab) {
    loginTab.onclick = () => {
        loginTab.classList.add('active');
        registerTab.classList.remove('active');
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
    };

    registerTab.onclick = () => {
        registerTab.classList.add('active');
        loginTab.classList.remove('active');
        loginForm.classList.add('hidden');
        registerForm.classList.remove('hidden');
    };
}

// Login Logic
if (loginForm) {
    loginForm.onsubmit = async (e) => {
        e.preventDefault();
        showLoader();

        try {
            const email = document.getElementById('login-email').value;
            const password = document.getElementById('login-password').value;

            const { data, error } = await supabaseClient.auth.signInWithPassword({ email, password });

            if (error) {
                alert("Login Error: " + error.message);
                hideLoader();
            } else {
                window.location.href = STREAMLIT_URL;
            }
        } catch (err) {
            alert("Connection error occurred.");
            hideLoader();
        }
    };
}

// Registration Logic
if (registerForm) {
    registerForm.onsubmit = async (e) => {
        e.preventDefault();
        showLoader();

        try {
            const email = document.getElementById('reg-email').value;
            const password = document.getElementById('reg-password').value;
            const fullName = document.getElementById('reg-name').value;
            const biz = document.getElementById('reg-biz').value;

            const { data, error } = await supabaseClient.auth.signUp({
                email,
                password,
                options: {
                    data: { full_name: fullName, biz_name: biz }
                }
            });

            if (error) {
                alert("Registration Error: " + error.message);
                hideLoader();
            } else {
                alert("Account created! You can now sign in.");
                loginTab.click();
                hideLoader();
            }
        } catch (err) {
            alert("Connectivity issue.");
            hideLoader();
        }
    };
}
