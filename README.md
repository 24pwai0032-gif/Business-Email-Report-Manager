# Business Email and Report Manager
**Agentic AI Bootcamp — atomcamp | Weekly Project Assignment**

A complete AI-powered business communication and reporting system built on the
Groq API (free tier). The assistant uses `llama-3.3-70b-versatile` with function
calling to intelligently chain tools before generating output.

Designed for business professionals who need to draft emails, produce reports,
process meeting notes, analyze sales data, and communicate with clients — all
from a single tool.

---

## What It Does

**Smart Email Writer** — Describe the purpose, choose a recipient type and tone,
and get a fully structured business email back. The assistant can optionally
search for current market data and weave it into the email before sending.

**Report Generator** — Pass in monthly or quarterly numbers and get a formatted
business report with an executive summary, computed metrics, trend analysis, and
five concrete recommendations. Works with both dict and list data.

**Meeting Summarizer** — Paste raw meeting notes and get back a clean structured
summary including key discussion points, decisions made, action items with owners,
and the next meeting date if mentioned.

**Business Data Analyzer** — Ask a plain-English question about your sales or
revenue data. The assistant calls the appropriate statistical tools automatically
and returns the answer alongside interpretation and recommendations.

**Client Communication Drafter** — Generate polished, ready-to-send client
communications: project proposals, status updates, responses to inquiries, and
follow-up messages — each tailored to the client and situation.

---

## Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | Smart Email Writer | Formal, professional, or friendly emails for any recipient type. Optional web research before writing. |
| 2 | Report Generator | Structured reports with executive summary, key metrics, analysis, and recommendations from raw numbers. |
| 3 | Meeting Summarizer | Converts messy notes into clean summaries with key points, decisions, action items, and next steps. |
| 4 | Business Data Analyzer | Natural language queries on sales, revenue, and KPI datasets with computed statistics. |
| 5 | Client Communication Drafter | Proposals, status updates, follow-ups, and responses for client-facing communication. |

---

## Tools

| # | Tool | Description |
|---|------|-------------|
| 1 | Calculator | Evaluates financial expressions — percentages, growth rates, compound interest, ratios. |
| 2 | Web Search | Mock search returning realistic business and market intelligence (replaceable with a real API). |
| 3 | Data Analyzer | Computes sum, average, max, min, median, std deviation, trend direction, and growth rate. |
| 4 | Report Formatter | Returns the correct section structure and KPI labels for each report type. |

---

## Requirements

- Python 3.9 or higher
- A free Groq API key — get one at https://console.groq.com

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/business-assistant.git
cd business-assistant

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up your API key
cp .env.example .env
# Open .env and replace the placeholder with your real Groq API key
```

---

## Running the Assistant

```bash
python business_assistant.py
```

This launches the interactive menu:

```
============================================================
  Business Email and Report Manager
============================================================
  1. Write Email
  2. Generate Report
  3. Summarize Meeting
  4. Analyze Business Data
  5. Draft Client Communication
  0. Exit
============================================================
```

Type the number of the feature you want and follow the prompts.

---

## Usage Examples

### 1. Write Email

```
Select option: 1
  Purpose        : Announce Q2 sales results. Revenue was PKR 12.5M, up 28% from Q1.
  Recipient type : stakeholder
  Tone           : formal
  Research topic : (press Enter to skip)
```

To add market context from web search before writing:
```
  Research topic : tech industry market trends 2026
```

Recipient options: `client`, `team`, `stakeholder`, `supplier`, `investor`, `partner`
Tone options: `formal`, `professional`, `friendly`

---

### 2. Generate Report

```
Select option: 2
  Report type : quarterly
  Period      : Q1 2026
  Data        : {"Jan": 50000, "Feb": 65000, "Mar": 80000}
```

Data can be a JSON object (with month/period labels) or a JSON list of numbers.
Report type options: `sales`, `revenue`, `performance`, `quarterly`, `marketing`

The assistant will call the data analyzer and calculator tools automatically,
then produce a formatted report with:
- Executive summary
- Key metrics (total, average, peak, growth rate, trend)
- Data analysis paragraph
- Five recommendations

---

### 3. Summarize Meeting

```
Select option: 3
  Paste meeting notes. Type END on a new line when done.

  > Discussed Q3 marketing plan. Budget approved at PKR 500k.
  > Sara to lead the campaign. Launch date set for June 1st.
  > Ahmed to prepare creative brief by May 30. Next meeting June 5.
  > END

  Meeting date : May 22, 2026
  Attendees    : Sara, Ahmed, Finance Team
```

Output structure:
```
===========================================
MEETING SUMMARY
===========================================
Date      : May 22, 2026
Attendees : Sara, Ahmed, Finance Team

SUMMARY
...

KEY DISCUSSION POINTS
- ...

DECISIONS MADE
1. ...

ACTION ITEMS
- Sara: Lead Q3 campaign
- Ahmed: Prepare creative brief by May 30

NEXT MEETING: June 5, 2026
===========================================
```

---

### 4. Analyze Business Data

```
Select option: 4
  Your question : What is the average monthly revenue and overall growth rate?
  Data          : {"Jan": 50000, "Feb": 55000, "Mar": 62000, "Apr": 68000}
```

The assistant computes all statistics using the data analyzer tool, then answers
your specific question in plain language with an interpretation and recommendation.

---

### 5. Draft Client Communication

```
Select option: 5
  Type    : proposal
  Client  : NexaTech Solutions
  Context : ERP implementation, 4-month timeline, PKR 2.5M budget,
            covering accounting, HR, inventory, and reporting modules
  Tone    : professional
```

Communication type options: `proposal`, `status_update`, `response`, `follow_up`

---

## Using the API Directly

```python
import os
from dotenv import load_dotenv
from business_assistant import BusinessAssistant

load_dotenv()
assistant = BusinessAssistant(api_key=os.environ["GROQ_API_KEY"])

# Write an email
print(assistant.write_email(
    purpose="Announce Q2 sales results to our investors",
    recipient="stakeholder",
    tone="formal"
))

# Generate a report
data = {"Jan": 50000, "Feb": 65000, "Mar": 80000}
print(assistant.generate_report("quarterly", data, "Q1 2026"))

# Summarize a meeting
notes = """
Approved Q3 marketing budget at PKR 500k. Sara to lead. Launch June 1st.
Ahmed preparing creative brief by May 30. Next meeting June 5.
"""
print(assistant.summarize_meeting(notes, date="May 22, 2026"))

# Analyze data
print(assistant.analyze_business_data(
    "What is the average revenue and overall growth rate?",
    data
))

# Draft client communication
print(assistant.draft_client_communication(
    comm_type="proposal",
    client="NexaTech Solutions",
    context="ERP system, 4 months, PKR 2.5M",
    tone="professional"
))
```

---

## Running Tests

```bash
# Run all tests
python -m pytest tests/test_features.py -v

# Run unit tests only (no API key required)
python -m pytest tests/test_features.py -v -m unit

# Run integration tests (requires GROQ_API_KEY)
python -m pytest tests/test_features.py -v -m integration
```

Test coverage:
- 83 unit tests covering all four tool functions — no API key required
- 37 integration tests covering all five assistant features
- Edge cases: empty inputs, invalid types, boundary values, error handling

---

## File Structure

```
business-assistant/
├── business_assistant.py        Main program and interactive CLI
├── tools.py                     Tool functions and Groq tool schemas
├── requirements.txt             Python dependencies
├── .env.example                 API key template
├── README.md                    This file
├── examples/
│   ├── email_examples.txt       Email writer usage examples
│   ├── report_examples.txt      Report generator usage examples
│   └── meeting_examples.txt     Meeting summarizer usage examples
└── tests/
    ├── __init__.py
    └── test_features.py         Full test suite (120 tests)
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes | Your Groq API key |

---

## Getting a Free Groq API Key

1. Go to https://console.groq.com
2. Sign up for a free account
3. Navigate to **API Keys** and create a new key
4. Paste the key into your `.env` file (copy from `.env.example`)

For Google Colab: click the lock icon in the left sidebar (Secrets),
add a secret named `groq`, and paste your key as the value.

---

## Notes

- The web search tool is a mock by default. To use real search results, replace
  the `web_search` function in `tools.py` with a call to SerpAPI, Tavily, or
  the Brave Search API.
- The agentic loop runs a maximum of 8 iterations per request to prevent runaway
  tool chains.
- All tool functions return JSON strings and are fully compatible with the Groq
  function-calling protocol.
- The `process_request()` method auto-routes plain-text input to the correct
  feature based on keyword detection.

---

*Built for atomcamp Agentic AI Bootcamp — Weekly Project Assignment*
