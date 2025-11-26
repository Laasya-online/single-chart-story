# Single-Chart Story (Containerized)

[![Build artifacts](https://github.com/laasya-online/single-chart-story/actions/workflows/build-artifacts.yml/badge.svg)](https://github.com/<your-username>/single-chart-story/actions/workflows/build-artifacts.yml)

Generate a professional **city premium vs US average** chart for a chosen tech role from a synthetic 2024 salary sample, **in one command** via Docker.

## Consumer Example (use the released CSV)

Use the prebuilt table directly in Python:

```python
import pandas as pd

url = "https://raw.githubusercontent.com/laasya-online/single-chart-story/main/assets/city_premium_summary.csv"
# If you didn't commit it to /assets, download from the Release page instead.
df = pd.read_csv(url)  # or manually download the CSV from Releases
print(df.head())

```

## TL | DR
```bash
docker build -t single-chart:0.1.0 .
mkdir -p out
docker run --rm -v "$PWD/out:/out" single-chart:0.1.0 --role "Software Engineer"
# Outputs: out/city_premium_dumbbell.(png|svg) + out/city_premium_summary.csv



