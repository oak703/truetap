import re
import streamlit as st

st.set_page_config(
    page_title="TrueTap — Verify before you trust",
    page_icon="✓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown("""
<style>
.stApp {
    background: #07111f;
    color: #f5f7fa;
}
.block-container {
    max-width: 1150px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}
h1, h2, h3 {
    color: #f5f7fa;
}
.hero {
    padding: 2.4rem;
    border: 1px solid #18314b;
    border-radius: 22px;
    background: linear-gradient(135deg, #0b1b2e, #0a1625);
    margin-bottom: 1.2rem;
}
.badge {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 20px;
    background: #102b40;
    color: #55d6ff;
    font-weight: 700;
    font-size: 0.85rem;
}
.card {
    padding: 1.4rem;
    border: 1px solid #18314b;
    border-radius: 16px;
    background: #0b1726;
    min-height: 175px;
}
.small {
    color: #9fb1c5;
}
.verdict {
    padding: 1rem;
    border-radius: 14px;
    border: 1px solid #28435c;
    background: #0b1726;
}
.flow-card {
    padding: 1rem;
    border: 1px solid #18314b;
    border-radius: 14px;
    background: #0b1726;
    text-align: center;
    min-height: 105px;
}
div.stButton > button {
    width: 100%;
}
</style>
""", unsafe_allow_html=True)


# ---------- Helpers ----------
def go_to(page):
    st.session_state.page = page
    st.rerun()


def verdict_box(title, message):
    st.markdown(
        f'<div class="verdict"><h3>{title}</h3><p>{message}</p></div>',
        unsafe_allow_html=True,
    )


def analyze_message(message):
    text = message.lower()
    reasons = []

    urgency = any(
        x in text
        for x in [
            "urgent",
            "immediately",
            "within 10 minutes",
            "within 15 minutes",
            "account will be blocked",
            "act now",
            "verify now",
        ]
    )

    sensitive = any(
        x in text
        for x in [
            "kyc",
            "otp",
            "password",
            "pin",
            "upi pin",
            "bank details",
            "card details",
            "login",
            "refund",
        ]
    )

    shortener = any(
        x in text
        for x in [
            "bit.ly/",
            "tinyurl.com/",
            "t.co/",
            "is.gd/",
        ]
    )

    urls = re.findall(r"https?://\S+", message)
    punycode = any("xn--" in url.lower() for url in urls)
    raw_ip = any(
        re.search(r"https?://\d{1,3}(?:\.\d{1,3}){3}", url)
        for url in urls
    )
    at_symbol = any("@" in url for url in urls)

    if urgency:
        reasons.append("Urgency language is present.")
    if sensitive:
        reasons.append("The message asks for a sensitive action or information.")
    if shortener:
        reasons.append("A URL shortener is present.")
    if punycode:
        reasons.append("A punycode/lookalike domain was detected.")
    if raw_ip:
        reasons.append("The link uses a raw IP address.")
    if at_symbol:
        reasons.append("The URL contains '@', which can hide the actual destination.")

    if len(reasons) >= 3:
        risk = "HIGH RISK"
    elif reasons:
        risk = "SUSPICIOUS"
    else:
        risk = "LOW RISK"

    return risk, reasons or [
        "No obvious high-risk indicators were detected by the current rules."
    ]


# ---------- Session state ----------
if "page" not in st.session_state:
    st.session_state.page = "Home"


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## TrueTap")
    st.caption("Verify before you trust.")
    st.divider()

    pages = [
        "Home",
        "Verify Payment",
        "Check Message / Link",
        "Judge Demo",
        "How it works",
    ]

    selected = st.radio(
        "Navigate",
        pages,
        index=pages.index(st.session_state.page),
    )

    if selected != st.session_state.page:
        st.session_state.page = selected
        st.rerun()

    st.divider()
    st.caption("NEXORA • Hackathon MVP")
    st.caption("Tamil + English ready")


page = st.session_state.page


# ---------- Home ----------
if page == "Home":
    st.markdown(
        """
        <div class="hero">
            <span class="badge">NEXORA • HACKATHON MVP</span>
            <h1 style="font-size:3.4rem; margin-bottom:0.2rem;">TrueTap</h1>
            <p style="font-size:1.4rem;">Verify before you trust.</p>
            <p class="small">
                A merchant-first fraud screening prototype for suspicious
                payment receipts, messages and links.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Choose what you want to verify")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(
            """
            <div class="card">
                <h2>✓ Verify Payment</h2>
                <p>
                Screen a payment receipt for visible inconsistencies such as
                amount, reference and timestamp signals.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open Payment Verification →", key="home_payment"):
            go_to("Verify Payment")

    with c2:
        st.markdown(
            """
            <div class="card">
                <h2>⌕ Check Message / Link</h2>
                <p>
                Detect urgency, credential requests, shortened links and
                other common phishing indicators.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open Message / Link Checker →", key="home_message"):
            go_to("Check Message / Link")

    st.write("")
    st.markdown("### Simple merchant flow")

    flow = [
        ("01", "Paste / upload"),
        ("02", "Scan signals"),
        ("03", "See evidence"),
        ("04", "Verify safely"),
    ]

    cols = st.columns(4)
    for col, (number, text_value) in zip(cols, flow):
        with col:
            st.markdown(
                f"""
                <div class="flow-card">
                    <h3>{number}</h3>
                    <p>{text_value}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    st.info(
        "Important: a screenshot alone cannot prove that money reached a "
        "bank account. Confirm payment in the trusted banking/payment app "
        "before handing over goods."
    )

    st.markdown("### Quick demo")
    d1, d2, d3 = st.columns(3)

    with d1:
        if st.button("Payment Demo", key="quick_payment"):
            go_to("Verify Payment")

    with d2:
        if st.button("Phishing Demo", key="quick_phishing"):
            go_to("Check Message / Link")

    with d3:
        if st.button("Judge Demo", key="quick_judge"):
            go_to("Judge Demo")


# ---------- Verify Payment ----------
elif page == "Verify Payment":
    st.title("Verify Payment")
    st.caption("MVP screening — not independent payment confirmation.")

    mode = st.radio(
        "Choose mode",
        ["Demo scenario", "Upload receipt"],
        horizontal=True,
    )

    if mode == "Demo scenario":
        st.success("Demo receipt loaded.")

        st.markdown(
            """
            ### Synthetic receipt

            **Amount:** ₹2,500

            **Reference:** `UPI24AB7X9K21`

            **Timestamp:** 10:42 AM
            """
        )

        st.markdown("### Evidence checks")

        checks = [
            ("Reference format", "Looks structurally plausible"),
            ("Amount consistency", "Visible amount can be extracted"),
            ("Timestamp", "Visible timestamp can be extracted"),
            (
                "Payment confirmation",
                "Not available from screenshot alone",
            ),
        ]

        for name, result in checks:
            st.write(f"**{name}:** {result}")

        verdict_box(
            "AMBER — VERIFY IN BANK APP",
            "The receipt has usable visible fields, but the screenshot "
            "does not independently confirm settlement.",
        )

    else:
        uploaded = st.file_uploader(
            "Upload a receipt image",
            type=["png", "jpg", "jpeg"],
        )

        if uploaded:
            st.image(
                uploaded,
                caption="Uploaded receipt",
                use_container_width=True,
            )
            st.warning(
                "Basic image received. Use the visible receipt fields and "
                "verify the transaction in the trusted payment/banking app."
            )
            st.code("PAYMENT NOT INDEPENDENTLY CONFIRMED")
        else:
            st.info("Upload a PNG/JPG receipt to test the flow.")


# ---------- Message / Link ----------
elif page == "Check Message / Link":
    st.title("Check Message / Link")
    st.caption("Explainable phishing-risk screening for common warning signs.")

    examples = {
        "High-risk KYC":
            "URGENT: Your KYC will expire today. "
            "Verify immediately at https://bit.ly/3FakeKyc",

        "Suspicious refund":
            "Refund pending. Login now and confirm your UPI PIN at "
            "https://tinyurl.com/refund-check",

        "Normal message":
            "Your order is ready for pickup. "
            "Please bring your order ID to the store.",
    }

    choice = st.selectbox("Try an example", list(examples))

    message = st.text_area(
        "Paste SMS / WhatsApp message / URL",
        examples[choice],
        height=160,
    )

    if st.button("Analyze message", type="primary"):
        risk, reasons = analyze_message(message)

        if risk == "HIGH RISK":
            st.error(risk)
        elif risk == "SUSPICIOUS":
            st.warning(risk)
        else:
            st.success(risk)

        st.markdown("### Why?")

        for reason in reasons:
            st.write("• " + reason)

        st.info(
            "Never share OTP, PIN or passwords through a link. "
            "Open the official app/site yourself when verification is needed."
        )


# ---------- Judge Demo ----------
elif page == "Judge Demo":
    st.title("Judge Demo")
    st.caption("Three short scenarios to demonstrate the MVP.")

    scenarios = [
        (
            "1. Fake payment screenshot",
            "Receipt image appears plausible → TrueTap flags that a "
            "screenshot cannot independently confirm settlement.",
        ),
        (
            "2. KYC phishing link",
            "Urgency + KYC request + shortened URL → HIGH RISK.",
        ),
        (
            "3. Normal pickup message",
            "No obvious risky indicators → LOW RISK under the current rules.",
        ),
    ]

    for title, description in scenarios:
        with st.expander(title, expanded=True):
            st.write(description)

    st.markdown("### Live demo shortcuts")
    a, b = st.columns(2)

    with a:
        if st.button("Run Payment Demo", key="judge_payment"):
            go_to("Verify Payment")

    with b:
        if st.button("Run Phishing Demo", key="judge_phishing"):
            go_to("Check Message / Link")


# ---------- How it works ----------
else:
    st.title("How TrueTap works")

    st.markdown(
        """
        ### Architecture

        **User input → OCR / text extraction → explainable rules →
        risk signals → verdict → safe verification guidance**

        ### Receipt checks

        - Visible amount, time and reference extraction
        - Reference-format checks
        - Basic consistency checks
        - Optional image-forensics signals
        - Clear warning that screenshots are not proof of settlement

        ### Message / link checks

        - Urgency language
        - Requests for OTP, PIN, password or KYC action
        - URL shorteners
        - Punycode/lookalike domains
        - Raw IP addresses
        - Suspicious URL structure

        ### Roadmap

        1. Better OCR and receipt templates
        2. Safe URL reputation integration
        3. Tamil + English voice interaction
        4. Shared scam-report intelligence with privacy controls
        """
    )

    st.success(
        "Design principle: explain the evidence behind every warning "
        "instead of presenting an unexplained trust score."
    )
