import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import os
import json
import re
import time
import random
from dotenv import load_dotenv

# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

# Local .env OR Streamlit Cloud Secrets
if "GOOGLE_API_KEY" in st.secrets:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
else:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

if "GEMINI_MODEL" in st.secrets:
    GEMINI_MODEL = st.secrets["GEMINI_MODEL"]

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

st.set_page_config(
    page_title="AI Cold Email & Outreach Generator",
    page_icon="✉️",
    layout="wide"
)

# ============================================================
# SESSION STATE
# ============================================================

if "prospects" not in st.session_state:
    st.session_state.prospects = pd.DataFrame(
        columns=[
            "name",
            "company",
            "role",
            "industry",
            "pain_point",
            "custom_note"
        ]
    )

if "generated_emails" not in st.session_state:
    st.session_state.generated_emails = []

if "approved_emails" not in st.session_state:
    st.session_state.approved_emails = []

if "generation_complete" not in st.session_state:
    st.session_state.generation_complete = False


# ============================================================
# PAGE HEADER
# ============================================================

st.title("✉️ AI Cold Email & Outreach Generator")

st.markdown(
    """
Create personalized cold emails for your prospects using Gemini AI.

**Generate → Check Spam Triggers → Review → Approve → Export → Analyze**
"""
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Settings")

    tone = st.selectbox(
        "Email Tone",
        [
            "Professional",
            "Casual",
            "Friendly",
            "Concise",
            "Witty"
        ]
    )

    st.divider()

    st.subheader("🤖 AI Model")

    st.caption(GEMINI_MODEL)

    st.divider()

    st.info(
        "💡 Tip: For large prospect lists, process smaller batches "
        "to avoid API rate limits."
    )


# ============================================================
# API KEY CHECK
# ============================================================

if not GOOGLE_API_KEY:

    st.error(
        "❌ Gemini API key not found.\n\n"
        "For local use, add GOOGLE_API_KEY to your .env file.\n"
        "For Streamlit Cloud, add it under App Settings → Secrets."
    )

    st.stop()


# ============================================================
# INPUT SECTION
# ============================================================

st.header("1️⃣ Campaign Information")

col1, col2 = st.columns(2)

with col1:

    product_description = st.text_area(
        "Product / Service Description",
        height=180,
        placeholder=(
            "Example:\n"
            "We provide an AI-powered sales assistant that automates "
            "prospect research and creates personalized cold emails. "
            "It helps sales teams save time, improve email relevance, "
            "generate A/B variants, and identify spam-triggering words "
            "before outreach."
        )
    )

with col2:

    target_audience = st.text_area(
        "Target Audience",
        height=180,
        placeholder=(
            "Example:\n"
            "B2B sales teams, startup founders, sales managers, "
            "business development representatives, and companies "
            "that use outbound email campaigns."
        )
    )


# ============================================================
# PROSPECT INPUT
# ============================================================

st.header("2️⃣ Prospect Information")

input_method = st.radio(
    "Choose how you want to add prospects:",
    [
        "📁 Upload CSV",
        "✍️ Manual Entry"
    ],
    horizontal=True
)


# ============================================================
# CSV UPLOAD
# ============================================================

if input_method == "📁 Upload CSV":

    uploaded_file = st.file_uploader(
        "Upload your prospect CSV file",
        type=["csv"]
    )

    if uploaded_file is not None:

        try:

            uploaded_df = pd.read_csv(uploaded_file)

            required_columns = [
                "name",
                "company",
                "role",
                "industry"
            ]

            optional_columns = [
                "pain_point",
                "custom_note"
            ]

            missing_columns = [
                col for col in required_columns
                if col not in uploaded_df.columns
            ]

            if missing_columns:

                st.error(
                    "❌ Missing required columns: "
                    + ", ".join(missing_columns)
                )

            else:

                for col in optional_columns:

                    if col not in uploaded_df.columns:
                        uploaded_df[col] = ""

                uploaded_df = uploaded_df[
                    [
                        "name",
                        "company",
                        "role",
                        "industry",
                        "pain_point",
                        "custom_note"
                    ]
                ]

                uploaded_df = uploaded_df.fillna("")

                st.session_state.prospects = uploaded_df.copy()

                st.success(
                    f"✅ {len(uploaded_df)} prospects loaded successfully."
                )

        except Exception as e:

            st.error(f"❌ Could not read CSV: {e}")


# ============================================================
# MANUAL ENTRY
# ============================================================

else:

    st.subheader("Add Prospect")

    with st.form("manual_prospect_form"):

        col1, col2 = st.columns(2)

        with col1:

            manual_name = st.text_input(
                "Name *"
            )

            manual_company = st.text_input(
                "Company *"
            )

            manual_role = st.text_input(
                "Role *"
            )

        with col2:

            manual_industry = st.text_input(
                "Industry *"
            )

            manual_pain = st.text_input(
                "Pain Point"
            )

            manual_note = st.text_input(
                "Custom Note"
            )

        add_prospect = st.form_submit_button(
            "➕ Add Prospect"
        )

        if add_prospect:

            if not manual_name or not manual_company or not manual_role or not manual_industry:

                st.warning(
                    "Please fill in all required fields."
                )

            else:

                new_prospect = pd.DataFrame(
                    [
                        {
                            "name": manual_name,
                            "company": manual_company,
                            "role": manual_role,
                            "industry": manual_industry,
                            "pain_point": manual_pain,
                            "custom_note": manual_note
                        }
                    ]
                )

                st.session_state.prospects = pd.concat(
                    [
                        st.session_state.prospects,
                        new_prospect
                    ],
                    ignore_index=True
                )

                st.success(
                    f"Added {manual_name}."
                )

    # --------------------------------------------------------
    # MANUAL PROSPECT TABLE
    # --------------------------------------------------------

    if len(st.session_state.prospects) > 0:

        st.subheader(
            f"Current Prospects ({len(st.session_state.prospects)})"
        )

        st.dataframe(
            st.session_state.prospects,
            use_container_width=True,
            hide_index=True
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "🗑️ Remove Last Prospect",
                use_container_width=True
            ):

                st.session_state.prospects = (
                    st.session_state.prospects.iloc[:-1]
                )

                st.rerun()

        with col2:

            if st.button(
                "🧹 Clear All Prospects",
                use_container_width=True
            ):

                st.session_state.prospects = pd.DataFrame(
                    columns=[
                        "name",
                        "company",
                        "role",
                        "industry",
                        "pain_point",
                        "custom_note"
                    ]
                )

                st.session_state.generated_emails = []
                st.session_state.approved_emails = []

                st.rerun()


# ============================================================
# PROSPECT SELECTION
# ============================================================

df = st.session_state.prospects

if len(df) > 0:

    st.divider()

    st.header("3️⃣ Prospect Selection")

    total_available = len(df)

    batch_options = []

    standard_sizes = [
        5, 10, 15, 20, 25,
        30, 35, 40, 45, 50
    ]

    for size in standard_sizes:

        if size < total_available:
            batch_options.append(size)

    batch_options.append(total_available)

    batch_options = sorted(
        set(batch_options)
    )

    default_index = (
        batch_options.index(5)
        if 5 in batch_options
        else 0
    )

    prospects_to_process = st.selectbox(
        "How many prospects do you want to process?",
        batch_options,
        index=default_index,
        help=(
            "Choose how many prospects from your uploaded "
            "or manually entered list should be processed."
        )
    )

    process_df = df.head(
        int(prospects_to_process)
    ).copy()

    st.info(
        f"📋 {len(process_df)} of {total_available} "
        "prospects selected for processing."
    )

    with st.expander("👀 Preview Selected Prospects"):

        st.dataframe(
            process_df,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# SPAM CHECKER
# ============================================================

SPAM_TRIGGERS = {

    "free": "Consider replacing 'free' with a more specific benefit.",

    "guarantee": "Avoid absolute guarantees. Use evidence-based language.",

    "act now": "Replace urgency-based wording with a clear next step.",

    "limited time": "Avoid artificial urgency.",

    "urgent": "Urgency can make an email feel promotional.",

    "buy now": "Use a softer call to action.",

    "winner": "This can sound promotional or misleading.",

    "risk free": "Avoid absolute claims.",

    "100%": "Use specific evidence instead of absolute claims.",

    "click here": "Use descriptive link text instead.",

    "special offer": "Use a specific benefit instead.",

    "cheap": "Use value-focused language instead.",

    "make money": "Avoid broad financial claims.",

    "cash": "Avoid promotional financial wording.",

    "sale": "Consider using a more relevant business benefit.",

    "discount": "Avoid promotional language when possible.",

    "deal": "Use neutral terms such as opportunity or conversation."
}


def check_spam_triggers(text):

    text_lower = text.lower()

    found = []

    suggestions = []

    for trigger, suggestion in SPAM_TRIGGERS.items():

        if trigger in text_lower:

            found.append(trigger)
            suggestions.append(suggestion)

    return found, suggestions


# ============================================================
# GEMINI GENERATION
# ============================================================

def generate_email(prospect):

    prompt = f"""
You are an expert B2B cold email writer.

PRODUCT / SERVICE:
{product_description}

TARGET AUDIENCE:
{target_audience}

PROSPECT INFORMATION:
Name: {prospect.get('name', '')}
Company: {prospect.get('company', '')}
Role: {prospect.get('role', '')}
Industry: {prospect.get('industry', '')}
Pain Point: {prospect.get('pain_point', '')}
Custom Note: {prospect.get('custom_note', '')}

EMAIL TONE:
{tone}

TASK:

Create TWO personalized cold email variants for this prospect.

Variant A:
Focus primarily on the prospect's pain point.

Variant B:
Focus primarily on curiosity, relevance, and value.

IMPORTANT RULES:

1. Use the prospect's exact name.
2. Use ONLY information supplied above.
3. Do not invent company facts.
4. Do not invent achievements.
5. Do not invent technologies.
6. Do not invent statistics.
7. Reference a specific prospect detail within the first two sentences.
8. Keep the email concise and human.
9. Avoid aggressive sales language.
10. Do not use the word "deal".
11. Prefer neutral phrases such as:
    opportunity,
    conversation,
    collaboration,
    option,
    next step.
12. Avoid spam-triggering language.
13. Do not use excessive exclamation marks.
14. Do not make unrealistic claims.
15. Include a natural call to action.
16. Generate one main subject and two alternative subject lines.
17. Give each subject a relevance score from 1 to 10.

Return ONLY valid JSON.

Required format:

{{
    "variant_a": {{
        "subject": "",
        "subject_options": ["", ""],
        "subject_score": 0,
        "body": ""
    }},
    "variant_b": {{
        "subject": "",
        "subject_options": ["", ""],
        "subject_score": 0,
        "body": ""
    }}
}}
"""

    try:

        model = genai.GenerativeModel(
            GEMINI_MODEL
        )

        response = model.generate_content(
            prompt
        )

        text = response.text.strip()

        # Remove markdown JSON fences
        text = re.sub(
            r"```json",
            "",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(
            r"```",
            "",
            text
        )

        text = text.strip()

        return json.loads(text)

    except json.JSONDecodeError:

        # Try to extract JSON object
        match = re.search(
            r"\{.*\}",
            text,
            re.DOTALL
        )

        if match:

            try:

                return json.loads(
                    match.group(0)
                )

            except Exception:

                pass

        return {
            "variant_a": {
                "subject": "A relevant opportunity",
                "subject_options": [
                    "A relevant opportunity",
                    "Quick idea for your team"
                ],
                "subject_score": 5,
                "body": text
            },
            "variant_b": {
                "subject": "A quick question",
                "subject_options": [
                    "A quick question",
                    "Worth exploring?"
                ],
                "subject_score": 5,
                "body": text
            }
        }


# ============================================================
# GENERATE BUTTON
# ============================================================

if len(df) > 0:

    st.divider()

    st.header("4️⃣ Generate Personalized Emails")

    if st.button(
        "🚀 Generate A/B Emails",
        type="primary",
        use_container_width=True
    ):

        if not product_description.strip():

            st.warning(
                "Please enter your product/service description."
            )

        elif not target_audience.strip():

            st.warning(
                "Please enter your target audience."
            )

        else:

            st.session_state.generated_emails = []
            st.session_state.approved_emails = []

            progress = st.progress(0)

            status = st.empty()

            total = len(process_df)

            for index, (_, prospect) in enumerate(
                process_df.iterrows()
            ):

                status.info(
                    f"Generating email {index + 1} of "
                    f"{total}: {prospect['name']}"
                )

                try:

                    result = generate_email(
                        prospect
                    )

                    variant_a = result.get(
                        "variant_a",
                        {}
                    )

                    variant_b = result.get(
                        "variant_b",
                        {}
                    )

                    # Spam check A
                    spam_a_text = (
                        variant_a.get("subject", "")
                        + " "
                        + variant_a.get("body", "")
                    )

                    spam_a, suggestions_a = (
                        check_spam_triggers(
                            spam_a_text
                        )
                    )

                    # Spam check B
                    spam_b_text = (
                        variant_b.get("subject", "")
                        + " "
                        + variant_b.get("body", "")
                    )

                    spam_b, suggestions_b = (
                        check_spam_triggers(
                            spam_b_text
                        )
                    )

                    email_record = {

                        "name": prospect["name"],
                        "company": prospect["company"],
                        "role": prospect["role"],
                        "industry": prospect["industry"],
                        "pain_point": prospect["pain_point"],
                        "custom_note": prospect["custom_note"],

                        "variant_a": variant_a,
                        "variant_b": variant_b,

                        "spam_a": spam_a,
                        "suggestions_a": suggestions_a,

                        "spam_b": spam_b,
                        "suggestions_b": suggestions_b,

                        "approved_variant": None,
                        "approved": False
                    }

                    st.session_state.generated_emails.append(
                        email_record
                    )

                except Exception as e:

                    st.error(
                        f"Failed for {prospect['name']}: {e}"
                    )

                progress.progress(
                    (index + 1) / total
                )

                # Delay to reduce API pressure
                if index < total - 1:
                    time.sleep(4)

            status.success(
                f"✅ Generated emails for "
                f"{len(st.session_state.generated_emails)} prospects."
            )

            st.session_state.generation_complete = True


# ============================================================
# REVIEW SECTION
# ============================================================

if st.session_state.generated_emails:

    st.divider()

    st.header("5️⃣ Review & Approve")

    st.caption(
        "Review, edit, choose a variant, and approve each email."
    )

    for index, email in enumerate(
        st.session_state.generated_emails
    ):

        with st.expander(
            f"👤 {email['name']} — "
            f"{email['company']}",
            expanded=False
        ):

            st.markdown(
                f"**Role:** {email['role']}  \n"
                f"**Industry:** {email['industry']}"
            )

            if email["pain_point"]:

                st.markdown(
                    f"**Pain Point:** {email['pain_point']}"
                )

            st.divider()

            col_a, col_b = st.columns(2)

            # ------------------------------------------------
            # VARIANT A
            # ------------------------------------------------

            with col_a:

                st.subheader(
                    "🅰️ Variant A — Pain Point"
                )

                subject_a = st.text_input(
                    "Subject A",
                    value=email["variant_a"].get(
                        "subject",
                        ""
                    ),
                    key=f"subject_a_{index}"
                )

                body_a = st.text_area(
                    "Body A",
                    value=email["variant_a"].get(
                        "body",
                        ""
                    ),
                    height=260,
                    key=f"body_a_{index}"
                )

                score_a = email["variant_a"].get(
                    "subject_score",
                    0
                )

                st.metric(
                    "Subject Score",
                    f"{score_a}/10"
                )

                if email["variant_a"].get(
                    "subject_options"
                ):

                    st.write(
                        "Alternative subjects:"
                    )

                    for option in email["variant_a"].get(
                        "subject_options",
                        []
                    ):

                        st.caption(
                            f"• {option}"
                        )

                if email["spam_a"]:

                    st.warning(
                        "⚠️ Spam triggers: "
                        + ", ".join(
                            email["spam_a"]
                        )
                    )

                    for suggestion in email[
                        "suggestions_a"
                    ]:

                        st.caption(
                            f"💡 {suggestion}"
                        )

                else:

                    st.success(
                        "✅ No common spam triggers detected."
                    )

            # ------------------------------------------------
            # VARIANT B
            # ------------------------------------------------

            with col_b:

                st.subheader(
                    "🅱️ Variant B — Curiosity / Value"
                )

                subject_b = st.text_input(
                    "Subject B",
                    value=email["variant_b"].get(
                        "subject",
                        ""
                    ),
                    key=f"subject_b_{index}"
                )

                body_b = st.text_area(
                    "Body B",
                    value=email["variant_b"].get(
                        "body",
                        ""
                    ),
                    height=260,
                    key=f"body_b_{index}"
                )

                score_b = email["variant_b"].get(
                    "subject_score",
                    0
                )

                st.metric(
                    "Subject Score",
                    f"{score_b}/10"
                )

                if email["variant_b"].get(
                    "subject_options"
                ):

                    st.write(
                        "Alternative subjects:"
                    )

                    for option in email["variant_b"].get(
                        "subject_options",
                        []
                    ):

                        st.caption(
                            f"• {option}"
                        )

                if email["spam_b"]:

                    st.warning(
                        "⚠️ Spam triggers: "
                        + ", ".join(
                            email["spam_b"]
                        )
                    )

                    for suggestion in email[
                        "suggestions_b"
                    ]:

                        st.caption(
                            f"💡 {suggestion}"
                        )

                else:

                    st.success(
                        "✅ No common spam triggers detected."
                    )

            st.divider()

            selected_variant = st.radio(
                "Choose email variant:",
                [
                    "Variant A",
                    "Variant B"
                ],
                horizontal=True,
                key=f"variant_{index}"
            )

            if selected_variant == "Variant A":

                selected_subject = subject_a
                selected_body = body_a

            else:

                selected_subject = subject_b
                selected_body = body_b

            if st.button(
                "✅ Approve Selected Email",
                key=f"approve_{index}",
                use_container_width=True
            ):

                # Prevent duplicate approvals
                st.session_state.approved_emails = [
                    item
                    for item in st.session_state.approved_emails
                    if item["name"] != email["name"]
                ]

                approved_record = {

                    "name": email["name"],
                    "company": email["company"],
                    "role": email["role"],
                    "industry": email["industry"],

                    "variant": selected_variant,

                    "subject": selected_subject,
                    "body": selected_body,

                    "spam_flags": (
                        email["spam_a"]
                        if selected_variant == "Variant A"
                        else email["spam_b"]
                    )
                }

                st.session_state.approved_emails.append(
                    approved_record
                )

                st.success(
                    f"✅ Approved {selected_variant} "
                    f"for {email['name']}"
                )


# ============================================================
# EXPORT SECTION
# ============================================================

if st.session_state.approved_emails:

    st.divider()

    st.header("6️⃣ Approved Emails")

    approved_df = pd.DataFrame(
        st.session_state.approved_emails
    )

    display_df = approved_df[
        [
            "name",
            "company",
            "role",
            "variant",
            "subject"
        ]
    ]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    csv_data = approved_df.to_csv(
        index=False
    )

    st.download_button(
        "📥 Download Approved Emails CSV",
        data=csv_data,
        file_name="approved_cold_emails.csv",
        mime="text/csv",
        use_container_width=True
    )

    # --------------------------------------------------------
    # COPY READY EMAILS
    # --------------------------------------------------------

    st.subheader(
        "📋 Copy-Ready Emails"
    )

    for email in st.session_state.approved_emails:

        with st.expander(
            f"{email['name']} — {email['company']}"
        ):

            copy_text = (
                f"Subject: {email['subject']}\n\n"
                f"{email['body']}"
            )

            st.code(
                copy_text,
                language="text"
            )


# ============================================================
# MOCK ANALYTICS
# ============================================================

if st.session_state.approved_emails:

    st.divider()

    st.header("7️⃣ 📊 Campaign Analytics")

    st.info(
        "ℹ️ **Mock Analytics:** The performance numbers below "
        "are simulated for demonstration purposes. They do not "
        "represent real email delivery, open, or reply data."
    )

    approved_df = pd.DataFrame(
        st.session_state.approved_emails
    )

    total_approved = len(
        approved_df
    )

    # --------------------------------------------------------
    # Generate deterministic mock metrics
    # --------------------------------------------------------

    random.seed(
        1000 + total_approved
    )

    total_sent = total_approved

    delivered = max(
        0,
        int(
            total_sent * random.uniform(
                0.94,
                0.99
            )
        )
    )

    opened = max(
        0,
        int(
            delivered * random.uniform(
                0.62,
                0.82
            )
        )
    )

    replied = max(
        0,
        int(
            opened * random.uniform(
                0.18,
                0.35
            )
        )
    )

    positive_replies = max(
        0,
        int(
            replied * random.uniform(
                0.55,
                0.80
            )
        )
    )

    delivery_rate = (
        delivered / total_sent * 100
        if total_sent
        else 0
    )

    open_rate = (
        opened / delivered * 100
        if delivered
        else 0
    )

    reply_rate = (
        replied / delivered * 100
        if delivered
        else 0
    )

    positive_rate = (
        positive_replies / replied * 100
        if replied
        else 0
    )

    # --------------------------------------------------------
    # Metric Cards
    # --------------------------------------------------------

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:

        st.metric(
            "Emails Sent",
            total_sent
        )

    with col2:

        st.metric(
            "Delivery Rate",
            f"{delivery_rate:.1f}%"
        )

    with col3:

        st.metric(
            "Open Rate",
            f"{open_rate:.1f}%"
        )

    with col4:

        st.metric(
            "Reply Rate",
            f"{reply_rate:.1f}%"
        )

    with col5:

        st.metric(
            "Positive Replies",
            positive_replies
        )

    st.divider()

    # --------------------------------------------------------
    # A/B Analytics
    # --------------------------------------------------------

    st.subheader(
        "🔄 A/B Variant Performance"
    )

    variant_a_count = len(
        approved_df[
            approved_df["variant"] == "Variant A"
        ]
    )

    variant_b_count = len(
        approved_df[
            approved_df["variant"] == "Variant B"
        ]
    )

    # Simulated performance values
    random.seed(
        2000 + total_approved
    )

    variant_a_open_rate = random.uniform(
        62,
        78
    )

    variant_b_open_rate = random.uniform(
        65,
        83
    )

    variant_a_reply_rate = random.uniform(
        15,
        28
    )

    variant_b_reply_rate = random.uniform(
        18,
        34
    )

    analytics_df = pd.DataFrame(
        {
            "Variant": [
                "Variant A",
                "Variant B"
            ],
            "Emails": [
                variant_a_count,
                variant_b_count
            ],
            "Mock Open Rate": [
                round(
                    variant_a_open_rate,
                    1
                ),
                round(
                    variant_b_open_rate,
                    1
                )
            ],
            "Mock Reply Rate": [
                round(
                    variant_a_reply_rate,
                    1
                ),
                round(
                    variant_b_reply_rate,
                    1
                )
            ]
        }
    )

    st.dataframe(
        analytics_df,
        use_container_width=True,
        hide_index=True
    )

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:

        st.write(
            "**Mock Open Rate Comparison**"
        )

        open_chart = analytics_df.set_index(
            "Variant"
        )[["Mock Open Rate"]]

        st.bar_chart(
            open_chart
        )

    with chart_col2:

        st.write(
            "**Mock Reply Rate Comparison**"
        )

        reply_chart = analytics_df.set_index(
            "Variant"
        )[["Mock Reply Rate"]]

        st.bar_chart(
            reply_chart
        )

    # --------------------------------------------------------
    # Funnel
    # --------------------------------------------------------

    st.subheader(
        "📈 Mock Campaign Funnel"
    )

    funnel_df = pd.DataFrame(
        {
            "Stage": [
                "Sent",
                "Delivered",
                "Opened",
                "Replied",
                "Positive Reply"
            ],
            "Count": [
                total_sent,
                delivered,
                opened,
                replied,
                positive_replies
            ]
        }
    )

    st.dataframe(
        funnel_df,
        use_container_width=True,
        hide_index=True
    )

    st.bar_chart(
        funnel_df.set_index("Stage")
    )

    # --------------------------------------------------------
    # Prospect-Level Analytics
    # --------------------------------------------------------

    st.subheader(
        "👥 Prospect-Level Mock Results"
    )

    random.seed(
        3000 + total_approved
    )

    prospect_results = []

    for _, row in approved_df.iterrows():

        delivered_status = random.choice(
            [
                "Delivered",
                "Delivered",
                "Delivered",
                "Delivered",
                "Bounced"
            ]
        )

        if delivered_status == "Bounced":

            opened_status = "No"
            replied_status = "No"
            response_type = "—"

        else:

            opened_status = random.choice(
                [
                    "Yes",
                    "Yes",
                    "Yes",
                    "No"
                ]
            )

            if opened_status == "Yes":

                replied_status = random.choice(
                    [
                        "Yes",
                        "No",
                        "No",
                        "No"
                    ]
                )

                if replied_status == "Yes":

                    response_type = random.choice(
                        [
                            "Positive",
                            "Positive",
                            "Neutral"
                        ]
                    )

                else:

                    response_type = "—"

            else:

                replied_status = "No"
                response_type = "—"

        prospect_results.append(
            {
                "Name": row["name"],
                "Company": row["company"],
                "Variant": row["variant"],
                "Delivered": delivered_status,
                "Opened": opened_status,
                "Replied": replied_status,
                "Response": response_type
            }
        )

    prospect_analytics_df = pd.DataFrame(
        prospect_results
    )

    st.dataframe(
        prospect_analytics_df,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "⚠️ All delivery/open/reply values in this section "
        "are simulated demonstration data."
    )


# ============================================================
# CAMPAIGN SUMMARY
# ============================================================

st.divider()

st.header("📌 Campaign Summary")

processed_count = len(
    st.session_state.generated_emails
)

approved_count = len(
    st.session_state.approved_emails
)

spam_flag_count = 0

for email in st.session_state.generated_emails:

    if email["spam_a"] or email["spam_b"]:

        spam_flag_count += 1

approval_rate = (
    approved_count / processed_count * 100
    if processed_count
    else 0
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Prospects Processed",
        processed_count
    )

with col2:

    st.metric(
