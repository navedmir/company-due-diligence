
from ..base import AgentResult, run_agent, parse_json_from_output
from ...config.agent_configs import COMPANY_PROFILER

async def run_company_profiler(startup_name: str, startup_description: str) -> AgentResult:
    """Run the company profiler agent to gather information about the startup."""
    prompt = f"""Research the following startup and complile a company profile:

Startup Name: {startup_name}
Description: {startup_description}

Please find and report:
1. Official website URL
2. Founded (year)
3. Headquarters location
4. Approximate employee count
5. Funding history (list each round with amount and lead investor if known)
6. Total funding raised
7. Main products/services (list up to 5)
8. Mission statement or tagline

Format your response as valid JSON:
{{
    "name": "{startup_name}",
    "founded": "year or null",
    "location": "city, country or null",
    "employee_count": number or null,
    "funding_history": [
        {{"round_name": "Series A", "amount": {{"amount": 10000000, "currency": "USD"}}, "investors": ["Investor1"]}}
    ],
    "total_funding": {{"amount": number, "currency": "USD"}},
    "products": ["product1", "product2"],
    "mission": "mission statement or null",
    "website": "url or null"
}}
"""

    result = await run_agent(
        agent_name=COMPANY_PROFILER.name,
        prompt=prompt,
        tools=COMPANY_PROFILER.tools,
        model=COMPANY_PROFILER.model,
        timeout_seconds=COMPANY_PROFILER.timeout_seconds,
        system_prompt=COMPANY_PROFILER.system_prompt
    )

    if result.success and result.raw_output:
        parsed = parse_json_from_output(result.raw_output)
        if parsed:
            result.output = parsed

    return result