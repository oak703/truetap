import re
import streamlit as st

st.set_page_config(page_title="TrueTap — Verify before you trust", page_icon="✓", layout="wide")

st.markdown("""
<style>
.stApp{background:#07111f;color:#f5f7fa}.block-container{max-width:1100px;padding-top:2rem}
h1,h2,h3{color:#f5f7fa}.hero{padding:2.2rem;border:1px solid #18314b;border-radius:20px;background:#0b1b2e}
.badge{display:inline-block;padding:6px 12px;border-radius:20px;background:#102b40;color:#55d6ff;font-weight:700}
.card{padding:1.3rem;border:1px solid #18314b;border-radius:16px;background:#0b1726;min-height:170px}
.small{color:#9fb1c5}.verdict{padding:1rem;border-radius:14px;border:1px solid #28435c;background:#0b1726}
</style>
""", unsafe_allow_html=True)

if "page" not in st.session_state: st.session_state.page="Home"
with st.sidebar:
    st.markdown("## TrueTap")
    st.caption("Verify before you trust.")
    pages=["Home","Verify Payment","Check Message / Link","Judge Demo","How it works"]
    st.session_state.page=st.radio("Navigate",pages,index=pages.index(st.session_state.page))
    st.divider()
    st.selectbox("Language",["English","தமிழ்"])

page=st.session_state.page

def verdict_box(title,text):
    st.markdown(f'<div class="verdict"><h3>{title}</h3><p>{text}</p></div>',unsafe_allow_html=True)

def analyze_message(message):
    text=message.lower(); reasons=[]
    urgency=any(x in text for x in ["urgent","immediately","within 10 minutes","within 15 minutes","account will be blocked","act now","verify now"])
    sensitive=any(x in text for x in ["kyc","otp","password","pin","upi pin","bank details","card details","login","refund"])
    shortener=any(x in text for x in ["bit.ly/","tinyurl.com/","t.co/","is.gd/"])
    urls=re.findall(r'https?://\S+',message)
    punycode=any("xn--" in u.lower() for u in urls)
    raw_ip=any(re.search(r'https?://\d{1,3}(?:\.\d{1,3}){3}',u) for u in urls)
    at_symbol=any("@" in u for u in urls)
    if urgency: reasons.append("Urgency language is present.")
    if sensitive: reasons.append("The message asks for a sensitive action or information.")
    if shortener: reasons.append("A URL shortener is present.")
    if punycode: reasons.append("A punycode/lookalike domain was detected.")
    if raw_ip: reasons.append("The link uses a raw IP address.")
    if at_symbol: reasons.append("The URL contains '@', which can hide the actual destination.")
    return ("HIGH RISK" if len(reasons)>=3 else "SUSPICIOUS" if reasons else "LOW RISK",
            reasons or ["No obvious high-risk indicators were detected by the current rules."])

if page=="Home":
    st.markdown('<div class="hero"><span class="badge">NEXORA • HACKATHON MVP</span><h1 style="font-size:3.2rem">TrueTap</h1><p style="font-size:1.35rem">Verify before you trust.</p><p class="small">A merchant-first fraud screening prototype for suspicious payment receipts, messages and links.</p></div>',unsafe_allow_html=True)
    st.write("")
    c1,c2=st.columns(2)
    with c1: st.markdown('<div class="card"><h2>✓ Verify Payment</h2><p>Screen a payment receipt for visible inconsistencies such as amount, reference and timestamp signals.</p></div>',unsafe_allow_html=True)
    with c2: st.markdown('<div class="card"><h2>⌕ Check Message / Link</h2><p>Detect urgency, credential requests, shortened links and other common phishing indicators.</p></div>',unsafe_allow_html=True)
    st.write(""); st.markdown("### Simple merchant flow")
    for col,(n,t) in zip(st.columns(4),[("01","Paste / upload"),("02","Scan signals"),("03","See evidence"),("04","Verify safely")]):
        with col: st.markdown(f"**{n}**  
{t}")
    st.info("Important: a screenshot alone cannot prove that money reached a bank account. Confirm payment in the trusted banking/payment app before handing over goods.")

elif page=="Verify Payment":
    st.title("Verify Payment"); st.caption("MVP screening — not independent payment confirmation.")
    mode=st.radio("Choose mode",["Demo scenario","Upload receipt"],horizontal=True)
    if mode=="Demo scenario":
        st.success("Demo receipt loaded.")
        st.markdown("**Synthetic receipt**\n\nAmount: ₹2,500  \nReference: `UPI24AB7X9K21`  \nTimestamp: 10:42 AM")
        st.markdown("### Evidence checks")
        for name,result in [("Reference format","Looks structurally plausible"),("Amount consistency","Visible amount can be extracted"),("Timestamp","Visible timestamp can be extracted"),("Payment confirmation","Not available from screenshot alone")]:
            st.write(f"**{name}:** {result}")
        verdict_box("AMBER — VERIFY IN BANK APP","The receipt has usable visible fields, but the screenshot does not independently confirm settlement.")
    else:
        uploaded=st.file_uploader("Upload a receipt image",type=["png","jpg","jpeg"])
        if uploaded:
            st.image(uploaded,caption="Uploaded receipt",use_container_width=True)
            st.warning("Basic image received. Use the visible receipt fields and verify the transaction in the trusted payment/banking app.")
            st.code("PAYMENT NOT INDEPENDENTLY CONFIRMED")
        else: st.info("Upload a PNG/JPG receipt to test the flow.")

elif page=="Check Message / Link":
    st.title("Check Message / Link")
    examples={"High-risk KYC":"URGENT: Your KYC will expire today. Verify immediately at https://bit.ly/3FakeKyc","Suspicious refund":"Refund pending. Login now and confirm your UPI PIN at https://tinyurl.com/refund-check","Normal message":"Your order is ready for pickup. Please bring your order ID to the store."}
    choice=st.selectbox("Try an example",list(examples)); message=st.text_area("Paste SMS / WhatsApp message / URL",examples[choice],height=150)
    if st.button("Analyze message",type="primary"):
        risk,reasons=analyze_message(message)
        {"HIGH RISK":st.error,"SUSPICIOUS":st.warning,"LOW RISK":st.success}[risk](risk)
        st.markdown("### Why?")
        for r in reasons: st.write("• "+r)
        st.info("Never share OTP, PIN or passwords through a link. Open the official app/site yourself when verification is needed.")

elif page=="Judge Demo":
    st.title("Judge Demo"); st.caption("Three short scenarios to demonstrate the MVP.")
    for title,desc in [("Fake payment screenshot","Receipt image appears plausible → TrueTap flags that a screenshot cannot independently confirm settlement."),("KYC phishing link","Urgency + KYC request + shortened URL → HIGH RISK."),("Normal pickup message","No obvious risky indicators → LOW RISK under the current rules.")]:
        with st.expander(title,expanded=True): st.write(desc)

else:
    st.title("How TrueTap works")
    st.markdown("""### Architecture
**User input → OCR / text extraction → explainable rules → risk signals → verdict → safe verification guidance**

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
""")
    st.success("Design principle: explain the evidence behind every warning instead of presenting an unexplained trust score.")
