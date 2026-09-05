# ✉️ AI Cold Email & Outreach Generator

An AI-powered web application that helps salespeople and founders create personalized cold emails for outbound outreach.

The application takes a product/service description, target audience, and prospect information, then generates two personalized email variants. It also checks generated emails for common spam-trigger words and allows users to review, edit, approve, and export the results.

---

## 🚀 Features

* 📝 Product/service description input
* 🎯 Target audience input
* 📂 Prospect CSV upload
* 👤 Prospect details:

  * Name
  * Company
  * Role
  * Industry
  * Pain point
  * Custom note
* 🤖 AI-powered personalized email generation
* 🔀 Two A/B email variants for each prospect
* 🎯 Pain-point-focused Variant A
* 💡 Curiosity/value-focused Variant B
* 🚨 Spam-trigger-word checker
* 💬 Spam-risk suggestions
* ✏️ Email preview and editing
* ✅ Email approval workflow
* 📋 Copy email content
* 📥 Download generated emails as CSV
* 📥 Download approved emails as CSV
* 📊 Generation summary

These features cover the workshop's core requirements.

---

## 🛠️ Technology Stack

* **Python**
* **Streamlit**
* **Google Gemini API**
* **Pandas**
* **python-dotenv**

The workshop lists React or HTML/CSS/JS for the frontend, FastAPI/Node.js for backend options, SQLite/Firestore for storage, and AI APIs for generation. This implementation uses Streamlit and Python for a lightweight prototype.

---

## 📁 Project Structure

```text
ai-cold-email-generator/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env
└── sample_prospects.csv
```

---

## 💻 Requirements

Before running the project, install:

* Python 3.11+
* pip
* A Google Gemini API key
* Internet connection

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Enter the project directory

```bash
cd ai-cold-email-generator
```

### 3. Create a virtual environment

Windows:

```powershell
py -3.11 -m venv .venv
```

### 4. Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```powershell
pip install -r requirements.txt
```

---

## 🔑 API Key Configuration

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
```

Replace `YOUR_GEMINI_API_KEY` with your actual Gemini API key.

### Security

Do **not** upload `.env` to GitHub.

Add the following to `.gitignore`:

```text
.env
.venv/
__pycache__/
*.pyc
```

---

# 📄 Prospect CSV Format

The application accepts a CSV file containing prospect information.

### Required columns

```text
name
company
role
industry
```

### Recommended columns

```text
pain_point
custom_note
```

### Example

```csv
name,company,role,industry,pain_point,custom_note
Priya Sharma,FinEdge,Head of Sales,Fintech,Low lead conversion,Expanding the sales team
Rahul Kumar,TechNova,CEO,SaaS,Manual outreach,Recently launched a new product
Ananya Rao,HealthPlus,Marketing Manager,Healthcare,Poor engagement,Improving customer engagement
```

The workshop recommends using fictional but realistic prospect data, with approximately 10–15 entries for a demonstration.

---

# ▶️ Running the Application

After activating the virtual environment, run:

```powershell
streamlit run app.py
```

The application will open in your browser.

Usually:

```text
http://localhost:8501
```

---

# 🔄 Application Workflow

```text
Product / Service
       ↓
Target Audience
       ↓
Upload Prospect CSV
       ↓
AI Email Generation
       ↓
A/B Email Variants
       ↓
Spam Trigger Check
       ↓
Review & Edit
       ↓
Approve
       ↓
Export CSV
```

---

# 1️⃣ Product / Service Input

The user enters a description of the product or service.

Example:

```text
An AI sales assistant that helps B2B sales teams research prospects
and create personalized outbound messages.
```

---

# 2️⃣ Target Audience

The user describes the intended audience.

Example:

```text
B2B SaaS companies with sales teams that want to improve
outbound productivity and response rates.
```

---

# 3️⃣ Prospect Upload

The user uploads a CSV containing prospect details.

The application reads the CSV using Pandas and displays the prospects before email generation.

---

# 4️⃣ AI Email Generation

The application sends the product information, target audience, prospect details, and selected tone to the Gemini API.

The AI generates two different email approaches for every prospect.

The workshop requires the AI to create personalized drafts using prospect-specific details.

---

# 🔀 A/B Email Variants

## Variant A — Pain Point Focused

This email focuses on a problem or challenge associated with the prospect.

## Variant B — Curiosity / Value Focused

This email uses a different angle focused on curiosity and potential value.

Both variants are generated for each prospect as required by the workshop.

---

# 🚨 Spam Trigger Checker

The application checks generated emails for potentially risky words and phrases.

Example trigger words:

```text
free
guarantee
act now
buy now
limited time
winner
urgent
discount
click here
```

If a trigger word is found, the application displays:

```text
⚠️ Spam risk detected
```

It also provides a suggested alternative.

The workshop recommends a simple keyword-based spam checker for the MVP rather than requiring a complex machine-learning deliverability system.

---

# ✏️ Review and Edit

Users can review both email variants.

They can:

* Edit the subject
* Edit the email body
* Review spam warnings
* Approve the emails

The workshop requires users to be able to view, modify, and approve generated emails before export.

---

# ✅ Approval

Each prospect has an approval checkbox.

Only emails marked as approved are included in the approved-email export.

---

# 📥 Export

The application provides two download options:

### Download All Emails

Downloads all generated emails as a CSV file.

### Download Approved Emails

Downloads only approved emails.

The workshop requires export/copy functionality and specifically states that actual email sending is not necessary.

---

# 📊 Exported CSV

The generated CSV contains:

```text
Name
Company
Role
Industry
Variant A Subject
Variant A Email
Variant B Subject
Variant B Email
Variant A Spam Flags
Variant B Spam Flags
Approved
```

---

# 🧠 Structured AI Output

The AI is instructed to return structured JSON:

```json
{
  "variant_a": {
    "subject": "Subject line",
    "body": "Email body"
  },
  "variant_b": {
    "subject": "Subject line",
    "body": "Email body"
  }
}
```

Structured JSON makes the AI response easier for the application to parse reliably. The workshop specifically recommends structured output for this reason.

---

# 🎨 Tone Selection

The application supports multiple email tones:

* Professional
* Formal
* Casual
* Friendly
* Witty

The selected tone is passed to the AI generation prompt.

Tone/style selection is also listed as a useful stretch feature in the workshop.

---

# 🧪 Demo Example

A recommended demo:

### Product

```text
AI Sales Assistant for B2B sales teams.
```

### Target Audience

```text
B2B SaaS companies with outbound sales teams.
```

### Prospect

```text
Name: Priya Sharma
Company: FinEdge
Role: Head of Sales
Industry: Fintech
Pain Point: Low lead conversion
```

The application generates:

```text
Variant A
Pain-point focused
        +
Variant B
Curiosity/value focused
```

The emails should reference the prospect's actual information rather than using generic text.

The workshop recommends highlighting specific prospect details in the first two sentences.

---

# 🔍 Demo Spam Check

To demonstrate the spam checker, an email can contain a phrase such as:

```text
Act now to learn more.
```

The application should identify:

```text
⚠️ Spam risk detected: act now
```

The user can then edit the phrase to something more natural, such as:

```text
If this is relevant, I'd be happy to share more details.
```

---

# 📈 Demo Flow

```text
1. Enter product/service
          ↓
2. Enter target audience
          ↓
3. Select tone
          ↓
4. Upload CSV
          ↓
5. Generate emails
          ↓
6. Show Variant A
          ↓
7. Show Variant B
          ↓
8. Demonstrate spam checker
          ↓
9. Edit email
          ↓
10. Approve email
          ↓
11. Download CSV
```

This follows the workshop's recommended demonstration flow.

---

# ⚠️ Limitations

The spam checker is a basic keyword-based heuristic.

It does **not** guarantee email deliverability or inbox placement.

A flagged word does not automatically mean an email will go to spam.

Similarly, an email without flagged words is not guaranteed to reach the inbox.

AI-generated emails should be reviewed by a human before use.

---

# 🔒 Security

API keys should never be hard-coded into `app.py`.

Use:

```env
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
```

Store secrets securely when deploying the application.

---

# 🚀 Future Improvements

Possible future features include:

* Advanced personalization
* More email tones
* Multiple subject-line suggestions
* Subject-line scoring
* Mock open/reply analytics
* A/B testing dashboard
* Database storage
* Gmail integration
* SendGrid integration
* Advanced deliverability analysis

These correspond to the workshop's suggested stretch features.

---

# 🎯 Project Objective

The objective of this project is to reduce the time required to create personalized outbound sales emails.

The application combines:

**AI Personalization + A/B Testing + Spam Checking + Human Review + Export**

This provides a practical workflow for creating outbound email campaigns without requiring the application to actually send emails.

---

# 📌 Key Value Proposition

### Before

```text
Research prospect
       ↓
Write email manually
       ↓
Create another version
       ↓
Check email manually
       ↓
Repeat for every prospect
```

### With this application

```text
Upload prospects
       ↓
AI personalization
       ↓
Two email variants
       ↓
Spam check
       ↓
Review
       ↓
Export
```

---

## 📜 License

This project is created for educational, workshop, prototype, and hackathon purposes.
