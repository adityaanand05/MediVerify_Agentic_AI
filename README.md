
# MediVerify: Agentic Provider Data Verification
**Automated Provider Data Compliance Engine**

MediVerify is a specialized **Agentic AI solution**, engineered for Insurance and Payer Companies, to dramatically reduce the manual effort and time for provider data verification.

This system leverages a multi-agent framework powered by Google's Gemini 2.5 Flash to automatically query, cross-reference, and reconcile critical information about medical practitioners from multiple authoritative sources. The goal is to ensure the accuracy and compliance of doctor and medical personnel data before onboarding or **during** ongoing validation, replacing tedious manual checks with rapid, verifiable AI workflows.

---

## 💡 Key Features & Use Case

The primary function of MediVerify is to serve as a fast, reliable verification engine for credentialing and data compliance teams.

* **Target Users:** Insurance carriers, healthcare payers, and credentialing organizations.
* **Agentic Verification (CrewAI):** Uses a collaborative AI crew to define verification tasks, gather data, and generate a definitive compliance report.
* **Multi-Source Integration:** Fetches and compares data simultaneously from critical open data sources:
    * NPI Registry (National Provider Identifier)
    * NABP (National Association of Boards of Pharmacy)
    * Propelus Open Data APIs (**Optional/If Applicable**)
* **LLM Core:** Powered by Gemini 2.5 Flash API for high-speed, accurate data synthesis and decision-making based on retrieved documents.
* **Document Handling:** Includes PDF extraction capabilities to process source documents like licenses or certifications.
* **Web Interface:** A simple yet effective frontend built with HTML, CSS, and vanilla JavaScript served by a Flask backend.

---

## ⚙️ Technology Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **LLM Engine** | Gemini 2.5 Flash | Core decision-making and synthesis model (via API). |
| **Agent Framework** | CrewAI | Orchestrates the multi-agent workflow (e.g., Retrieval Agent, Comparison Agent). |
| **Backend/Web** | Flask | Serves the web application and handles API routing for the AI crew. |
| **Data Processing** | pandas, numpy, csv | Handles structured data manipulation, analysis, and ingestion. |
| **Document Processing** | pdfextractor (e.g., PyPDF) | Extracts text and data from PDF documents for agent analysis. |
| **Frontend** | HTML, CSS, JavaScript | User interface for inputting provider details and viewing verification reports. |

---

## 🧠 Agent Architecture Overview (CrewAI)

MediVerify uses a specialized crew of four expert agents to execute the provider verification pipeline. This systematic delegation ensures high-quality, audit-ready verification outputs.

| Agent Role | Goal | Key Responsibilities |
| :--- | :--- | :--- |
| 1. Healthcare Provider Data Validator | Perform comprehensive primary data verification and flag discrepancies. | Cross-references NPI, NABP, and Propelus data using API tools. |
| 2. Provider Data Enrichment Specialist | Analyze validated data to identify gaps, inconsistencies, or missing information. | Enhances data quality and requests additional information to build a complete profile. |
| 3. Quality Assurance & Compliance Reviewer | Conduct thorough quality review against credentialing standards. | Ensures data is accurate, complete, and compliant with regulations (e.g., CMS, NCQA). |
| 4. Healthcare Validation Report Generator | Synthesize all findings into professional, actionable reports. | Transforms complex validation data into clear reports for stakeholders and decision-makers. |

---

## 🚀 Getting Started

Follow these steps to set up and run the MediVerify application locally.

### Prerequisites

* Python 3.10+
* A valid Gemini API Key.

### 1. Installation

Clone the Repository:

```bash
git clone [https://github.com/adityaanand05/MediVerify_Agentic_AI.git](https://github.com/adityaanand05/MediVerify_Agentic_AI.git)
cd MediVerify_Agentic_AI
````

Set Up the Virtual Environment (`.venv`):
It is mandatory to use a virtual environment to manage dependencies.

```bash
python -m venv .venv
source .venv/bin/activate  # On Linux/macOS
# .\.venv\Scripts\activate   # On Windows
```

Install Dependencies:

```bash
pip install -r requirements.txt
```

### 2\. Environment Configuration (`.env`)

You must create a file named `.env` in the root directory to store your API key. The application will use this for the Gemini API calls.

1.  Create a new file named `.env`.
2.  Add your Gemini API Key:

<!-- end list -->

```dotenv
# Set your Google Gemini API Key
GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
```

*Note: If your CrewAI setup requires the key as `OPENAI_API_KEY` for compatibility, use that variable name instead, but map it to your Gemini key.*

### 3\. Running the Application

1.  Ensure you are in the virtual environment (`source .venv/bin/activate`).
2.  Run the Flask application:

<!-- end list -->

```bash
flask run
```

3.  Open your web browser and navigate to the address shown in the terminal (usually `http://127.0.0.1:5000/`).

-----

## 🤝 Contributing

We welcome contributions\! Please feel free to open issues or submit pull requests with improvements, bug fixes, or new features (like integrating additional data sources).

-----

## 📄 License

This project is open-sourced under the **Mozilla Public License Version 2.0**. See the `LICENSE` file for more details.
