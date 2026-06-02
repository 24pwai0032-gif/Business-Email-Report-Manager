"""
tests/test_features.py
----------------------
Test suite for the Business Email and Report Manager.
Agentic AI Bootcamp - atomcamp | Weekly Project

Coverage:
    Unit tests  - every tool function tested in isolation
    Integration - BusinessAssistant methods called against the real Groq API
    Edge cases  - empty inputs, invalid types, boundary values

Running:
    # Run all tests (requires GROQ_API_KEY in environment or .env)
    python -m pytest tests/test_features.py -v

    # Run only unit tests (no API key needed)
    python -m pytest tests/test_features.py -v -m unit

    # Run only integration tests
    python -m pytest tests/test_features.py -v -m integration

    # Run with visible stdout (useful to see tool call logs)
    python -m pytest tests/test_features.py -v -s
"""

import json
import os
import sys
import unittest

# Make sure the parent directory is on the path so imports work whether
# pytest is run from the project root or from inside tests/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools import (
    calculate,
    web_search,
    analyze_data,
    format_report,
    ALL_TOOL_SCHEMAS,
    TOOL_FUNCTIONS,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse(result: str) -> dict:
    """Parse a JSON tool result string and return the dict."""
    return json.loads(result)


def _is_success(result: str) -> bool:
    """Return True when the tool result carries status='success'."""
    try:
        return _parse(result).get("status") == "success"
    except json.JSONDecodeError:
        return False


def _is_error(result: str) -> bool:
    """Return True when the tool result carries status='error'."""
    try:
        return _parse(result).get("status") == "error"
    except json.JSONDecodeError:
        return False


# ===========================================================================
# UNIT TESTS — Tool 1: calculate
# ===========================================================================

class TestCalculate(unittest.TestCase):
    """Unit tests for the calculate() tool function."""

    # --- Happy-path arithmetic ---

    def test_simple_addition(self):
        result = _parse(calculate("2 + 3"))
        self.assertEqual(result["status"], "success")
        self.assertAlmostEqual(result["result"], 5.0)

    def test_simple_subtraction(self):
        result = _parse(calculate("100 - 37"))
        self.assertEqual(result["status"], "success")
        self.assertAlmostEqual(result["result"], 63.0)

    def test_multiplication(self):
        result = _parse(calculate("50000 * 0.15"))
        self.assertEqual(result["status"], "success")
        self.assertAlmostEqual(result["result"], 7500.0)

    def test_division(self):
        result = _parse(calculate("120 / 4"))
        self.assertEqual(result["status"], "success")
        self.assertAlmostEqual(result["result"], 30.0)

    def test_exponentiation(self):
        result = _parse(calculate("2 ** 10"))
        self.assertEqual(result["status"], "success")
        self.assertAlmostEqual(result["result"], 1024.0)

    def test_percentage_of_value(self):
        # 18% of 50000
        result = _parse(calculate("50000 * 0.18"))
        self.assertEqual(result["status"], "success")
        self.assertAlmostEqual(result["result"], 9000.0)

    def test_growth_rate_formula(self):
        # (75000 - 50000) / 50000 * 100 = 50%
        result = _parse(calculate("(75000 - 50000) / 50000 * 100"))
        self.assertEqual(result["status"], "success")
        self.assertAlmostEqual(result["result"], 50.0)

    def test_compound_interest(self):
        # 100000 * (1 + 0.12) ** 3 = 140492.8
        result = _parse(calculate("100000 * (1 + 0.12) ** 3"))
        self.assertEqual(result["status"], "success")
        self.assertAlmostEqual(result["result"], 140492.8, places=0)

    def test_sqrt(self):
        result = _parse(calculate("sqrt(144)"))
        self.assertEqual(result["status"], "success")
        self.assertAlmostEqual(result["result"], 12.0)

    def test_float_result(self):
        result = _parse(calculate("1 / 3"))
        self.assertEqual(result["status"], "success")
        self.assertAlmostEqual(result["result"], 0.3333, places=3)

    def test_nested_parentheses(self):
        result = _parse(calculate("((100 + 200) * 3) / 9"))
        self.assertEqual(result["status"], "success")
        self.assertAlmostEqual(result["result"], 100.0)

    def test_expression_stored_in_result(self):
        expr   = "20 * 5"
        result = _parse(calculate(expr))
        self.assertEqual(result["expression"], expr)

    # --- Edge cases and errors ---

    def test_division_by_zero(self):
        result = _parse(calculate("10 / 0"))
        self.assertEqual(result["status"], "error")
        self.assertIn("zero", result["error"].lower())

    def test_empty_expression(self):
        self.assertTrue(_is_error(calculate("")))

    def test_whitespace_only(self):
        self.assertTrue(_is_error(calculate("   ")))

    def test_invalid_syntax(self):
        # "2 +* 3" is a genuine SyntaxError in Python
        self.assertTrue(_is_error(calculate("2 +* 3")))

    def test_disallowed_builtin(self):
        # __import__ should be blocked
        self.assertTrue(_is_error(calculate("__import__('os')")))

    def test_large_numbers(self):
        result = _parse(calculate("999999999 * 999999999"))
        self.assertEqual(result["status"], "success")


# ===========================================================================
# UNIT TESTS — Tool 2: web_search
# ===========================================================================

class TestWebSearch(unittest.TestCase):
    """Unit tests for the web_search() mock tool."""

    def test_returns_success_status(self):
        self.assertTrue(_is_success(web_search("market trends")))

    def test_returns_list_of_results(self):
        data = _parse(web_search("industry news"))
        self.assertIsInstance(data["results"], list)
        self.assertGreater(len(data["results"]), 0)

    def test_each_result_has_title_and_snippet(self):
        data = _parse(web_search("sales strategy"))
        for r in data["results"]:
            self.assertIn("title",   r)
            self.assertIn("snippet", r)

    def test_market_trends_keyword(self):
        data = _parse(web_search("market trends 2026"))
        self.assertTrue(_is_success(json.dumps(data)))
        self.assertGreater(len(data["results"]), 0)

    def test_email_best_practice_keyword(self):
        data = _parse(web_search("email best practices for B2B"))
        self.assertGreater(len(data["results"]), 0)

    def test_competitor_keyword(self):
        data = _parse(web_search("competitor analysis"))
        self.assertGreater(len(data["results"]), 0)

    def test_finance_keyword(self):
        data = _parse(web_search("business finance trends"))
        self.assertGreater(len(data["results"]), 0)

    def test_marketing_keyword(self):
        data = _parse(web_search("digital marketing ROI"))
        self.assertGreater(len(data["results"]), 0)

    def test_unknown_query_still_returns_results(self):
        data = _parse(web_search("obscure topic xyz 12345"))
        self.assertGreater(len(data["results"]), 0)

    def test_query_echoed_in_response(self):
        q    = "sales strategy for startups"
        data = _parse(web_search(q))
        self.assertEqual(data["query"], q)

    def test_result_count_matches_list_length(self):
        data = _parse(web_search("finance"))
        self.assertEqual(data["result_count"], len(data["results"]))

    def test_empty_query_returns_error(self):
        self.assertTrue(_is_error(web_search("")))

    def test_whitespace_query_returns_error(self):
        self.assertTrue(_is_error(web_search("   ")))


# ===========================================================================
# UNIT TESTS — Tool 3: analyze_data
# ===========================================================================

class TestAnalyzeData(unittest.TestCase):
    """Unit tests for the analyze_data() tool function."""

    LIST_DATA = json.dumps([50000, 55000, 60000, 65000, 70000, 75000])
    DICT_DATA = json.dumps({"Jan": 50000, "Feb": 55000, "Mar": 60000,
                            "Apr": 65000, "May": 70000, "Jun": 75000})
    SINGLE    = json.dumps([100])

    # --- List format ---

    def test_list_all_operation(self):
        result = _parse(analyze_data(self.LIST_DATA, "all"))
        self.assertEqual(result["status"], "success")
        r = result["result"]
        self.assertEqual(r["count"], 6)
        self.assertAlmostEqual(r["sum"], 375000.0)
        self.assertAlmostEqual(r["average"], 62500.0)
        self.assertEqual(r["max"]["value"], 75000.0)
        self.assertEqual(r["min"]["value"], 50000.0)

    def test_list_sum(self):
        result = _parse(analyze_data(self.LIST_DATA, "sum"))
        self.assertAlmostEqual(result["result"]["sum"], 375000.0)

    def test_list_average(self):
        result = _parse(analyze_data(self.LIST_DATA, "average"))
        self.assertAlmostEqual(result["result"]["average"], 62500.0)

    def test_list_max(self):
        result = _parse(analyze_data(self.LIST_DATA, "max"))
        self.assertAlmostEqual(result["result"]["max"], 75000.0)

    def test_list_min(self):
        result = _parse(analyze_data(self.LIST_DATA, "min"))
        self.assertAlmostEqual(result["result"]["min"], 50000.0)

    def test_list_median(self):
        result = _parse(analyze_data(self.LIST_DATA, "median"))
        self.assertAlmostEqual(result["result"]["median"], 62500.0)

    def test_list_std(self):
        result = _parse(analyze_data(self.LIST_DATA, "std"))
        self.assertIn("std_dev", result["result"])
        self.assertGreater(result["result"]["std_dev"], 0)

    def test_list_count(self):
        result = _parse(analyze_data(self.LIST_DATA, "count"))
        self.assertEqual(result["result"]["count"], 6)

    # --- Dict format ---

    def test_dict_all_operation(self):
        result = _parse(analyze_data(self.DICT_DATA, "all"))
        self.assertEqual(result["status"], "success")
        r = result["result"]
        self.assertEqual(r["count"], 6)
        self.assertAlmostEqual(r["sum"], 375000.0)

    def test_dict_labels_preserved(self):
        result = _parse(analyze_data(self.DICT_DATA, "all"))
        labels = result["result"]["labels"]
        self.assertIn("Jan", labels)
        self.assertIn("Jun", labels)

    def test_dict_max_label(self):
        result = _parse(analyze_data(self.DICT_DATA, "max"))
        self.assertEqual(result["result"]["label"], "Jun")

    def test_dict_min_label(self):
        result = _parse(analyze_data(self.DICT_DATA, "min"))
        self.assertEqual(result["result"]["label"], "Jan")

    # --- Trend detection ---

    def test_trend_increasing(self):
        data   = json.dumps([10, 20, 30, 40, 50, 60])
        result = _parse(analyze_data(data, "all"))
        self.assertEqual(result["result"]["trend"], "Increasing")

    def test_trend_decreasing(self):
        data   = json.dumps([60, 50, 40, 30, 20, 10])
        result = _parse(analyze_data(data, "all"))
        self.assertEqual(result["result"]["trend"], "Decreasing")

    def test_trend_stable(self):
        data   = json.dumps([100, 100, 100, 100])
        result = _parse(analyze_data(data, "all"))
        self.assertEqual(result["result"]["trend"], "Stable")

    # --- Growth rate ---

    def test_growth_rate_positive(self):
        data   = json.dumps([50000, 75000])
        result = _parse(analyze_data(data, "all"))
        self.assertAlmostEqual(result["result"]["growth_rate_percent"], 50.0)

    def test_growth_rate_negative(self):
        data   = json.dumps([100, 80])
        result = _parse(analyze_data(data, "all"))
        self.assertAlmostEqual(result["result"]["growth_rate_percent"], -20.0)

    def test_single_element_no_growth_rate(self):
        # growth_rate requires at least 2 values
        result = _parse(analyze_data(self.SINGLE, "all"))
        self.assertIsNone(result["result"]["growth_rate_percent"])

    # --- Error cases ---

    def test_empty_data_string(self):
        self.assertTrue(_is_error(analyze_data("")))

    def test_empty_json_list(self):
        self.assertTrue(_is_error(analyze_data("[]")))

    def test_invalid_json(self):
        self.assertTrue(_is_error(analyze_data("not json")))

    def test_non_numeric_list(self):
        self.assertTrue(_is_error(analyze_data('["a", "b", "c"]')))

    def test_unknown_operation(self):
        self.assertTrue(_is_error(analyze_data(self.LIST_DATA, "variance")))

    def test_default_operation_is_all(self):
        result = _parse(analyze_data(self.LIST_DATA))
        self.assertIn("sum",     result["result"])
        self.assertIn("average", result["result"])

    def test_negative_numbers(self):
        data   = json.dumps([-100, -50, 0, 50, 100])
        result = _parse(analyze_data(data, "all"))
        self.assertEqual(result["status"], "success")
        self.assertAlmostEqual(result["result"]["sum"], 0.0)
        self.assertAlmostEqual(result["result"]["average"], 0.0)

    def test_float_values(self):
        data   = json.dumps([1.5, 2.5, 3.5])
        result = _parse(analyze_data(data, "average"))
        self.assertAlmostEqual(result["result"]["average"], 2.5)


# ===========================================================================
# UNIT TESTS — Tool 4: format_report
# ===========================================================================

class TestFormatReport(unittest.TestCase):
    """Unit tests for the format_report() tool function."""

    def _call(self, report_type="sales", data='[50000]', period="Q1 2026"):
        return _parse(format_report(report_type, data, period))

    def test_sales_report_success(self):
        result = self._call("sales")
        self.assertEqual(result["status"], "success")

    def test_quarterly_report_success(self):
        result = self._call("quarterly")
        self.assertEqual(result["status"], "success")

    def test_revenue_report_success(self):
        result = self._call("revenue")
        self.assertEqual(result["status"], "success")

    def test_performance_report_success(self):
        result = self._call("performance")
        self.assertEqual(result["status"], "success")

    def test_marketing_report_success(self):
        result = self._call("marketing")
        self.assertEqual(result["status"], "success")

    def test_header_contains_period(self):
        result = self._call("sales", period="Q2 2026")
        self.assertIn("Q2 2026", result["header"])

    def test_sections_is_list(self):
        result = self._call()
        self.assertIsInstance(result["sections"], list)
        self.assertGreater(len(result["sections"]), 0)

    def test_kpis_is_list(self):
        result = self._call()
        self.assertIsInstance(result["kpis"], list)
        self.assertGreater(len(result["kpis"]), 0)

    def test_timestamp_present(self):
        result = self._call()
        self.assertIn("timestamp", result)
        self.assertTrue(len(result["timestamp"]) > 0)

    def test_period_echoed(self):
        result = self._call(period="H1 2026")
        self.assertEqual(result["period"], "H1 2026")

    def test_report_type_echoed(self):
        result = self._call("marketing")
        self.assertEqual(result["report_type"], "marketing")

    def test_data_echoed(self):
        data   = '{"Jan": 50000}'
        result = self._call(data=data)
        self.assertEqual(result["data_received"], data)

    def test_unknown_type_falls_back_to_sales(self):
        result = self._call("nonexistent_type")
        # Should not error — falls back to sales template
        self.assertEqual(result["status"], "success")

    def test_empty_period_returns_error(self):
        self.assertTrue(_is_error(format_report("sales", "[]", "")))

    def test_whitespace_period_returns_error(self):
        self.assertTrue(_is_error(format_report("sales", "[]", "   ")))

    def test_quarterly_has_executive_overview_section(self):
        result = self._call("quarterly")
        self.assertIn("Executive Overview", result["sections"])

    def test_sales_has_recommendations_section(self):
        result = self._call("sales")
        section_names = " ".join(result["sections"])
        self.assertIn("Recommendations", section_names)


# ===========================================================================
# UNIT TESTS — Tool registry
# ===========================================================================

class TestToolRegistry(unittest.TestCase):
    """Verify that the tool schema registry is correctly assembled."""

    def test_all_tool_schemas_is_list(self):
        self.assertIsInstance(ALL_TOOL_SCHEMAS, list)

    def test_exactly_four_tools(self):
        self.assertEqual(len(ALL_TOOL_SCHEMAS), 4)

    def test_tool_functions_dict_has_four_entries(self):
        self.assertEqual(len(TOOL_FUNCTIONS), 4)

    def test_all_schemas_have_type_function(self):
        for schema in ALL_TOOL_SCHEMAS:
            self.assertEqual(schema["type"], "function")

    def test_all_schemas_have_name(self):
        for schema in ALL_TOOL_SCHEMAS:
            self.assertIn("name", schema["function"])

    def test_schema_names_match_function_keys(self):
        schema_names = {s["function"]["name"] for s in ALL_TOOL_SCHEMAS}
        self.assertEqual(schema_names, set(TOOL_FUNCTIONS.keys()))

    def test_required_tool_names_present(self):
        names = {s["function"]["name"] for s in ALL_TOOL_SCHEMAS}
        for expected in ["calculate", "web_search", "analyze_data", "format_report"]:
            self.assertIn(expected, names)

    def test_all_schemas_have_parameters(self):
        for schema in ALL_TOOL_SCHEMAS:
            self.assertIn("parameters", schema["function"])

    def test_all_functions_are_callable(self):
        for name, fn in TOOL_FUNCTIONS.items():
            self.assertTrue(callable(fn), f"{name} is not callable")


# ===========================================================================
# INTEGRATION TESTS — BusinessAssistant (requires GROQ_API_KEY)
# ===========================================================================

def _get_api_key() -> str:
    """Load the Groq API key from environment or .env file."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    return os.environ.get("GROQ_API_KEY", "")


API_KEY = _get_api_key()
SKIP_INTEGRATION = not API_KEY
SKIP_REASON      = "GROQ_API_KEY not set — skipping integration tests"


@unittest.skipIf(SKIP_INTEGRATION, SKIP_REASON)
class TestEmailWriter(unittest.TestCase):
    """Integration tests for Feature 1: Smart Email Writer."""

    @classmethod
    def setUpClass(cls):
        from business_assistant import BusinessAssistant
        cls.assistant = BusinessAssistant(api_key=API_KEY)

    def test_returns_string(self):
        result = self.assistant.write_email("Announce a new product launch")
        self.assertIsInstance(result, str)

    def test_contains_subject_line(self):
        result = self.assistant.write_email("Invite team to end-of-year party")
        self.assertIn("Subject:", result)

    def test_formal_tone_no_error(self):
        result = self.assistant.write_email(
            purpose="Request budget approval for Q3",
            recipient="stakeholder",
            tone="formal"
        )
        self.assertFalse(result.startswith("Error:"), msg=result)

    def test_friendly_tone_no_error(self):
        result = self.assistant.write_email(
            purpose="Thank the team for hitting quarterly targets",
            recipient="team",
            tone="friendly"
        )
        self.assertFalse(result.startswith("Error:"), msg=result)

    def test_with_research_topic(self):
        result = self.assistant.write_email(
            purpose="Introduce AI services to potential clients",
            recipient="client",
            tone="professional",
            research_topic="AI adoption in business 2026"
        )
        self.assertIsInstance(result, str)
        self.assertFalse(result.startswith("Error:"), msg=result)

    def test_empty_purpose_returns_error(self):
        result = self.assistant.write_email("")
        self.assertTrue(result.startswith("Error:"))

    def test_invalid_recipient_defaults_gracefully(self):
        result = self.assistant.write_email(
            purpose="Send a project update",
            recipient="unknown_type"
        )
        self.assertFalse(result.startswith("Error:"), msg=result)

    def test_invalid_tone_defaults_gracefully(self):
        result = self.assistant.write_email(
            purpose="Send a project update",
            tone="aggressive"
        )
        self.assertFalse(result.startswith("Error:"), msg=result)


@unittest.skipIf(SKIP_INTEGRATION, SKIP_REASON)
class TestReportGenerator(unittest.TestCase):
    """Integration tests for Feature 2: Report Generator."""

    @classmethod
    def setUpClass(cls):
        from business_assistant import BusinessAssistant
        cls.assistant = BusinessAssistant(api_key=API_KEY)
        cls.sales_data = {"Jan": 50000, "Feb": 65000, "Mar": 80000}

    def test_returns_string(self):
        result = self.assistant.generate_report("sales", self.sales_data, "Q1 2026")
        self.assertIsInstance(result, str)

    def test_contains_executive_summary(self):
        result = self.assistant.generate_report("sales", self.sales_data, "Q1 2026")
        self.assertIn("EXECUTIVE SUMMARY", result.upper())

    def test_contains_recommendations(self):
        result = self.assistant.generate_report("quarterly", self.sales_data, "Q1 2026")
        self.assertIn("RECOMMENDATION", result.upper())

    def test_list_data_accepted(self):
        result = self.assistant.generate_report("revenue", [50000, 65000, 80000], "Q1 2026")
        self.assertFalse(result.startswith("Error:"), msg=result)

    def test_empty_data_returns_error(self):
        result = self.assistant.generate_report("sales", {}, "Q1 2026")
        self.assertTrue(result.startswith("Error:"))

    def test_empty_period_returns_error(self):
        result = self.assistant.generate_report("sales", self.sales_data, "")
        self.assertTrue(result.startswith("Error:"))

    def test_invalid_type_defaults_gracefully(self):
        result = self.assistant.generate_report("unknown", self.sales_data, "Q1 2026")
        self.assertFalse(result.startswith("Error:"), msg=result)


@unittest.skipIf(SKIP_INTEGRATION, SKIP_REASON)
class TestMeetingSummarizer(unittest.TestCase):
    """Integration tests for Feature 3: Meeting Summarizer."""

    @classmethod
    def setUpClass(cls):
        from business_assistant import BusinessAssistant
        cls.assistant = BusinessAssistant(api_key=API_KEY)
        cls.sample_notes = (
            "Discussed Q3 marketing strategy. Budget approved at PKR 500k. "
            "Sara to lead the LinkedIn campaign. Ahmed to prepare ad creatives by May 30. "
            "Decision to stop Google Display Ads and focus on email and LinkedIn. "
            "Next meeting June 5th at 10am."
        )

    def test_returns_string(self):
        result = self.assistant.summarize_meeting(self.sample_notes)
        self.assertIsInstance(result, str)

    def test_contains_summary_header(self):
        result = self.assistant.summarize_meeting(self.sample_notes, date="May 20, 2026")
        self.assertIn("SUMMARY", result.upper())

    def test_contains_action_items(self):
        result = self.assistant.summarize_meeting(self.sample_notes)
        self.assertIn("ACTION", result.upper())

    def test_attendees_included_in_output(self):
        result = self.assistant.summarize_meeting(
            self.sample_notes,
            date="May 20, 2026",
            attendees=["Sara", "Ahmed", "Finance Team"]
        )
        # At minimum the output should not error
        self.assertFalse(result.startswith("Error:"), msg=result)

    def test_default_date_used_when_not_provided(self):
        result = self.assistant.summarize_meeting(self.sample_notes)
        self.assertFalse(result.startswith("Error:"), msg=result)

    def test_empty_notes_returns_error(self):
        result = self.assistant.summarize_meeting("")
        self.assertTrue(result.startswith("Error:"))

    def test_too_short_notes_returns_error(self):
        result = self.assistant.summarize_meeting("Short notes.")
        self.assertTrue(result.startswith("Error:"))


@unittest.skipIf(SKIP_INTEGRATION, SKIP_REASON)
class TestDataAnalyzer(unittest.TestCase):
    """Integration tests for Feature 4: Business Data Analyzer."""

    @classmethod
    def setUpClass(cls):
        from business_assistant import BusinessAssistant
        cls.assistant = BusinessAssistant(api_key=API_KEY)
        cls.revenue = {"Jan": 50000, "Feb": 55000, "Mar": 62000,
                       "Apr": 59000, "May": 68000, "Jun": 75000}

    def test_returns_string(self):
        result = self.assistant.analyze_business_data(
            "What is the total revenue?", self.revenue
        )
        self.assertIsInstance(result, str)

    def test_contains_analysis_results_header(self):
        result = self.assistant.analyze_business_data(
            "What is the average monthly revenue?", self.revenue
        )
        self.assertIn("ANALYSIS", result.upper())

    def test_contains_recommendation(self):
        result = self.assistant.analyze_business_data(
            "Analyze revenue trend and give recommendations.", self.revenue
        )
        self.assertIn("RECOMMENDATION", result.upper())

    def test_list_data_accepted(self):
        result = self.assistant.analyze_business_data(
            "What is the average and max?", [10, 20, 30, 40, 50]
        )
        self.assertFalse(result.startswith("Error:"), msg=result)

    def test_empty_query_returns_error(self):
        result = self.assistant.analyze_business_data("", self.revenue)
        self.assertTrue(result.startswith("Error:"))

    def test_empty_data_returns_error(self):
        result = self.assistant.analyze_business_data("Analyze this data", {})
        self.assertTrue(result.startswith("Error:"))


@unittest.skipIf(SKIP_INTEGRATION, SKIP_REASON)
class TestClientCommunication(unittest.TestCase):
    """Integration tests for Feature 5: Client Communication Drafter."""

    @classmethod
    def setUpClass(cls):
        from business_assistant import BusinessAssistant
        cls.assistant = BusinessAssistant(api_key=API_KEY)

    def test_proposal_returns_string(self):
        result = self.assistant.draft_client_communication(
            comm_type="proposal",
            client="NexaTech Solutions",
            context="ERP implementation, 4-month timeline, PKR 2.5 million budget",
            tone="professional"
        )
        self.assertIsInstance(result, str)

    def test_proposal_no_error(self):
        result = self.assistant.draft_client_communication(
            comm_type="proposal",
            client="ABC Corp",
            context="Website redesign, 3 months, $50,000",
        )
        self.assertFalse(result.startswith("Error:"), msg=result)

    def test_status_update_no_error(self):
        result = self.assistant.draft_client_communication(
            comm_type="status_update",
            client="Al-Noor Enterprises",
            context="Website project 60% complete, on schedule, logo files needed in high resolution",
        )
        self.assertFalse(result.startswith("Error:"), msg=result)

    def test_follow_up_no_error(self):
        result = self.assistant.draft_client_communication(
            comm_type="follow_up",
            client="Global Traders",
            context="Following up on the proposal sent two weeks ago regarding the logistics software",
        )
        self.assertFalse(result.startswith("Error:"), msg=result)

    def test_response_no_error(self):
        result = self.assistant.draft_client_communication(
            comm_type="response",
            client="Sunrise Retail",
            context="Client asked about integration with their existing POS system",
        )
        self.assertFalse(result.startswith("Error:"), msg=result)

    def test_empty_client_returns_error(self):
        result = self.assistant.draft_client_communication(
            comm_type="proposal",
            client="",
            context="Some context here"
        )
        self.assertTrue(result.startswith("Error:"))

    def test_empty_context_returns_error(self):
        result = self.assistant.draft_client_communication(
            comm_type="proposal",
            client="Test Client",
            context=""
        )
        self.assertTrue(result.startswith("Error:"))

    def test_invalid_comm_type_defaults_gracefully(self):
        result = self.assistant.draft_client_communication(
            comm_type="unknown_type",
            client="Test Client",
            context="Some details about the project"
        )
        self.assertFalse(result.startswith("Error:"), msg=result)

    def test_friendly_tone_accepted(self):
        result = self.assistant.draft_client_communication(
            comm_type="follow_up",
            client="StartupXYZ",
            context="Following up on the demo we gave last week",
            tone="friendly"
        )
        self.assertFalse(result.startswith("Error:"), msg=result)


# ===========================================================================
# Entry point
# ===========================================================================

if __name__ == "__main__":
    # When run directly, print a clear summary of what will be skipped
    if SKIP_INTEGRATION:
        print("NOTE: Integration tests will be skipped (GROQ_API_KEY not set).")
        print("      Only unit tests will run.\n")

    unittest.main(verbosity=2)
