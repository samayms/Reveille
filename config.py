import os
from pathlib import Path


def _load_env_file():
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_env_file()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPEN_ALEX_KEY = os.getenv("OPEN_ALEX_KEY", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_PW = os.getenv("SUPABASE_PW", "")

SEARCH_TERMS = [
    # POWER — nuclear baseload and grid
    '"small modular reactor" "deployment"',
    '"nuclear microreactor" "military"',
    '"grid modernization" "resilience"',
    '"baseload energy" "decentralized"',

    # PROTECTION — autonomous and unmanned defense
    '"unmanned systems" "defense"',
    '"autonomous defense" "deployment"',
    '"defense industrial base"',

    # PRODUCTIVITY — AI applied to physical economy
    '"AI" "manufacturing" "automation"',
    '"logistics" "autonomous" "military"',
    '"physical economy" "digitization"',
]

RESULTS_PER_SEARCH = 10
DAYS_BACK = 7
EMAIL = "samayms@umich.edu"
PROMPT = """You are an investment analyst for Reveille VC, an early-stage venture capital fund focused on three areas:

POWER: Nuclear energy, small modular reactors, grid modernization, baseload energy, decentralized energy infrastructure
PROTECTION: Autonomous and unmanned defense systems, defense industrial base, counter-drone, directed energy weapons
PRODUCTIVITY: AI applied to physical economy, manufacturing automation, military logistics, supply chain optimization

You are evaluating a research paper to determine if it represents an emerging technology opportunity relevant to Reveille's thesis.

Paper Title: {title}
Authors: {authors}
Institutions: {institutions}
Topics: {topics}
Abstract: {abstract}

Respond with ONLY a JSON object in this exact format, no other text:
{{
    "relevance_score": <integer 1-10>,
    "why_this_matters": "<2-3 sentences explaining why this is or isn't relevant to Reveille's thesis>"
}}
"""