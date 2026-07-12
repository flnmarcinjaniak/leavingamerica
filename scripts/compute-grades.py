import json
from collections import Counter

DATA_PATH = "src/data/quality-scores.json"

WEIGHTS = {
    'safety':       0.25,
    'healthcare':   0.20,
    'happiness':    0.15,
    'pollution':    0.10,
    'unemployment': 0.10,
    'internet':     0.10,
    'gdpGrowth':    0.05,
    'traffic':      0.05,
}

def compute_raw_score(data):
    total, weight_sum = 0.0, 0.0
    for metric, weight in WEIGHTS.items():
        val = data.get(metric)
        if val is not None:
            total += val * weight
            weight_sum += weight
    return (total / weight_sum) if weight_sum > 0 else 0.0

with open(DATA_PATH, 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

countries = data['countries']

scored = sorted(
    [(slug, compute_raw_score(cdata)) for slug, cdata in countries.items()],
    key=lambda x: x[1],
    reverse=True
)
total = len(scored)

# Percentile cutoffs (higher percentile = better rank)
# A: top 15%  (pct >= 85)
# B: next 25%  (pct >= 60)
# C: next 30%  (pct >= 30)
# D: next 15%  (pct >= 10)
# F: bottom 10% (pct < 10)

def grade_from_pct(pct):
    if pct >= 85: return 'A'
    if pct >= 60: return 'B'
    if pct >= 30: return 'C'
    if pct >= 10: return 'D'
    return 'F'

VERDICTS = {
    'A': 'Excellent destination',
    'B': 'Good destination',
    'C': 'Average destination',
    'D': 'Below average',
    'F': 'Poor destination',
}

print(f"Grading {total} countries (percentile-based)\n")
print(f"{'#':<4} {'Grade':<5} {'Pct':>5}  {'Score':>6}   Slug")
print("-" * 55)

for rank, (slug, score) in enumerate(scored, 1):
    # percentile: rank 1 (best) → 100, rank N (worst) → 0
    pct = round((total - rank) / max(total - 1, 1) * 100)
    grade = grade_from_pct(pct)
    countries[slug]['grade'] = grade
    countries[slug]['grade_percent'] = pct
    print(f"  {rank:<3} {grade:<5} {pct:>4}%   {score*10:>5.1f}   {slug}")

with open(DATA_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

grade_counts = Counter(countries[s]['grade'] for s in countries)
print(f"\nGrade distribution:")
for g in ['A', 'B', 'C', 'D', 'F']:
    print(f"  {g}: {grade_counts.get(g, 0)} countries")

print(f"\nSaved grade + grade_percent to {DATA_PATH}")
