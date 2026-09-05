import streamlit as st
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import re
import time

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Cold Email & Outreach Generator",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.1-flash-lite"
)

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


# ============================================================
# SESSION STATE
# ============================================================

if "manual_prospects" not in st.session_state:
    st.session_state.manual_prospects = []

if "generated_results" not in st.session_state:
    st.session_state.generated_results = []


# ============================================================
# SPAM TRIGGER WORDS
# ============================================================

SPAM_TRIGGERS = {
    "free": "Use a value-focused phrase instead of a promotional claim.",
    "guarantee": "Avoid absolute promises. Use a specific, verifiable benefit.",
    "act now": "Use a softer CTA such as 'Would you be open to a conversation?'",
    "limited time": "Avoid artificial urgency unless the deadline is genuine.",
    "urgent": "Use neutral language instead of pressure-based wording.",
    "buy now": "Replace with a conversational CTA.",
    "winner": "Avoid promotional or contest-style wording.",
    "risk free": "Avoid absolute claims about risk.",
    "100%": "Avoid absolute claims unless they can be verified.",
    "click here": "Use descriptive CTA wording instead.",
    "special offer": "Describe the actual value rather than using promotional language.",
    "cheap": "Use 'cost-effective' or explain the value.",
    "make money": "Describe the specific business outcome.",
    "cash": "Avoid unnecessary promotional money-related language.",
    "sale": "Use neutral business language.",
    "discount": "Use only when a genuine discount is relevant.",
    "deal": "Use 'opportunity', 'conversation', or 'option' instead."
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_text(value):
    """Convert empty/NaN values into clean strings."""

    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass

    return str(value).strip()


def check_spam(text):
    """Check email text against configured spam-trigger words."""

    text_lower = text.lower()
    found_words = []

    for trigger in SPAM_TRIGGERS:

        if " " in trigger:

            if trigger in text_lower:
                found_words.append(trigger)

        else:

            pattern = r"\b" + re.escape(trigger) + r"\b"

            if re.search(pattern, text_lower):
                found_words.append(trigger)

    return found_words


def get_spam_suggestions(words):

    suggestions = []

    for word in words:

        suggestion = SPAM_TRIGGERS.get(word)

        if suggestion:
            suggestions.append(
                f"**{word}** → {suggestion}"
            )

    return suggestions


def clean_json_response(text):

    text = text.strip()

    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"^```\s*",
        "",
        text
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    return text.strip()


# ============================================================
# AI EMAIL GENERATION
# ============================================================

def generate_emails(
    product_description,
    target_audience,
    prospect,
    tone
):

    model = genai.GenerativeModel(MODEL_NAME)

    name = safe_text(prospect.get("name"))
    company = safe_text(prospect.get("company"))
    role = safe_text(prospect.get("role"))
    industry = safe_text(prospect.get("industry"))
    pain_point = safe_text(prospect.get("pain_point"))
    custom_note = safe_text(prospect.get("custom_note"))

    prompt = f"""
You are an expert B2B cold-email copywriter.

Create TWO genuinely personalized cold email variants
for the prospect below.

==================================================
PRODUCT / SERVICE
==================================================

{product_description}

==================================================
TARGET AUDIENCE
==================================================

{target_audience}

==================================================
PROSPECT DETAILS
==================================================

Name: {name}
Company: {company}
Role: {role}
Industry: {industry}
Pain Point: {pain_point}
Custom Note: {custom_note}

==================================================
TONE
==================================================

{tone}

==================================================
PERSONALIZATION RULES
==================================================

1. Use ONLY the prospect information provided above.

2. Never invent company news, achievements, revenue,
   customers, technologies, statistics, events,
   partnerships, or personal facts.

3. Use the prospect's exact name.

4. Mention at least one specific prospect detail
   within the first two sentences.

5. Make the email sound natural and human.

6. Keep the email concise.

7. Avoid aggressive sales language.

8. Do not use fake urgency.

9. Do not use the word "deal".
   Use neutral phrases such as:
   opportunity, conversation, option, or collaboration.

10. Avoid spam-trigger phrases such as:
    free, guarantee, act now, limited time, urgent,
    buy now, winner, risk free, 100%, click here,
    special offer, cheap, make money, cash, sale,
    discount.

==================================================
VARIANT A
==================================================

Pain-point focused.

Connect the supplied prospect pain point or context
with the product/service.

==================================================
VARIANT B
==================================================

Curiosity/value focused.

Create interest around a useful business outcome.

==================================================
SUBJECT LINES
==================================================

For each variant provide:

- One main subject
- Two alternative subject lines
- A score from 1-10 for open-rate potential

Score based on:
- relevance
- clarity
- brevity
- curiosity
- personalization

==================================================
OUTPUT
==================================================

Return ONLY valid JSON.

Use exactly this structure:

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

    response = model.generate_content(prompt)

    text = clean_json_response(response.text)

    try:

        return json.loads(text)

    except json.JSONDecodeError:

        match = re.search(
            r"\{.*\}",
            text,
            re.DOTALL
        )

        if not match:

            raise ValueError(
                "Gemini returned an invalid JSON response."
            )

        return json.loads(match.group())


# ============================================================
# API KEY CHECK
# ============================================================

if not GOOGLE_API_KEY:

    st.error("❌ Gemini API key not found.")

    st.code(
        "GOOGLE_API_KEY=YOUR_GEMINI_API_KEY",
        language="text"
    )

    st.info(
        "Add your API key to the .env file and restart the app."
    )

    st.stop()


# ============================================================
# HEADER
# ============================================================

st.title("📧 AI Cold Email & Outreach Generator")

st.write(
    "Generate personalized cold emails with A/B variants, "
    "spam checking, editing, approval, and export."
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

    st.subheader("✨ Features")

    st.write("✅ Product & audience input")
    st.write("✅ CSV upload")
    st.write("✅ Manual prospect entry")
    st.write("✅ AI personalization")
    st.write("✅ A/B variants")
    st.write("✅ Spam checker")
    st.write("✅ Spam suggestions")
    st.write("✅ Subject alternatives")
    st.write("✅ Subject scoring")
    st.write("✅ Email editing")
    st.write("✅ Approval workflow")
    st.write("✅ CSV export")


# ============================================================
# 1. PRODUCT & TARGET AUDIENCE
# ============================================================

st.header("1️⃣ Product & Target Audience")

col1, col2 = st.columns(2)

with col1:

    product_description = st.text_area(
        "Product / Service Description *",
        placeholder=(
            "Example:\n"
            "We provide an AI-powered sales assistant that "
            "researches prospects and creates personalized "
            "outbound emails."
        ),
        height=180
    )

with col2:

    target_audience = st.text_area(
        "Target Audience *",
        placeholder=(
            "Example:\n"
            "B2B sales teams, startup founders, sales managers, "
            "and business development teams."
        ),
        height=180
    )


# ============================================================
# 2. PROSPECT LIST
# ============================================================

st.header("2️⃣ Prospect List")

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

    st.subheader("📁 Upload Prospect CSV")

    uploaded_file = st.file_uploader(
        "Upload your prospect list",
        type=["csv"],
        help=(
            "Required: name, company, role, industry. "
            "Optional: pain_point, custom_note."
        )
    )

    if uploaded_file is not None:

        try:

            df = pd.read_csv(uploaded_file)

            # Normalize column names
            df.columns = [
                str(column)
                .strip()
                .lower()
                .replace(" ", "_")
                for column in df.columns
            ]

            required_columns = [
                "name",
                "company",
                "role",
                "industry"
            ]

            missing_columns = [
                column
                for column in required_columns
                if column not in df.columns
            ]

            if missing_columns:

                st.error(
                    "❌ Missing required columns: "
                    + ", ".join(missing_columns)
                )

                st.info(
                    "Required columns: "
                    "name, company, role, industry"
                )

                df = pd.DataFrame()

            else:

                if "pain_point" not in df.columns:
                    df["pain_point"] = ""

                if "custom_note" not in df.columns:
                    df["custom_note"] = ""

                # Remove completely empty rows
                df = df.dropna(
                    how="all"
                ).reset_index(drop=True)

                st.success(
                    f"✅ {len(df)} prospects loaded successfully!"
                )

                with st.expander(
                    "👥 View Prospect List"
                ):

                    st.dataframe(
                        df,
                        use_container_width=True,
                        height=300
                    )

        except Exception as e:

            st.error(
                f"❌ Could not read CSV: {str(e)}"
            )

            df = pd.DataFrame()

    else:

        st.info(
            "Upload a CSV file containing your prospects."
        )

        with st.expander(
            "📄 View CSV Format"
        ):

            example_df = pd.DataFrame([
                {
                    "name": "Priya Sharma",
                    "company": "FinEdge",
                    "role": "Head of Sales",
                    "industry": "Fintech",
                    "pain_point": "Low lead conversion",
                    "custom_note": "Expanding the sales team"
                }
            ])

            st.dataframe(
                example_df,
                use_container_width=True
            )

        df = pd.DataFrame()


# ============================================================
# MANUAL ENTRY
# ============================================================

else:

    st.subheader("✍️ Manual Prospect Entry")

    st.info(
        "Enter prospect details and click "
        "**Add Prospect**. You can add multiple prospects."
    )

    with st.form(
        "manual_prospect_form",
        clear_on_submit=True
    ):

        col1, col2 = st.columns(2)

        with col1:

            manual_name = st.text_input(
                "Name *",
                placeholder="Priya Sharma"
            )

            manual_company = st.text_input(
                "Company *",
                placeholder="FinEdge"
            )

            manual_role = st.text_input(
                "Role *",
                placeholder="Head of Sales"
            )

        with col2:

            manual_industry = st.text_input(
                "Industry *",
                placeholder="Fintech"
            )

            manual_pain_point = st.text_input(
                "Pain Point",
                placeholder="Low lead conversion"
            )

            manual_custom_note = st.text_area(
                "Custom Note",
                placeholder=(
                    "Example: Expanding the sales team "
                    "and focusing on outbound growth."
                ),
                height=100
            )

        add_prospect = st.form_submit_button(
            "➕ Add Prospect",
            use_container_width=True
        )

        if add_prospect:

            if not manual_name.strip():

                st.error(
                    "Please enter the prospect name."
                )

            elif not manual_company.strip():

                st.error(
                    "Please enter the company."
                )

            elif not manual_role.strip():

                st.error(
                    "Please enter the role."
                )

            elif not manual_industry.strip():

                st.error(
                    "Please enter the industry."
                )

            else:

                new_prospect = {
                    "name": manual_name.strip(),
                    "company": manual_company.strip(),
                    "role": manual_role.strip(),
                    "industry": manual_industry.strip(),
                    "pain_point": manual_pain_point.strip(),
                    "custom_note": manual_custom_note.strip()
                }

                st.session_state.manual_prospects.append(
                    new_prospect
                )

                st.success(
                    f"✅ {manual_name} added successfully!"
                )


    # ========================================================
    # DISPLAY MANUAL PROSPECTS
    # ========================================================

    if st.session_state.manual_prospects:

        st.divider()

        st.subheader(
            f"👥 Added Prospects "
            f"({len(st.session_state.manual_prospects)})"
        )

        manual_df = pd.DataFrame(
            st.session_state.manual_prospects
        )

        st.dataframe(
            manual_df,
            use_container_width=True,
            height=250
        )

        # Remove prospect
        prospect_options = [
            f"{i + 1}. {p['name']} — {p['company']}"
            for i, p in enumerate(
                st.session_state.manual_prospects
            )
        ]

        selected_remove = st.selectbox(
            "Select a prospect to remove",
            ["Select..."] + prospect_options
        )

        if selected_remove != "Select...":

            remove_index = prospect_options.index(
                selected_remove
            )

            if st.button(
                "🗑️ Remove Selected Prospect"
            ):

                removed = (
                    st.session_state.manual_prospects.pop(
                        remove_index
                    )
                )

                st.success(
                    f"Removed {removed['name']}."
                )

                st.rerun()

        if st.button(
            "🧹 Clear All Manual Prospects"
        ):

            st.session_state.manual_prospects = []

            st.rerun()

        df = pd.DataFrame(
            st.session_state.manual_prospects
        )

    else:

        st.info(
            "No manual prospects added yet."
        )

        df = pd.DataFrame()


# ============================================================
# CHECK PROSPECT LIST
# ============================================================

if df.empty:

    st.warning(
        "⚠️ Add at least one prospect using CSV upload "
        "or Manual Entry."
    )

    st.stop()


# ============================================================
# 3. SELECT NUMBER OF PROSPECTS
# ============================================================

st.header("3️⃣ Select Prospects to Process")

total_available = len(df)

st.write(
    f"📊 **Total prospects available: {total_available}**"
)

# ------------------------------------------------------------
# CREATE OPTIONS BASED ON TOTAL CSV / MANUAL PROSPECTS
# ------------------------------------------------------------

batch_options = []

# Standard batch sizes
standard_sizes = [
    5,
    10,
    15,
    20,
    25,
    30,
    35,
    40,
    45,
    50
]

for size in standard_sizes:

    if size < total_available:
        batch_options.append(size)

# Always include the exact number available
batch_options.append(total_available)

# Remove duplicates and sort
batch_options = sorted(
    set(batch_options)
)

# ------------------------------------------------------------
# DEFAULT TO 5 IF AVAILABLE
# ------------------------------------------------------------

if 5 in batch_options:

    default_index = batch_options.index(5)

else:

    default_index = 0


prospects_to_process = st.selectbox(
    "How many prospects do you want to process?",
    batch_options,
    index=default_index,
    help=(
        "Choose how many prospects from your uploaded "
        "or manually entered list should be processed."
    )
)

# ------------------------------------------------------------
# SELECT FIRST N PROSPECTS
# ------------------------------------------------------------

process_df = df.head(
    int(prospects_to_process)
).copy()

st.success(
    f"✅ **{len(process_df)}** prospect(s) selected "
    f"out of **{total_available}** available."
)

# ------------------------------------------------------------
# PREVIEW SELECTED PROSPECTS
# ------------------------------------------------------------

with st.expander(
    "👥 View Selected Prospects"
):

    st.dataframe(
        process_df,
        use_container_width=True,
        height=250
    )


# ============================================================
# 4. AI EMAIL GENERATION
# ============================================================

st.header("4️⃣ AI Email Generation")

st.caption(
    "Two different personalized email variants will be "
    "generated for every selected prospect."
)

generate_button = st.button(
    "🚀 Generate Personalized Emails",
    type="primary",
    use_container_width=True
)


if generate_button:

    if not product_description.strip():

        st.error(
            "❌ Please enter your product/service description."
        )

        st.stop()

    if not target_audience.strip():

        st.error(
            "❌ Please enter your target audience."
        )

        st.stop()

    # Clear old results
    st.session_state.generated_results = []

    progress_bar = st.progress(0)

    status_text = st.empty()

    total = len(process_df)

    for index, (_, prospect) in enumerate(
        process_df.iterrows()
    ):

        prospect_data = prospect.to_dict()

        prospect_name = safe_text(
            prospect_data.get("name")
        )

        status_text.info(
            f"Generating email for **{prospect_name}** "
            f"({index + 1}/{total})..."
        )

        try:

            ai_result = generate_emails(
                product_description,
                target_audience,
                prospect_data,
                tone
            )

            variant_a = ai_result.get(
                "variant_a",
                {}
            )

            variant_b = ai_result.get(
                "variant_b",
                {}
            )

            subject_a = safe_text(
                variant_a.get("subject")
            )

            body_a = safe_text(
                variant_a.get("body")
            )

            subject_b = safe_text(
                variant_b.get("subject")
            )

            body_b = safe_text(
                variant_b.get("body")
            )

            spam_a = check_spam(
                subject_a + " " + body_a
            )

            spam_b = check_spam(
                subject_b + " " + body_b
            )

            result = {

                "name": prospect_name,

                "company": safe_text(
                    prospect_data.get("company")
                ),

                "role": safe_text(
                    prospect_data.get("role")
                ),

                "industry": safe_text(
                    prospect_data.get("industry")
                ),

                "pain_point": safe_text(
                    prospect_data.get("pain_point")
                ),

                "custom_note": safe_text(
                    prospect_data.get("custom_note")
                ),

                "variant_a": {

                    "subject": subject_a,

                    "subject_options":
                        variant_a.get(
                            "subject_options",
                            []
                        ),

                    "subject_score":
                        variant_a.get(
                            "subject_score",
                            0
                        ),

                    "body": body_a,

                    "spam_words": spam_a
                },

                "variant_b": {

                    "subject": subject_b,

                    "subject_options":
                        variant_b.get(
                            "subject_options",
                            []
                        ),

                    "subject_score":
                        variant_b.get(
                            "subject_score",
                            0
                        ),

                    "body": body_b,

                    "spam_words": spam_b
                },

                "approved": False,

                "approved_variant": "A"
            }

            st.session_state.generated_results.append(
                result
            )

        except Exception as e:

            st.error(
                f"❌ Failed for {prospect_name}: {str(e)}"
            )

        progress_bar.progress(
            (index + 1) / total
        )

        # Prevent sending requests too quickly
        if index < total - 1:

            time.sleep(4)

    status_text.success(
        f"✅ Finished processing {total} prospect(s)."
    )

    time.sleep(1)

    st.rerun()


# ============================================================
# 5. REVIEW, EDIT & APPROVE
# ============================================================

if st.session_state.generated_results:

    st.divider()

    st.header("5️⃣ Review, Edit & Approve")

    st.info(
        "Review both A/B variants, edit them if necessary, "
        "select your preferred variant, and approve."
    )

    for i, result in enumerate(
        st.session_state.generated_results
    ):

        st.markdown(
            f"## 👤 {result['name']} — {result['company']}"
        )

        st.write(
            f"**Role:** {result['role']}  | "
            f"**Industry:** {result['industry']}"
        )

        if result["pain_point"]:

            st.write(
                f"**Pain Point:** {result['pain_point']}"
            )

        if result["custom_note"]:

            st.write(
                f"**Custom Note:** {result['custom_note']}"
            )

        col_a, col_b = st.columns(2)

        # ====================================================
        # VARIANT A
        # ====================================================

        with col_a:

            st.subheader(
                "🅰️ Variant A — Pain Point"
            )

            subject_a = st.text_input(
                "Subject A",
                value=result["variant_a"]["subject"],
                key=f"subject_a_{i}"
            )

            body_a = st.text_area(
                "Email A",
                value=result["variant_a"]["body"],
                height=280,
                key=f"body_a_{i}"
            )

            result["variant_a"]["subject"] = subject_a
            result["variant_a"]["body"] = body_a

            subject_options_a = result[
                "variant_a"
            ].get(
                "subject_options",
                []
            )

            if subject_options_a:

                st.caption(
                    "Alternative Subject Lines"
                )

                for option in subject_options_a:

                    st.write(
                        f"• {option}"
                    )

            score_a = result[
                "variant_a"
            ].get(
                "subject_score",
                0
            )

            st.metric(
                "Subject Potential Score",
                f"{score_a}/10"
            )

            # Spam check
            spam_a = check_spam(
                subject_a + " " + body_a
            )

            result["variant_a"]["spam_words"] = spam_a

            if spam_a:

                st.warning(
                    "⚠️ Spam-risk language detected: "
                    + ", ".join(spam_a)
                )

                for suggestion in get_spam_suggestions(
                    spam_a
                ):

                    st.markdown(
                        "• " + suggestion
                    )

            else:

                st.success(
                    "✅ No configured spam-trigger "
                    "words detected."
                )

            st.caption(
                "📋 Copy-ready email"
            )

            st.code(
                f"Subject: {subject_a}\n\n{body_a}",
                language=None
            )

        # ====================================================
        # VARIANT B
        # ====================================================

        with col_b:

            st.subheader(
                "🅱️ Variant B — Curiosity / Value"
            )

            subject_b = st.text_input(
                "Subject B",
                value=result["variant_b"]["subject"],
                key=f"subject_b_{i}"
            )

            body_b = st.text_area(
                "Email B",
                value=result["variant_b"]["body"],
                height=280,
                key=f"body_b_{i}"
            )

            result["variant_b"]["subject"] = subject_b
            result["variant_b"]["body"] = body_b

            subject_options_b = result[
                "variant_b"
            ].get(
                "subject_options",
                []
            )

            if subject_options_b:

                st.caption(
                    "Alternative Subject Lines"
                )

                for option in subject_options_b:

                    st.write(
                        f"• {option}"
                    )

            score_b = result[
                "variant_b"
            ].get(
                "subject_score",
                0
            )

            st.metric(
                "Subject Potential Score",
                f"{score_b}/10"
            )

            # Spam check
            spam_b = check_spam(
                subject_b + " " + body_b
            )

            result["variant_b"]["spam_words"] = spam_b

            if spam_b:

                st.warning(
                    "⚠️ Spam-risk language detected: "
                    + ", ".join(spam_b)
                )

                for suggestion in get_spam_suggestions(
                    spam_b
                ):

                    st.markdown(
                        "• " + suggestion
                    )

            else:

                st.success(
                    "✅ No configured spam-trigger "
                    "words detected."
                )

            st.caption(
                "📋 Copy-ready email"
            )

            st.code(
                f"Subject: {subject_b}\n\n{body_b}",
                language=None
            )

        # ====================================================
        # APPROVAL
        # ====================================================

        st.markdown(
            "### ✅ Select & Approve"
        )

        selected_variant = st.radio(
            "Choose the variant to export",
            ["A", "B"],
            index=(
                0
                if result["approved_variant"] == "A"
                else 1
            ),
            horizontal=True,
            key=f"variant_choice_{i}"
        )

        result["approved_variant"] = selected_variant

        approved = st.checkbox(
            "Approve this email",
            value=result["approved"],
            key=f"approved_{i}"
        )

        result["approved"] = approved

        if approved:

            st.success(
                f"✅ Variant {selected_variant} "
                "approved and ready for export."
            )

        else:

            st.info(
                "This prospect has not been approved yet."
            )

        st.divider()


# ============================================================
# 6. EXPORT
# ============================================================

if st.session_state.generated_results:

    st.header("6️⃣ Export Approved Emails")

    approved_rows = []

    for result in st.session_state.generated_results:

        if result["approved"]:

            if result["approved_variant"] == "A":

                selected_variant = result["variant_a"]

            else:

                selected_variant = result["variant_b"]

            approved_rows.append(
                {
                    "name": result["name"],
                    "company": result["company"],
                    "role": result["role"],
                    "industry": result["industry"],
                    "selected_variant":
                        result["approved_variant"],
                    "subject":
                        selected_variant["subject"],
                    "email_body":
                        selected_variant["body"],
                    "spam_flags":
                        ", ".join(
                            selected_variant["spam_words"]
                        )
                }
            )

    if approved_rows:

        approved_df = pd.DataFrame(
            approved_rows
        )

        st.success(
            f"✅ {len(approved_rows)} approved "
            "email(s) ready for export."
        )

        st.dataframe(
            approved_df,
            use_container_width=True
        )

        # CSV
        csv_data = approved_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "⬇️ Download Approved Emails CSV",
            data=csv_data,
            file_name="approved_cold_emails.csv",
            mime="text/csv",
            use_container_width=True
        )

        # Copy-ready output
        st.subheader(
            "📋 Copy Approved Emails"
        )

        all_copy_text = ""

        for row in approved_rows:

            all_copy_text += (
                f"Name: {row['name']}\n"
                f"Company: {row['company']}\n"
                f"Variant: {row['selected_variant']}\n"
                f"Subject: {row['subject']}\n\n"
                f"{row['email_body']}\n\n"
                f"{'-' * 60}\n\n"
            )

        st.code(
            all_copy_text,
            language=None
        )

        st.caption(
            "Use the copy button on the code block "
            "to copy the approved emails."
        )

    else:

        st.info(
            "Approve at least one email to enable export."
        )


# ============================================================
# 7. CAMPAIGN SUMMARY
# ============================================================

if st.session_state.generated_results:

    st.divider()

    st.header("📊 Campaign Summary")

    total_generated = len(
        st.session_state.generated_results
    )

    total_approved = sum(
        1
        for result in st.session_state.generated_results
        if result["approved"]
    )

    total_spam_flags = sum(
        len(result["variant_a"]["spam_words"])
        +
        len(result["variant_b"]["spam_words"])
        for result in st.session_state.generated_results
    )

    approval_rate = (
        (total_approved / total_generated) * 100
        if total_generated
        else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Prospects Processed",
            total_generated
        )

    with col2:

        st.metric(
            "Approved Emails",
            total_approved
        )

    with col3:

        st.metric(
            "Spam Flags",
            total_spam_flags
        )

    with col4:

        st.metric(
            "Approval Rate",
            f"{approval_rate:.0f}%"
        )

    st.caption(
        "These are workflow metrics, not actual email "
        "open or reply results."
    )


# ============================================================
# ABOUT
# ============================================================

st.divider()

with st.expander(
    "ℹ️ About this application"
):

    st.write(
        """
        AI Cold Email & Outreach Generator

        This application allows users to:

        • Describe a product or service
        • Define the target audience
        • Upload prospect lists using CSV
        • Add prospects manually
        • Generate personalized cold emails
        • Create two A/B variants
        • Check for spam-trigger language
        • Edit generated emails
        • Approve a selected variant
        • Export approved emails as CSV
        • Copy approved emails for external use

        The application does not automatically send emails.
        """
    )

st.caption(
    "📧 AI Cold Email & Outreach Generator"
)
