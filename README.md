# Single-Chart Story (Containerized)

Generate a professional **city premium vs US average** chart for a chosen tech role from a synthetic 2024 salary sample—**in one command** via Docker.

## TL;DR
```bash
docker build -t single-chart:0.1.0 .
mkdir -p out
docker run --rm -v "$PWD/out:/out" single-chart:0.1.0 --role "Software Engineer"
# Outputs: out/city_premium_dumbbell.(png|svg) + out/city_premium_summary.csv
