# app.py
# A tiny CLI that generates the "city premium vs US average" chart.
# Runs headless (no GUI) inside Docker and saves outputs to /out.

import argparse, os, numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")  # headless backend
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from pathlib import Path

def synth_data(seed=42):
    rng = np.random.default_rng(seed)
    cities = [
        ("San Francisco","CA", 210_000),
        ("San Jose","CA",      200_000),
        ("Seattle","WA",       185_000),
        ("New York","NY",      190_000),
        ("Boston","MA",        175_000),
        ("Austin","TX",        165_000),
        ("Los Angeles","CA",   170_000),
        ("Chicago","IL",       160_000),
        ("Denver","CO",        158_000),
        ("Atlanta","GA",       155_000),
    ]
    roles = [("Software Engineer",1.00),("GenAI Developer",1.12),("Data Scientist",0.95)]
    rows = []
    for city, state, base in cities:
        for role, mult in roles:
            n = 30
            mean = base * mult
            sd   = mean * 0.10
            sals = rng.normal(mean, sd, size=n).clip(90_000, 500_000)
            for s in sals:
                rows.append({
                    "year": 2024, "role": role, "city": city, "state": state,
                    "salary_usd": round(float(s), 2)
                })
    return pd.DataFrame(rows)

def make_chart(df, role, out_dir):
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    se = df[df["role"] == role].copy()
    if se.empty:
        raise SystemExit(f"No rows for role={role}. Choices: {df['role'].unique().tolist()}")

    national_avg = se["salary_usd"].mean()
    city_stats = (se.groupby("city")["salary_usd"]
                    .agg(["count","mean"])
                    .rename(columns={"mean":"city_avg"})
                    .sort_values("city_avg", ascending=False))
    top5 = city_stats.head(5).reset_index()
    top5["premium"] = top5["city_avg"] - national_avg

    # Save summary CSV
    top5[["city","count","city_avg"]].assign(
        national_avg=national_avg,
        premium_abs=top5["premium"],
        premium_pct=100*top5["premium"]/national_avg
    ).to_csv(out / "city_premium_summary.csv", index=False)

    # Lollipop / dumbbell-style chart
    ordered = top5.sort_values("premium").reset_index(drop=True)
    y = np.arange(len(ordered))
    city_avg = ordered["city_avg"].values
    nat = np.full_like(city_avg, national_avg, dtype=float)
    diff = city_avg - nat

    fig, ax = plt.subplots(figsize=(10,5))
    for i in range(len(y)):
        ax.plot([nat[i], city_avg[i]], [y[i], y[i]], linewidth=3)
    ax.scatter(nat, y, s=60)
    ax.scatter(city_avg, y, s=80)
    for i, d in enumerate(diff):
        ax.text(city_avg[i] + (0.0075 * national_avg), y[i],
                f"+${int(round(d/1000))*1000:,}", va="center")

    ax.set_yticks(y); ax.set_yticklabels(ordered["city"].tolist())
    ax.invert_yaxis()
    ax.set_xlabel("Average Compensation (USD)")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${int(v):,}"))

    biggest_city = ordered.iloc[-1]["city"]
    biggest_gap  = int(round(ordered.iloc[-1]["premium"]/1000))*1000
    title = f"City Premium vs National Average — {role}"
    subtitle = f"Largest premium: {biggest_city} at +${biggest_gap:,} vs US average"

    plt.title(title + "\n" + subtitle, loc="left")
    plt.tight_layout()

    figpath_png = out / "city_premium_dumbbell.png"
    figpath_svg = out / "city_premium_dumbbell.svg"
    plt.savefig(figpath_png, dpi=220, bbox_inches="tight")
    plt.savefig(figpath_svg,            bbox_inches="tight")
    print(f"Wrote: {figpath_png}\nWrote: {figpath_svg}")

def main():
    ap = argparse.ArgumentParser(description="Generate Single-Chart Story artifacts.")
    ap.add_argument("--role", default="Software Engineer", help="Role to analyze")
    ap.add_argument("--out",  default="/out", help="Output directory (mounted volume)")
    args = ap.parse_args()

    df = synth_data()
    make_chart(df, args.role, args.out)

if __name__ == "__main__":
    main()
