"""
tools.py
--------
All tool functions for the Business Email and Report Manager.

Tools:
    1. calculate       - Safe evaluation of financial math expressions
    2. web_search      - Mock web search for business research
    3. analyze_data    - Statistical analysis of business datasets
    4. format_report   - Returns structured report templates and metadata

Each function returns a JSON string so it can be passed directly back to
the Groq tool-calling API as a tool result.
"""

import json
import math
import statistics
from datetime import datetime


# ==============================================================
# TOOL 1: Calculator
# ==============================================================

def calculate(expression: str) -> str:
    """
    Safely evaluate a mathematical or financial expression.

    Supports: +, -, *, /, **, sqrt, log, log10, sin, cos, abs, round, pi, e
    Examples:
        '50000 * 0.15'
        '(75000 - 50000) / 50000 * 100'
        'sqrt(144)'
        '100000 * (1 + 0.12) ** 3'

    Args:
        expression: A Python-compatible math expression as a string.

    Returns:
        JSON string with keys: expression, result, status
        On error: JSON string with keys: error, status
    """
    if not expression or not expression.strip():
        return json.dumps({"error": "Expression cannot be empty.", "status": "error"})

    safe_context = {
        "__builtins__": {},
        "sqrt":  math.sqrt,
        "log":   math.log,
        "log10": math.log10,
        "sin":   math.sin,
        "cos":   math.cos,
        "tan":   math.tan,
        "abs":   abs,
        "round": round,
        "pi":    math.pi,
        "e":     math.e,
    }

    try:
        result = eval(expression, safe_context)
        return json.dumps({
            "expression": expression,
            "result":     round(float(result), 4),
            "status":     "success"
        })
    except ZeroDivisionError:
        return json.dumps({"error": "Division by zero.", "status": "error"})
    except (SyntaxError, NameError) as exc:
        return json.dumps({"error": f"Invalid expression: {str(exc)}", "status": "error"})
    except Exception as exc:
        return json.dumps({"error": f"Calculation failed: {str(exc)}", "status": "error"})


# ==============================================================
# TOOL 2: Web Search (Mock)
# ==============================================================

def web_search(query: str) -> str:
    """
    Mock web search returning realistic business and market data.

    Covers: market trends, industry news, email best practices,
            competitors, sales strategy, finance, marketing.

    Replace the mock_data dict with a real API call (SerpAPI, Tavily,
    or Brave Search) for production use.

    Args:
        query: Natural language search query string.

    Returns:
        JSON string with keys: query, result_count, results, status
        results is a list of dicts with keys: title, snippet
    """
    if not query or not query.strip():
        return json.dumps({"error": "Search query cannot be empty.", "status": "error"})

    q = query.lower()

    mock_data = {
        "market trend": [
            {
                "title":   "Global Tech Market Q1 2026",
                "snippet": "The technology sector recorded 15% YoY growth in Q1 2026, "
                           "driven by AI adoption and cloud migration. SaaS revenue grew by 22% globally."
            },
            {
                "title":   "Emerging Market Opportunities",
                "snippet": "Southeast Asia and South Asia are seeing the fastest B2B software "
                           "adoption rates, with Pakistan's IT exports surpassing $3 billion in FY2025."
            },
        ],
        "industry news": [
            {
                "title":   "AI Adoption in Business 2026",
                "snippet": "Over 67% of mid-size enterprises have integrated AI tools into daily "
                           "operations as of early 2026, up from 34% in 2024."
            },
            {
                "title":   "Digital Transformation Report",
                "snippet": "Companies investing in digital transformation report 30% higher customer "
                           "retention and 20% lower operational costs on average."
            },
        ],
        "email best practice": [
            {
                "title":   "Professional Email Guide 2026",
                "snippet": "High-performing business emails have clear subject lines under 50 characters, "
                           "a single call-to-action, and are sent on Tuesday-Thursday mornings."
            },
            {
                "title":   "B2B Email Benchmarks",
                "snippet": "Average B2B email open rate is 22.5%. Personalized subject lines increase "
                           "open rates by 26%. Follow-up emails generate 16% more responses."
            },
        ],
        "competitor": [
            {
                "title":   "Competitive Landscape Analysis",
                "snippet": "Major competitors are expanding into adjacent markets. Three top players "
                           "have raised Series B/C funding in Q1 2026, signaling aggressive growth."
            },
            {
                "title":   "Market Share Report",
                "snippet": "The top 5 players control 58% of the addressable market. Smaller entrants "
                           "are competing on pricing and niche specialization."
            },
        ],
        "sales strategy": [
            {
                "title":   "Sales Effectiveness Report 2026",
                "snippet": "Consultative selling outperforms transactional approaches by 43%. "
                           "Account-based sales strategies see 28% higher deal values."
            },
            {
                "title":   "Revenue Growth Tactics",
                "snippet": "Top-performing sales teams invest heavily in post-sale customer success, "
                           "achieving 35% revenue from upsells and renewals."
            },
        ],
        "finance": [
            {
                "title":   "Business Finance Trends Q1 2026",
                "snippet": "SME lending rates stabilized at 8-11%. Invoice financing and "
                           "revenue-based financing are gaining popularity among startups."
            },
            {
                "title":   "Cash Flow Management Best Practices",
                "snippet": "Businesses maintaining 3-month operating reserves report 40% lower "
                           "risk of operational disruptions during market downturns."
            },
        ],
        "marketing": [
            {
                "title":   "Digital Marketing ROI 2026",
                "snippet": "Content marketing delivers 3x more leads than outbound at 62% lower "
                           "cost. Video content has 4x higher engagement than static posts."
            },
            {
                "title":   "B2B Marketing Channels",
                "snippet": "LinkedIn remains the top B2B channel with 80% of leads. Email marketing "
                           "ROI averages $36 for every $1 spent in 2025-2026."
            },
        ],
    }

    results = []
    for keyword, data in mock_data.items():
        if keyword in q:
            results = data
            break

    if not results:
        results = [
            {
                "title":   f"Business Research: {query.title()}",
                "snippet": f"Recent analysis on '{query}' indicates growing market activity. "
                           "Industry experts recommend staying updated with quarterly reports "
                           "and aligning strategy to current demand signals."
            },
            {
                "title":   f"{query.title()} — Industry Insights 2026",
                "snippet": f"Organizations focused on '{query}' are seeing increased ROI by "
                           "adopting data-driven approaches and automation. Cross-functional "
                           "alignment is cited as a key success factor."
            },
        ]

    return json.dumps({
        "query":        query,
        "result_count": len(results),
        "results":      results,
        "status":       "success"
    })


# ==============================================================
# TOOL 3: Data Analyzer
# ==============================================================

def analyze_data(data_string: str, operation: str = "all") -> str:
    """
    Analyze a business dataset provided as a JSON string.

    Accepted formats:
        List:   '[50000, 65000, 70000]'
        Dict:   '{"Jan": 50000, "Feb": 65000, "Mar": 70000}'

    Operations: sum, average, max, min, median, std, count, all
        'all' returns every metric plus trend and growth rate.

    Args:
        data_string: JSON-encoded list or dict of numeric values.
        operation:   Statistic to compute. Default is 'all'.

    Returns:
        JSON string with keys: result, status
        On error: JSON string with keys: error, status
    """
    if not data_string or not data_string.strip():
        return json.dumps({"error": "data_string cannot be empty.", "status": "error"})

    try:
        raw = json.loads(data_string)
    except json.JSONDecodeError as exc:
        return json.dumps({"error": f"Invalid JSON in data_string: {str(exc)}", "status": "error"})

    # Support list and dict formats
    if isinstance(raw, list):
        try:
            values = [float(x) for x in raw]
        except (ValueError, TypeError) as exc:
            return json.dumps({"error": f"Non-numeric value in list: {str(exc)}", "status": "error"})
        labels = [str(i + 1) for i in range(len(values))]
    elif isinstance(raw, dict):
        labels = list(raw.keys())
        try:
            values = [float(v) for v in raw.values()]
        except (ValueError, TypeError) as exc:
            return json.dumps({"error": f"Non-numeric value in dict: {str(exc)}", "status": "error"})
    else:
        return json.dumps({"error": "data_string must be a JSON list or object.", "status": "error"})

    if not values:
        return json.dumps({"error": "Dataset is empty.", "status": "error"})

    op = operation.lower().strip()

    try:
        if op == "all":
            max_val   = max(values)
            min_val   = min(values)
            max_label = labels[values.index(max_val)]
            min_label = labels[values.index(min_val)]

            # Trend: compare first half average to second half average
            mid = len(values) // 2
            if mid > 0:
                first_avg  = sum(values[:mid]) / mid
                second_avg = sum(values[mid:]) / (len(values) - mid)
                if second_avg > first_avg * 1.02:
                    trend = "Increasing"
                elif second_avg < first_avg * 0.98:
                    trend = "Decreasing"
                else:
                    trend = "Stable"
            else:
                trend = "Insufficient data for trend analysis"

            # Period-over-period growth (first value to last value)
            growth_rate = None
            if len(values) >= 2 and values[0] != 0:
                growth_rate = round((values[-1] - values[0]) / values[0] * 100, 2)

            result = {
                "count":               len(values),
                "labels":              labels,
                "sum":                 round(sum(values), 2),
                "average":             round(statistics.mean(values), 2),
                "median":              round(statistics.median(values), 2),
                "max":                 {"value": max_val, "label": max_label},
                "min":                 {"value": min_val, "label": min_label},
                "std_dev":             round(statistics.stdev(values), 2) if len(values) > 1 else 0,
                "trend":               trend,
                "growth_rate_percent": growth_rate,
            }

        elif op in ("sum", "total"):
            result = {"sum": round(sum(values), 2)}

        elif op in ("average", "mean", "avg"):
            result = {"average": round(statistics.mean(values), 2)}

        elif op == "max":
            m = max(values)
            result = {"max": m, "label": labels[values.index(m)]}

        elif op == "min":
            m = min(values)
            result = {"min": m, "label": labels[values.index(m)]}

        elif op == "median":
            result = {"median": round(statistics.median(values), 2)}

        elif op in ("std", "stdev", "std_dev"):
            result = {"std_dev": round(statistics.stdev(values), 2) if len(values) > 1 else 0}

        elif op == "count":
            result = {"count": len(values)}

        else:
            return json.dumps({
                "error":  f"Unknown operation '{operation}'. "
                          "Valid options: sum, average, max, min, median, std, count, all",
                "status": "error"
            })

        return json.dumps({"result": result, "status": "success"})

    except statistics.StatisticsError as exc:
        return json.dumps({"error": f"Statistics error: {str(exc)}", "status": "error"})
    except Exception as exc:
        return json.dumps({"error": f"Analysis failed: {str(exc)}", "status": "error"})


# ==============================================================
# TOOL 4: Report Formatter
# ==============================================================

def format_report(report_type: str, data: str, period: str) -> str:
    """
    Return a structured report template with section headers and KPI labels.

    The LLM calls this tool first when generating a report to get the
    correct structure before writing the content.

    Args:
        report_type: One of 'sales', 'revenue', 'performance', 'quarterly', 'marketing'
        data:        JSON string of the data to be included (passed through for reference)
        period:      Reporting period, e.g. 'Q1 2026', 'January 2026', 'FY2025'

    Returns:
        JSON string with keys: header, sections, kpis, timestamp, period,
                               report_type, data_received, status
    """
    if not period or not period.strip():
        return json.dumps({"error": "Period cannot be empty.", "status": "error"})

    report_type = report_type.lower().strip()

    templates = {
        "sales": {
            "header":   f"{period} Sales Performance Report",
            "sections": ["Executive Summary", "Key Sales Metrics", "Monthly Breakdown",
                         "Performance Analysis", "Recommendations"],
            "kpis":     ["Total Revenue", "Average Monthly Revenue", "Peak Month",
                         "Growth Rate", "Revenue per Period"],
        },
        "revenue": {
            "header":   f"{period} Revenue Report",
            "sections": ["Executive Summary", "Revenue Breakdown", "Cost Analysis",
                         "Profit Margins", "Forecast"],
            "kpis":     ["Gross Revenue", "Net Revenue", "COGS", "Gross Margin", "YoY Growth"],
        },
        "performance": {
            "header":   f"{period} Performance Report",
            "sections": ["Executive Summary", "KPI Dashboard", "Team Performance",
                         "Goal Achievement", "Next Period Targets"],
            "kpis":     ["Target Achievement %", "Average Score", "Top Performer",
                         "Areas for Improvement", "Trend"],
        },
        "quarterly": {
            "header":   f"{period} Quarterly Business Report",
            "sections": ["Executive Overview", "Financial Highlights", "Operational Updates",
                         "Market Position", "Strategic Next Steps"],
            "kpis":     ["Total Revenue", "Operating Expenses", "Net Profit",
                         "Customer Growth", "QoQ Growth Rate"],
        },
        "marketing": {
            "header":   f"{period} Marketing Performance Report",
            "sections": ["Campaign Summary", "Lead Generation", "Conversion Metrics",
                         "Channel Performance", "Budget Analysis"],
            "kpis":     ["Total Leads", "Conversion Rate", "Cost per Lead", "ROI", "Top Channel"],
        },
    }

    template = templates.get(report_type, templates["sales"])

    return json.dumps({
        "header":        template["header"],
        "sections":      template["sections"],
        "kpis":          template["kpis"],
        "timestamp":     datetime.now().strftime("%B %d, %Y"),
        "period":        period,
        "report_type":   report_type,
        "data_received": data,
        "status":        "success"
    })


# ==============================================================
# Tool schemas for Groq function calling
# ==============================================================

calculator_tool = {
    "type": "function",
    "function": {
        "name":        "calculate",
        "description": (
            "Evaluate a mathematical or financial expression. Use for percentages, "
            "growth rates, totals, ratios, and any arithmetic. "
            "Examples: '50000 * 0.15', '(75000 - 50000) / 50000 * 100', 'sqrt(9)'."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type":        "string",
                    "description": "A valid Python math expression."
                }
            },
            "required": ["expression"]
        }
    }
}

web_search_tool = {
    "type": "function",
    "function": {
        "name":        "web_search",
        "description": (
            "Search for business information, market trends, industry news, competitor "
            "analysis, and best practices. Use before writing emails or reports that "
            "require current market context."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type":        "string",
                    "description": "Search query, e.g. 'tech industry market trends 2026'."
                }
            },
            "required": ["query"]
        }
    }
}

data_analyzer_tool = {
    "type": "function",
    "function": {
        "name":        "analyze_data",
        "description": (
            "Analyze business data: sales figures, revenue, KPIs, or any numeric dataset. "
            "Accepts JSON list or JSON object. Returns sum, average, max, min, median, "
            "std deviation, trend, and growth rate."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "data_string": {
                    "type":        "string",
                    "description": (
                        "JSON string of data. "
                        "List: '[50000, 60000, 70000]'. "
                        "Dict: '{\"Jan\": 50000, \"Feb\": 60000}'."
                    )
                },
                "operation": {
                    "type":        "string",
                    "description": "Statistic to compute. Default: 'all'.",
                    "enum":        ["sum", "average", "max", "min", "median", "std", "count", "all"]
                }
            },
            "required": ["data_string"]
        }
    }
}

report_formatter_tool = {
    "type": "function",
    "function": {
        "name":        "format_report",
        "description": (
            "Get a professional report structure and template. Returns section headers, "
            "KPI labels, and metadata. Call this first before generating any business report."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "report_type": {
                    "type":        "string",
                    "description": "Type of report.",
                    "enum":        ["sales", "revenue", "performance", "quarterly", "marketing"]
                },
                "data": {
                    "type":        "string",
                    "description": "JSON string of the data to be included in the report."
                },
                "period": {
                    "type":        "string",
                    "description": "Reporting period, e.g. 'Q1 2026', 'January 2026'."
                }
            },
            "required": ["report_type", "data", "period"]
        }
    }
}

# Convenience collections used by BusinessAssistant
ALL_TOOL_SCHEMAS = [
    calculator_tool,
    web_search_tool,
    data_analyzer_tool,
    report_formatter_tool,
]

TOOL_FUNCTIONS = {
    "calculate":    calculate,
    "web_search":   web_search,
    "analyze_data": analyze_data,
    "format_report": format_report,
}
