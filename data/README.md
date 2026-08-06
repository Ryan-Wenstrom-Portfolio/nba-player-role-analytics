# Data Documentation

This directory contains documentation for the raw and processed data used by the NBA Player Role Analytics application.

Raw and intermediate datasets are excluded from Git because they are large or reproducible. The smaller files required by the public website are committed under `static/data/`.

## Required Raw Files

Place these files inside `data/raw/`:

```text
data/raw/
├── NBA Player Stats and Salaries_2010-2025.csv
└── Games.csv
```

### Player Statistics and Salaries

**Dataset:** NBA Player Stats and Salaries 2010-2025  
**Creator:** Ratin21  
**Platform:** Kaggle  
**Source:** https://www.kaggle.com/datasets/ratin21/nba-player-stats-and-salaries-2010-2025

The file contains player-team-season box-score statistics, positions, and salary information.

The raw file contains 7,298 records. The application retains 5,665 eligible player-team-season records after requiring:

- At least 20 games played
- At least 10 minutes per game

### Historical Game Results

**Dataset:** NBA Database (1947-Present)  
**Creator:** Eoin A Moore  
**Platform:** Kaggle  
**Source:** https://www.kaggle.com/datasets/eoinamoore/historical-nba-data-and-player-box-scores

The project uses `Games.csv` to calculate team-season wins, losses, games played, and win percentage.

Only seasons labeled 2010 through 2025 are retained.

## Season Convention

Seasons are labeled by the calendar year in which they end:

- The 2009-10 season is labeled `2010`
- The 2023-24 season is labeled `2024`
- The 2024-25 season is labeled `2025`

## NBA Cup Treatment

NBA Cup games that count toward regular-season standings are included.

The separate championship game is excluded because it does not count toward regular-season records. The pipeline checks tournament labels as well as the general game-type field because the source data is not fully consistent across seasons.

## 2024-25 Record Correction

The downloaded `Games.csv` snapshot did not contain a complete 1,230-game 2024-25 regular season.

The audit found:

- One NBA Cup championship game labeled as a regular-season game
- No duplicated game IDs
- No duplicated date-and-matchup rows
- Five missing regular-season games after excluding the championship

The pipeline therefore replaces the reconstructed 2025 team records with the final standings stored in `FINAL_2025_RECORDS` inside `prepare_data.py`.

Validation requires:

- 30 teams
- 82 games per team
- 1,230 total games

## Generated Files

Run:

```powershell
python prepare_data.py
```

Local validation outputs:

```text
data/processed/player_seasons_rebuilt.csv
data/processed/team_season_records.csv
```

Application-ready outputs:

```text
static/data/player_seasons.csv
static/data/nba_app_data.json
```

## Validation Checks

The pipeline checks:

- Player and team-season row counts
- Duplicate player-team-season keys
- Duplicate team-season keys
- Season coverage from 2010 through 2025
- Missing team-record joins
- Team-name mappings
- Complete corrected 2025 standings
- Player eligibility rules
- Role-profile calculations

## Responsible Use

The data supports descriptive analysis. It should not be used to claim that:

- A statistical profile caused a team to win
- Steals and blocks represent complete defensive performance
- Role breadth is a definitive player-quality ranking
- Team win percentage measures individual player performance
- Salaries are directly comparable across seasons without additional adjustment