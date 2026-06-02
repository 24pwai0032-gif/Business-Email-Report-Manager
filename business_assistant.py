"""
business_assistant.py
---------------------
Business Email and Report Manager
Agentic AI Bootcamp - atomcamp | Weekly Project

A complete AI-powered business communication and reporting assistant
built on top of the Groq API (free tier, llama-3.3-70b-versatile).

Features:
    1. Smart Email Writer         - Draft professional emails with optional research
    2. Report Generator           - Create structured reports from numeric data
    3. Meeting Summarizer         - Convert raw notes to action-item summaries
    4. Business Data Analyzer     - Answer natural language queries about data
    5. Client Communication       - Proposals, status updates, follow-ups, responses

Usage:
    python business_assistant.py
"""

import json
import os
from datetime import datetime

from dotenv import load_dotenv
from groq import Groq

from tools import ALL_TOOL_SCHEMAS, TOOL_FUNCTIONS

# Load GROQ_API_KEY from .env file if present
load_dotenv()


# ==============================================================
# BusinessAssistant class
# ==============================================================

class BusinessAssistant:
    """
    Main orchestrator for the Business Email and Report Manager.

    Attributes:
        client    : Groq API client
        tools     : List of tool schemas passed to every LLM call
        functions : Dict mapping tool names to callable Python functions
    """

    MODEL      = "llama-3.3-70b-versatile"
    MAX_TOKENS = 1500

    def __init__(self, api_key: str):
        """
        Initialize the assistant.

        Args:
            api_key: Groq API key. Get one free at https://console.groq.com

        Raises:
            ValueError: If api_key is empty or None.
        """
        if not api_key or not api_key.strip():
            raise ValueError(
                "GROQ_API_KEY is missing.\n"
                "  Option 1: Set it in a .env file  ->  GROQ_API_KEY=your-key\n"
                "  Option 2: export GROQ_API_KEY=your-key  (shell)\n"
                "  Option 3: Pass it directly       ->  BusinessAssistant(api_key='...')"
            )

        self.client    = Groq(api_key=api_key)
        self.tools     = ALL_TOOL_SCHEMAS
        self.functions = TOOL_FUNCTIONS

        print("BusinessAssistant initialized.")
        print(f"  Model  : {self.MODEL}")
        print(f"  Tools  : {', '.join(self.functions.keys())}")

    # ----------------------------------------------------------
    # Internal helpers
    # ----------------------------------------------------------

    def _execute_tool(self, tool_name: str, tool_args: dict) -> str:
        """
        Dispatch a tool call to the matching Python function.

        Args:
            tool_name: Name of the tool (must exist in self.functions).
            tool_args: Keyword arguments parsed from the LLM's tool call.

        Returns:
            JSON string result from the tool function.
        """
        if tool_name not in self.functions:
            return json.dumps({"error": f"Unknown tool: '{tool_name}'", "status": "error"})

        try:
            return self.functions[tool_name](**tool_args)
        except TypeError as exc:
            return json.dumps({
                "error":  f"Wrong arguments for '{tool_name}': {str(exc)}",
                "status": "error"
            })
        except Exception as exc:
            return json.dumps({
                "error":  f"Tool '{tool_name}' raised an exception: {str(exc)}",
                "status": "error"
            })

    def _call_llm(
        self,
        messages:    list,
        use_tools:   bool  = True,
        temperature: float = 0.6
    ) -> object:
        """
        Call the Groq Chat Completions API.

        Args:
            messages:    Full conversation list including system and user turns.
            use_tools:   Whether to attach tool schemas to the request.
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative).

        Returns:
            Groq ChatCompletion response object.
        """
        kwargs = {
            "model":       self.MODEL,
            "messages":    messages,
            "max_tokens":  self.MAX_TOKENS,
            "temperature": temperature,
        }
        if use_tools:
            kwargs["tools"]       = self.tools
            kwargs["tool_choice"] = "auto"

        return self.client.chat.completions.create(**kwargs)

    def _run_agent_loop(self, messages: list, verbose: bool = True) -> str:
        """
        Agentic loop: repeatedly call the LLM and execute any requested tools
        until the model returns a final text response with no further tool calls.

        Args:
            messages: Starting conversation message list.
            verbose:  If True, print each tool call as it executes.

        Returns:
            Final text response from the model.
        """
        max_iterations = 8
        iteration      = 0

        while iteration < max_iterations:
            iteration += 1
            response = self._call_llm(messages)
            msg      = response.choices[0].message

            # No tool calls — model has produced its final answer
            if not msg.tool_calls:
                return msg.content or "(No content returned.)"

            # Append the assistant's tool-request message to history
            messages.append(msg)

            # Execute every tool the model requested in this turn
            for tc in msg.tool_calls:
                tool_name = tc.function.name

                try:
                    tool_args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    tool_args = {}

                if verbose:
                    preview = ", ".join(
                        f"{k}={repr(v)[:50]}" for k, v in tool_args.items()
                    )
                    print(f"  [Tool] {tool_name}({preview})")

                tool_result = self._execute_tool(tool_name, tool_args)

                messages.append({
                    "role":         "tool",
                    "tool_call_id": tc.id,
                    "content":      tool_result,
                })

        return "(Max iterations reached. The request may be too complex — try simplifying it.)"

    # ----------------------------------------------------------
    # Feature 1: Smart Email Writer
    # ----------------------------------------------------------

    def write_email(
        self,
        purpose:        str,
        recipient:      str  = "stakeholder",
        tone:           str  = "formal",
        research_topic: str  = None
    ) -> str:
        """
        Write a complete, professional business email.

        Args:
            purpose:        What the email needs to accomplish.
            recipient:      Audience type. One of: client, team, stakeholder,
                            supplier, investor, partner. Default: stakeholder.
            tone:           Writing style. One of: formal, professional, friendly.
                            Default: formal.
            research_topic: If provided, the assistant searches for current market
                            data on this topic and weaves it into the email body.

        Returns:
            Complete email as a string including Subject line and body.
            Returns an error string if input validation fails.
        """
        # --- Input validation ---
        if not purpose or not purpose.strip():
            return "Error: Email purpose cannot be empty."

        recipient = recipient.lower().strip()
        valid_recipients = {"client", "team", "stakeholder", "supplier", "investor", "partner"}
        if recipient not in valid_recipients:
            print(f"  Warning: Unknown recipient '{recipient}'. Defaulting to 'stakeholder'.")
            recipient = "stakeholder"

        tone = tone.lower().strip()
        valid_tones = {"formal", "professional", "friendly"}
        if tone not in valid_tones:
            print(f"  Warning: Unknown tone '{tone}'. Defaulting to 'professional'.")
            tone = "professional"

        # --- System prompt ---
        system_prompt = f"""You are a senior business communication specialist.
Write complete, professional business emails ready to send.

Recipient type : {recipient.upper()}
Tone           : {tone.upper()}

Tone guidelines:
  formal       - Strictly professional. Full sentences. Titles and surnames. No contractions.
  professional - Clear and business-appropriate. Balanced. Respectful but not stiff.
  friendly     - Warm and approachable. Still professional. First names acceptable.

Output format (follow exactly):
Subject: [subject line here]

Dear [Recipient Name / Title],

[Opening paragraph — state the purpose clearly]

[Body paragraphs — details, supporting data, context]

[Closing paragraph — call to action or next steps]

[Sign-off],
[Your Name]
[Title], [Company Name]"""

        research_note = ""
        if research_topic and research_topic.strip():
            research_note = (
                f"\nBefore writing, call web_search with query '{research_topic}' "
                "and incorporate the most relevant findings into the email body."
            )

        user_message = (
            f"Write a {tone} business email to a {recipient}.\n"
            f"Purpose: {purpose}{research_note}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message},
        ]

        print(f"\nFeature 1: Smart Email Writer")
        print(f"  Recipient : {recipient}  |  Tone : {tone}  |  Research : {'Yes' if research_topic else 'No'}")
        print("  Processing...")

        try:
            return self._run_agent_loop(messages)
        except Exception as exc:
            return f"Error: Email generation failed — {str(exc)}"

    # ----------------------------------------------------------
    # Feature 2: Report Generator
    # ----------------------------------------------------------

    def generate_report(
        self,
        report_type: str,
        data:        "dict | list",
        period:      str
    ) -> str:
        """
        Generate a professionally structured business report from numeric data.

        Args:
            report_type: Type of report. One of: sales, revenue, performance,
                         quarterly, marketing.
            data:        Business data as a Python dict ({"Jan": 50000, "Feb": 65000})
                         or list ([50000, 65000, 80000]).
            period:      Reporting period label, e.g. "Q1 2026" or "H1 2026".

        Returns:
            Formatted report as a multi-line string.
            Returns an error string if input validation fails.
        """
        # --- Input validation ---
        if not data:
            return "Error: Data cannot be empty."
        if not period or not period.strip():
            return "Error: Period cannot be empty."

        report_type = report_type.lower().strip()
        valid_types = {"sales", "revenue", "performance", "quarterly", "marketing"}
        if report_type not in valid_types:
            print(f"  Warning: Unknown report type '{report_type}'. Defaulting to 'sales'.")
            report_type = "sales"

        data_json = json.dumps(data)

        # --- System prompt ---
        system_prompt = """You are a senior business analyst who writes clear, data-driven reports.

When asked to generate a report:
  Step 1 - Call format_report to retrieve the correct report structure and KPI labels.
  Step 2 - Call analyze_data with operation='all' to compute all statistics.
  Step 3 - Call calculate to compute the growth rate:
           expression = '(last_value - first_value) / first_value * 100'
  Step 4 - Write the complete report using this exact layout:

============================================
[REPORT TITLE IN CAPS]
============================================
Date   : [current date from format_report]
Period : [reporting period]

EXECUTIVE SUMMARY
[2-3 sentence overview of key findings and what they mean for the business]

KEY METRICS
- Total        : [value]
- Average      : [value]
- Peak Period  : [label] ([value])
- Lowest Period: [label] ([value])
- Growth Rate  : [value]%
- Trend        : [Increasing / Stable / Decreasing]

DATA ANALYSIS
[One substantial paragraph explaining the numbers, notable patterns, and business implications]

RECOMMENDATIONS
1. [Concrete recommendation supported by the data]
2. [Concrete recommendation supported by the data]
3. [Concrete recommendation supported by the data]
4. [Concrete recommendation supported by the data]
5. [Concrete recommendation supported by the data]
============================================"""

        user_message = (
            f"Generate a {report_type} report for period: {period}\n\n"
            f"Data: {data_json}\n\n"
            "Follow the four steps in the system instructions exactly."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message},
        ]

        print(f"\nFeature 2: Report Generator")
        print(f"  Type : {report_type}  |  Period : {period}  |  Data points : {len(data)}")
        print("  Processing...")

        try:
            return self._run_agent_loop(messages)
        except Exception as exc:
            return f"Error: Report generation failed — {str(exc)}"

    # ----------------------------------------------------------
    # Feature 3: Meeting Summarizer
    # ----------------------------------------------------------

    def summarize_meeting(
        self,
        notes:     str,
        date:      str        = None,
        attendees: list       = None
    ) -> str:
        """
        Convert raw meeting notes into a structured summary with action items.

        Args:
            notes:     Raw meeting notes as a plain text string.
            date:      Meeting date string. Defaults to today if not provided.
            attendees: Optional list of attendee names/roles.

        Returns:
            Structured meeting summary as a multi-line string.
            Returns an error string if input validation fails.
        """
        # --- Input validation ---
        if not notes or not notes.strip():
            return "Error: Meeting notes cannot be empty."
        if len(notes.split()) < 10:
            return "Error: Notes are too short. Please provide more detail (minimum 10 words)."

        meeting_date  = date if date and date.strip() else datetime.now().strftime("%B %d, %Y")
        attendees_str = ", ".join(attendees) if attendees else "Not specified"

        # --- System prompt ---
        system_prompt = """You are an executive assistant who produces structured meeting summaries.
Extract every important piece of information from the notes and organise it clearly.

Output EXACTLY this format — do not skip any section:

===========================================
MEETING SUMMARY
===========================================
Date      : [date]
Attendees : [attendees]

SUMMARY
[2-3 sentences capturing what the meeting achieved overall]

KEY DISCUSSION POINTS
- [point]
- [point]
(add as many bullet points as needed)

DECISIONS MADE
1. [decision]
2. [decision]
(add as many numbered items as needed)

ACTION ITEMS
- [Owner / Team]: [action] by [deadline if mentioned]
(write "No specific assignments mentioned" if none were recorded)

NEXT MEETING: [date and time if mentioned, otherwise "Not scheduled"]
==========================================="""

        user_message = (
            f"Summarise these meeting notes.\n\n"
            f"Date      : {meeting_date}\n"
            f"Attendees : {attendees_str}\n\n"
            f"Raw Notes:\n{notes}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message},
        ]

        print(f"\nFeature 3: Meeting Summarizer")
        print(f"  Date : {meeting_date}  |  Attendees : {attendees_str}")
        print("  Processing...")

        try:
            # Meeting summaries do not require tool calls
            response = self._call_llm(messages, use_tools=False)
            return response.choices[0].message.content.strip()
        except Exception as exc:
            return f"Error: Meeting summarization failed — {str(exc)}"

    # ----------------------------------------------------------
    # Feature 4: Business Data Analyzer
    # ----------------------------------------------------------

    def analyze_business_data(
        self,
        query: str,
        data:  "dict | list"
    ) -> str:
        """
        Answer a natural language question about a business dataset.

        Args:
            query: Plain-English question, e.g.
                   "What is the average monthly revenue and growth rate?"
            data:  Business data as a Python dict or list of numbers.

        Returns:
            Formatted analysis including computed metrics, interpretation,
            and recommendations.
            Returns an error string if input validation fails.
        """
        # --- Input validation ---
        if not query or not query.strip():
            return "Error: Query cannot be empty."
        if not data:
            return "Error: Data cannot be empty."

        data_json = json.dumps(data)

        # --- System prompt ---
        system_prompt = """You are a business data analyst.
Answer natural language queries about business datasets precisely.

Steps to follow for every request:
  1. Call analyze_data with operation='all' to compute all statistics.
  2. Call calculate for any additional metric the query specifically asks for
     (e.g. percentage change, ratio, compound growth).
  3. Write the answer in this exact format:

ANALYSIS RESULTS
==================
[Direct answer to the query with the key computed value(s) prominently stated]

KEY METRICS
- [metric label]: [value]
- [metric label]: [value]
(list every relevant metric)

INTERPRETATION
[2-3 sentences explaining what these numbers mean for the business in plain language]

RECOMMENDATION
[1-2 specific, actionable steps the business should consider based on the data]"""

        user_message = (
            f"Query : {query}\n\n"
            f"Data  : {data_json}\n\n"
            "Follow the steps in the system instructions."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message},
        ]

        print(f"\nFeature 4: Business Data Analyzer")
        print(f"  Query : {query[:80]}{'...' if len(query) > 80 else ''}")
        print("  Processing...")

        try:
            return self._run_agent_loop(messages)
        except Exception as exc:
            return f"Error: Data analysis failed — {str(exc)}"

    # ----------------------------------------------------------
    # Feature 5: Client Communication Drafter
    # ----------------------------------------------------------

    def draft_client_communication(
        self,
        comm_type: str,
        client:    str,
        context:   str,
        tone:      str = "professional"
    ) -> str:
        """
        Draft a professional client-facing communication.

        Args:
            comm_type: Communication type. One of:
                       proposal, status_update, response, follow_up.
            client:    Client name or company name.
            context:   Details about the project, situation, or request.
            tone:      One of: formal, professional, friendly. Default: professional.

        Returns:
            Complete communication as a ready-to-send string.
            Returns an error string if input validation fails.
        """
        # --- Input validation ---
        if not client or not client.strip():
            return "Error: Client name cannot be empty."
        if not context or not context.strip():
            return "Error: Context cannot be empty."

        comm_type = comm_type.lower().strip().replace(" ", "_")
        valid_types = {"proposal", "status_update", "response", "follow_up"}
        if comm_type not in valid_types:
            print(f"  Warning: Unknown type '{comm_type}'. Defaulting to 'response'.")
            comm_type = "response"

        tone = tone.lower().strip()
        if tone not in {"formal", "professional", "friendly"}:
            tone = "professional"

        type_guidance = {
            "proposal": (
                "Write a compelling project or business proposal. "
                "Cover: scope of work, timeline, value delivered, investment required, "
                "and a clear call to action to move forward."
            ),
            "status_update": (
                "Write a clear project status update. "
                "Cover: work completed since last update, current status, "
                "upcoming milestones, any risks or blockers, and next steps."
            ),
            "response": (
                "Write a professional response to a client inquiry. "
                "Address every point raised, provide clear answers, "
                "and indicate any required next actions."
            ),
            "follow_up": (
                "Write a polite but purposeful follow-up message. "
                "Reference the previous interaction, state what you are following up on, "
                "and include one clear next step or ask."
            ),
        }

        system_prompt = (
            f"You are a senior client relationship manager.\n"
            f"Draft professional client-facing communications that are ready to send.\n\n"
            f"Communication type : {comm_type.upper().replace('_', ' ')}\n"
            f"Tone               : {tone.upper()}\n\n"
            f"Instruction: {type_guidance[comm_type]}\n\n"
            "Output a complete communication with:\n"
            "  - Professional greeting addressing the client by name\n"
            "  - Well-structured body (2-4 paragraphs suited to the type)\n"
            "  - Clear call-to-action or stated next step\n"
            "  - Professional closing with signature placeholder"
        )

        user_message = (
            f"Draft a {tone} {comm_type.replace('_', ' ')} for client: {client}\n\n"
            f"Context and details:\n{context}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message},
        ]

        print(f"\nFeature 5: Client Communication Drafter")
        print(f"  Type : {comm_type}  |  Client : {client}  |  Tone : {tone}")
        print("  Processing...")

        try:
            # Client communications rarely need tools; skip to reduce latency
            response = self._call_llm(messages, use_tools=False)
            return response.choices[0].message.content.strip()
        except Exception as exc:
            return f"Error: Client communication drafting failed — {str(exc)}"

    # ----------------------------------------------------------
    # Main router
    # ----------------------------------------------------------

    def process_request(self, request: str) -> str:
        """
        Route a plain-text request to the appropriate feature automatically.

        Recognised trigger phrases:
            Email      : "write email", "draft email", "compose email", "email to"
            Report     : "generate report", "create report", "sales report", "quarterly report"
            Meeting    : "meeting notes", "summarize meeting", "action items from"
            Data       : "analyze data", "analyze sales", "growth rate", "average revenue"
            Client     : "proposal", "status update", "follow up", "follow-up"

        Falls back to a general-purpose LLM answer for everything else.

        Args:
            request: User's plain-text request.

        Returns:
            Result string from the matched feature, or a direct LLM answer.
        """
        if not request or not request.strip():
            return "Error: Request cannot be empty."

        r = request.lower()

        # Route: Email
        if any(kw in r for kw in ["write email", "draft email", "compose email", "email to"]):
            tone      = "formal" if "formal" in r else "friendly" if "friendly" in r else "professional"
            recipient = next(
                (rec for rec in ["client", "team", "supplier", "investor", "partner"] if rec in r),
                "stakeholder"
            )
            return self.write_email(request, recipient=recipient, tone=tone)

        # Route: Report
        if any(kw in r for kw in ["generate report", "create report", "write report",
                                   "business report", "quarterly report", "sales report"]):
            return (
                "To generate a report, call:\n"
                "  assistant.generate_report(report_type, data, period)\n\n"
                "Example:\n"
                "  data = {\"Jan\": 50000, \"Feb\": 65000, \"Mar\": 80000}\n"
                "  assistant.generate_report(\"quarterly\", data, \"Q1 2026\")"
            )

        # Route: Meeting
        if any(kw in r for kw in ["meeting notes", "summarize meeting",
                                   "meeting summary", "action items from"]):
            return (
                "To summarize a meeting, call:\n"
                "  assistant.summarize_meeting(notes, date, attendees)\n\n"
                "Example:\n"
                "  assistant.summarize_meeting(notes=\"...\", date=\"May 22, 2026\")"
            )

        # Route: Data analysis
        if any(kw in r for kw in ["analyze data", "analyze sales", "average revenue",
                                   "total sales", "growth rate", "what is the average"]):
            return (
                "To analyze data, call:\n"
                "  assistant.analyze_business_data(query, data)\n\n"
                "Example:\n"
                "  data = {\"Jan\": 50000, \"Feb\": 65000}\n"
                "  assistant.analyze_business_data(\"What is the average and growth rate?\", data)"
            )

        # Route: Client communication
        if any(kw in r for kw in ["proposal", "status update", "follow up",
                                   "follow-up", "client response", "draft for client"]):
            return (
                "To draft a client communication, call:\n"
                "  assistant.draft_client_communication(comm_type, client, context, tone)\n\n"
                "comm_type options: proposal, status_update, response, follow_up"
            )

        # Fallback: general LLM answer with tool access
        messages = [
            {
                "role":    "system",
                "content": (
                    "You are a helpful business assistant. "
                    "Answer business questions clearly and concisely. "
                    "Use available tools when they would improve accuracy."
                )
            },
            {"role": "user", "content": request},
        ]
        try:
            return self._run_agent_loop(messages)
        except Exception as exc:
            return f"Error processing request: {str(exc)}"


# ==============================================================
# Interactive CLI
# ==============================================================

MENU = """
============================================================
  Business Email and Report Manager
  Powered by Groq API (llama-3.3-70b-versatile)
============================================================
  1. Write Email
  2. Generate Report
  3. Summarize Meeting
  4. Analyze Business Data
  5. Draft Client Communication
  0. Exit
============================================================"""

HELP = """
USAGE EXAMPLES
--------------
1. Write Email:
   Purpose   : Announce Q2 sales results, revenue PKR 12.5M, up 28% QoQ
   Recipient : stakeholder
   Tone      : formal
   Research  : (press Enter to skip)

2. Generate Report:
   Type      : quarterly
   Period    : Q1 2026
   Data      : {"Jan": 50000, "Feb": 65000, "Mar": 80000}

3. Summarize Meeting:
   Paste raw notes, type END on a new line to finish

4. Analyze Data:
   Query : What is the average revenue and overall growth rate?
   Data  : {"Jan": 50000, "Feb": 58000, "Mar": 65000}

5. Draft Client Communication:
   Type    : proposal
   Client  : NexaTech Solutions
   Context : ERP implementation, 4 months, PKR 2.5M budget
   Tone    : professional
"""


def _get_input(prompt: str, default: str = "") -> str:
    """Prompt the user and return stripped input, falling back to default."""
    try:
        value = input(prompt).strip()
        return value if value else default
    except (EOFError, KeyboardInterrupt):
        return default


def _get_json_data() -> "dict | list | None":
    """Prompt for a JSON string and return the parsed object, or None on failure."""
    print("  Enter data as JSON.")
    print("  Dict format : {\"Jan\": 50000, \"Feb\": 65000}")
    print("  List format : [50000, 65000, 80000]")
    raw = _get_input("  Data: ")
    if not raw:
        print("  No data entered.")
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"  Invalid JSON: {exc}")
        return None


def run_interactive(assistant: BusinessAssistant) -> None:
    """Run the menu-driven interactive CLI session."""
    print(MENU)

    while True:
        try:
            choice = input("\nSelect option (0-5, or 'help'): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nSession ended.")
            break

        if choice == "help":
            print(HELP)
            continue

        if choice == "0":
            print("Session ended. Goodbye.")
            break

        # ── Feature 1: Email ──────────────────────────────────
        elif choice == "1":
            print("\n--- Write Email ---")
            purpose   = _get_input("  Purpose        : ")
            recipient = _get_input("  Recipient type [stakeholder]: ", "stakeholder")
            tone      = _get_input("  Tone           [formal]: ",      "formal")
            research  = _get_input("  Research topic [Enter to skip]: ") or None

            if not purpose:
                print("  Error: Purpose is required.")
                continue

            result = assistant.write_email(purpose, recipient=recipient,
                                           tone=tone, research_topic=research)
            print(f"\n{result}")

        # ── Feature 2: Report ─────────────────────────────────
        elif choice == "2":
            print("\n--- Generate Report ---")
            report_type = _get_input("  Report type [sales]: ", "sales")
            period      = _get_input("  Period      [Q1 2026]: ", "Q1 2026")
            data        = _get_json_data()

            if data is None:
                continue

            result = assistant.generate_report(report_type, data, period)
            print(f"\n{result}")

        # ── Feature 3: Meeting ────────────────────────────────
        elif choice == "3":
            print("\n--- Summarize Meeting ---")
            print("  Paste meeting notes. Type END on a new line when done.")
            lines = []
            while True:
                try:
                    line = input()
                except (EOFError, KeyboardInterrupt):
                    break
                if line.strip().upper() == "END":
                    break
                lines.append(line)

            notes     = "\n".join(lines)
            date      = _get_input("  Meeting date [today]: ") or None
            att_input = _get_input("  Attendees, comma-separated [Enter to skip]: ")
            attendees = [a.strip() for a in att_input.split(",")] if att_input else None

            if not notes:
                print("  Error: Notes cannot be empty.")
                continue

            result = assistant.summarize_meeting(notes, date=date, attendees=attendees)
            print(f"\n{result}")

        # ── Feature 4: Data Analyzer ──────────────────────────
        elif choice == "4":
            print("\n--- Analyze Business Data ---")
            query = _get_input("  Your question: ")
            data  = _get_json_data()

            if not query:
                print("  Error: Query is required.")
                continue
            if data is None:
                continue

            result = assistant.analyze_business_data(query, data)
            print(f"\n{result}")

        # ── Feature 5: Client Communication ──────────────────
        elif choice == "5":
            print("\n--- Draft Client Communication ---")
            comm_type = _get_input("  Type [proposal/status_update/response/follow_up]: ", "response")
            client    = _get_input("  Client name/company: ")
            context   = _get_input("  Context and details: ")
            tone      = _get_input("  Tone [professional]: ", "professional")

            if not client or not context:
                print("  Error: Client name and context are required.")
                continue

            result = assistant.draft_client_communication(comm_type, client, context, tone)
            print(f"\n{result}")

        else:
            print("  Invalid option. Enter a number from 0 to 5, or 'help'.")


# ==============================================================
# Entry point
# ==============================================================

if __name__ == "__main__":
    api_key = os.environ.get("GROQ_API_KEY", "")

    if not api_key:
        print("GROQ_API_KEY not found in environment.")
        print("Create a .env file based on .env.example and add your key.")
        raise SystemExit(1)

    try:
        assistant = BusinessAssistant(api_key=api_key)
    except ValueError as exc:
        print(str(exc))
        raise SystemExit(1)

    run_interactive(assistant)
