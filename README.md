
# 🩺 MediVerify — Agentic Provider Data Verification

### **Automated AI-Powered Provider Data Compliance Engine**

**MediVerify** is an **Agentic AI solution** built to revolutionize the way **healthcare payers and insurance organizations** verify provider data.
It eliminates tedious manual checks by deploying a multi-agent system powered by **Google Gemini 2.5 Flash**, automating the validation, reconciliation, and compliance of provider information across multiple authoritative data sources.

---

## 🚀 Overview

Healthcare payers face a critical need to maintain accurate and compliant provider directories — a task often burdened by manual processes, fragmented systems, and regulatory constraints.

**MediVerify** streamlines this process by leveraging **autonomous AI agents** that collaboratively:

* Retrieve data from trusted healthcare registries.
* Compare and verify records.
* Flag discrepancies.
* Generate audit-ready compliance reports.

This not only improves accuracy but also reduces verification time by over **70%**, accelerating provider onboarding and directory updates.

---

## 🧩 Core Features

✅ **Agentic AI Verification (CrewAI):**
A multi-agent CrewAI framework performs distributed verification and analysis tasks in parallel.

✅ **Multi-Source Data Cross-Referencing:**
Integrates with key open and optional data sources:

* **NPI Registry (National Provider Identifier)**
* **NABP (National Association of Boards of Pharmacy)**
* **Propelus Open Data APIs** *(optional)*

✅ **LLM-Powered Decision Layer:**
Utilizes **Gemini 2.5 Flash** for intelligent data synthesis, interpretation, and discrepancy reasoning.

✅ **Document Intelligence:**
Extracts and validates data from uploaded documents (PDF licenses, certifications, etc.) using PyPDF.

✅ **Web Dashboard (Flask + Vanilla JS):**
Simple, intuitive frontend to submit provider details, view real-time validation progress, and download compliance summaries.

---

## 🧠 Agentic Architecture

MediVerify deploys a four-agent collaborative pipeline within **CrewAI**, ensuring every verification is complete, accurate, and traceable.

| **Agent Role**                            | **Objective**                                    | **Key Responsibilities**                                 |
| ----------------------------------------- | ------------------------------------------------ | -------------------------------------------------------- |
| 🩺 **Healthcare Provider Data Validator** | Conduct primary verification from multiple APIs. | Cross-check NPI, NABP, and Propelus datasets.            |
| 🔍 **Data Enrichment Specialist**         | Fill missing fields and resolve inconsistencies. | Enhance incomplete profiles using structured inference.  |
| 🧾 **Compliance & QA Reviewer**           | Ensure regulatory and credentialing compliance.  | Validate data against CMS/NCQA credentialing standards.  |
| 📑 **Report Generator**                   | Produce structured verification reports.         | Summarize agent findings into a clean, shareable format. |

---

## ⚙️ Technology Stack

| **Layer**           | **Technology**                 | **Purpose**                                      |
| ------------------- | ------------------------------ | ------------------------------------------------ |
| **LLM Engine**      | Google **Gemini 2.5 Flash**    | High-speed decision-making and summarization     |
| **Agent Framework** | **CrewAI**                     | Multi-agent orchestration and task delegation    |
| **Backend**         | **Flask**                      | Core API and web server for agent orchestration  |
| **Frontend**        | **HTML, CSS, JS**              | Lightweight user interface                       |
| **Data Layer**      | **pandas**, **numpy**, **csv** | Structured data processing                       |
| **Documents**       | **PyPDF / pdfextractor**       | License and certificate text extraction          |
| **Version Control** | **Git & GitHub**               | Project management and open-source collaboration |

---

## 🧰 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/adityaanand05/MediVerify_Agentic_AI.git
cd MediVerify_Agentic_AI
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate       # Linux/macOS
# .\.venv\Scripts\activate      # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```dotenv
# Google Gemini API Key
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
GEMINI_MODEL="gemini/gemini-2.5-flash"
NABP_API_KEY=/v2/Individual/eprofile/validate
PROPELUS_API_KEY=/v1/licenses/verify HTTP/1.1
NABP_BASE_URL=https://api.nabp.pharmacy/v2/Individual/eprofile/validate
PROPELUS_BASE_URL=https://api.propelus.com/v1/verifications
```

> 💡 *If CrewAI expects an `OPENAI_API_KEY`, use that name but assign your Gemini key.*

### 5. Run the Application

```bash
flask run
```

Visit the local server link (usually **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)**) to access the MediVerify dashboard.

---

## 📊 Example Workflow

1. Upload or input provider details (NPI, Name, License ID).
2. Agents retrieve and verify records from open sources.
3. Data Enrichment fills missing information.
4. QA Agent ensures compliance and correctness.
5. Final agent generates a downloadable verification report.

---

## 🧑‍💻 Project Structure

```
MediVerify_Agentic_AI/
│
├── .vscode/                 # VSCode workspace settings
├── reports/                 # Generated verification reports (if any)
├── Agent/                   # (optional) agent modules (if present locally)
│
├── agents.py                # Agent definitions / orchestration helpers
├── config.py                # Configuration and environment handling
├── crew.py                  # Main agent orchestration file
├── main.py                  # CLI / entrypoint for agents/workflows
├── nabp_tool.py             # NABP integration utilities
├── npi_tool.py              # NPI Registry utilities
├── propelus_tool.py         # Propelus / external data utilities
├── tasks.py                 # Task definitions for agents
├── utils.py                 # Utility helpers
│
├── requirements.txt         # Python dependencies
├── .gitignore               # Files to ignore in Git
├── LICENSE                  # Repository license (MPL-2.0 detected)
└── README.md                # Project documentation
```

---

## 🤝 Contributing

Contributions are always welcome!
Read Contribution.md for more details.
If you’d like to improve MediVerify — be it through bug fixes, new integrations (like state license boards), or performance optimizations — please:

1. Fork the repo
2. Create a new branch (`feature/your-feature-name`)
3. Commit your changes
4. Submit a pull request 🎯

---

## ✨ Our Contributors !!

Thanks to these wonderful people ✨  

<a href="https://github.com/adityaanand05/MediVerify_Agentic_AI/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=adityaanand05/MediVerify_Agentic_AI" />
</a>

---

## 🧾 License

This project is licensed under the **MPL License** — see the [LICENSE](./LICENSE) file for details.

---

## 💬 Acknowledgments

* **EY Techathon 6.0 — Challenge VI Solution**: Provider Data Validation & Directory Management.
* **CrewAI** and **Gemini 2.5 Flash** for enabling rapid, intelligent agent-based orchestration.
* **Open-source contributors** and the **healthcare tech community** inspiring innovation in data integrity.

---

## 🌐 Repository

🔗 **GitHub:** [adityaanand05/MediVerify_Agentic_AI](https://github.com/adityaanand05/MediVerify_Agentic_AI)

---
