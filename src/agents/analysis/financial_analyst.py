from typing import Optional, Dict, Any
from ..base import AgentResult, run_agent, parse_json_from_output
from ...config.agent_configs import FINANCIAL_ANALYST

async def run_financial_analyst(startup_name: str, startup_description: str, company_profile: Optional[Dict[str, Any]] = None, market_analysis: Optional[Dict[str, Any]] = None) -> AgentResult:
    """Run the financial analyst agent to evaluate the startup's financial health and projections."""
    context_parts = []

    if startup_name:
        context_parts.append(f"Startup Name: {startup_name}")
    if startup_description:
        context_parts.append(f"Description: {startup_description}")
    if company_profile:
        context_parts.append(f"\n## Company Profile Data:\n{_format_dict(company_profile)}")
    if market_analysis:
        context_parts.append(f"\n## Market Analysis Data:\n{_format_dict(market_analysis)}")

    context = "\n".join(context_parts)

    prompt = f"""Analyze the financial health and sustainability of this startup:

{context}

Please provide:
1. Total funding raised (sum from funding history)
2. Estimated runway based on funding stage
3. Revenue model assessment
4. Financial health score (1-10)
5. Key financial concerns

Format your response as valid JSON:
{{
    "total_funding": {{"amount": 50000000, "currency": "USD"}},
    "estimated_runway": "18-24 months",
    "revenue_model": "SaaS subscription",
    "financial_health_score": 7,
    "concerns": ["High burn rate", "Need path to profitability"]
}}

Base analysis on available data. Note if data is missing.
"""

    result = await run_agent(
        agent_name=FINANCIAL_ANALYST.name,
        prompt=prompt,
        tools=FINANCIAL_ANALYST.tools,
        model=FINANCIAL_ANALYST.model,
        timeout_seconds=FINANCIAL_ANALYST.timeout_seconds,
        system_prompt=FINANCIAL_ANALYST.system_prompt
    )

    if result.success and result.raw_output:
        parsed = parse_json_from_output(result.raw_output)
        if parsed:
            result.output = parsed

    return result

def _format_dict(d: Dict[str, Any], indent: int = 0) -> str:
    """Format a dictionary for readable output."""
    lines = []
    prefix = "  " * indent
    for key, value in d.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            lines.append(_format_dict(value, indent + 1))
        else:
            lines.append(f"{prefix}{key}: {value}")
    return "\n".join(lines)
