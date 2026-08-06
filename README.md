# Beyond Points Per Game: NBA Player Role Analytics

An interactive NBA analytics application for exploring how players contribute through scoring, creation, rebounding, shooting efficiency, defensive events, and overall role breadth.

Rather than producing another single “best player” ranking, the project compares player-season statistical profiles and roster composition while using team winning only as descriptive context.

## Project Overview

The application analyzes NBA player and team data from the 2010 through 2025 seasons.

- 7,298 raw player records reviewed
- 5,665 eligible player-team-season records
- 480 team-season records
- 16 NBA seasons
- Custom interactive visualizations built with D3.js
- Reproducible Python data-preparation pipeline
- Static deployment through GitHub Pages

A player-season is included when the player:

- Appeared in at least 20 games
- Averaged at least 10 minutes per game

## Questions Explored

The project examines questions such as:

- How do broad player-role profiles differ across team-success levels?
- Where do efficient, lower-shot contributors appear?
- How often are defensive-event leaders also top scorers?
- Which historical player-seasons have similar statistical profiles?
- How do roster role distributions differ across teams and seasons?

These analyses describe statistical associations. They do not claim that a specific player profile causes team success.

## Interactive Features

### Role Explorer

The Role Explorer allows users to:

- Compare two player-team-seasons
- Review scoring, creation, rebounding, efficiency, defensive-event, and turnover metrics
- View role fingerprints and percentile-based profiles
- Find statistically similar historical player-seasons
- Explore relationships between player profiles and team win percentage
- Switch among role breadth, shooting efficiency, and defensive-event analyses

### Team Roster Lab

The Team Roster Lab allows users to:

- Select any team and season from 2010–2025
- Explore player-role coverage across a roster
- Focus on the ten highest-minute players as a rotation proxy
- Compare two team rosters
- Examine role balance, strengths, and potential coverage gaps
- Export or share the selected roster view

### Methodology Page

The application includes a dedicated methodology page explaining:

- Data scope and eligibility rules
- Player-role calculations
- Team-success categories
- Percentile interpretation
- Similarity methodology
- Limitations and responsible interpretation

## Core Metrics

| Metric | Interpretation |
|---|---|
| `points_per_36` | Scoring rate normalized to 36 minutes |
| `assists_per_36` | Playmaking and creation rate |
| `rebounds_per_36` | Rebounding rate |
| `stocks_per_36` | Steals plus blocks per 36 minutes |
| `efg_pct` | Effective field-goal percentage |
| `fga_per_game` | Shot volume |
| `turnovers_per_36` | Turnovers normalized to 36 minutes |
| `role_category_count` | Number of role dimensions at or above the eligible-sample median |
| `win_pct` | Team regular-season win percentage |

Role breadth compares six dimensions:

1. Points per 36 minutes
2. Assists per 36 minutes
3. Rebounds per 36 minutes
4. Steals per 36 minutes
5. Blocks per 36 minutes
6. Effective field-goal percentage

Player-seasons are grouped as:

- **Narrow profile:** 0–1 dimensions
- **Mixed profile:** 2–3 dimensions
- **Balanced profile:** 4–6 dimensions

These labels describe statistical breadth and are not player-quality rankings.

## Data Pipeline

`prepare_data.py` rebuilds the complete analysis layer from the raw source files.

The pipeline:

1. Loads player statistics, salary data, and game results
2. Standardizes team and season identifiers
3. Filters eligible player-team-season records
4. Calculates per-36 and efficiency metrics
5. Derives role breadth and descriptive profile labels
6. Reconstructs team-season records and win percentages
7. Assigns team-success tertiles
8. Validates row counts, duplicate keys, missing joins, and season coverage
9. Generates the CSV and JSON files consumed by the website

Generated application files:

```text
static/data/player_seasons.csv
static/data/nba_app_data.json