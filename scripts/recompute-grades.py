import json

DATA_PATH = "src/data/quality-scores.json"

WEIGHTS = {
    "safety": 0.25,
    "healthcare": 0.20,
    "happiness": 0.15,
    "hdi": 0.15,
    "pollution": 0.08,
    "unemployment": 0.07,
    "internet": 0.05,
    "traffic": 0.05,
}


def calculate_grade(metrics):
    """Absolute weighted score, 0-100%, with
    8 descriptive tiers instead of A-F letters"""
    total_score = 0
    total_weight = 0
    for metric, weight in WEIGHTS.items():
        score = metrics.get(metric)
        if score is not None:
            total_score += score * weight
            total_weight += weight

    if total_weight == 0:
        return None, None

    weighted_average = total_score / total_weight
    percent = round(weighted_average * 10)

    if percent >= 90:
        label = "Outstanding destination"
    elif percent >= 80:
        label = "Excellent destination"
    elif percent >= 70:
        label = "Very good destination"
    elif percent >= 60:
        label = "Good destination"
    elif percent >= 50:
        label = "Moderate destination"
    elif percent >= 40:
        label = "Mixed destination"
    elif percent >= 30:
        label = "Limited destination"
    else:
        label = "Challenging destination"

    return percent, label


def main():
    with open(DATA_PATH, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    countries = data.get('countries', {})
    updated = 0

    print("--- Recomputing grades "
          "(absolute weighted score) ---\n")

    results = []
    for slug, metrics in countries.items():
        percent, label = calculate_grade(metrics)
        if percent is not None:
            old_grade = metrics.get('grade')
            old_percent = metrics.get('grade_percent')
            metrics['grade_percent'] = percent
            metrics['grade_label'] = label
            # Keep old 'grade' field for backward
            # compatibility but mark it deprecated
            # by removing it - the new system uses
            # grade_percent + grade_label only
            if 'grade' in metrics:
                del metrics['grade']
            updated += 1
            results.append(
                (slug, old_grade, old_percent,
                 percent, label)
            )

    # Sort by new percent descending for a
    # readable summary
    results.sort(key=lambda x: x[3], reverse=True)
    for slug, old_g, old_p, new_p, label in results:
        print(f"  {slug}: old={old_g}/{old_p}% "
              f"-> new={new_p}% ({label})")

    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nUpdated {updated}/{len(countries)} "
          f"countries in {DATA_PATH}")


if __name__ == "__main__":
    main()
