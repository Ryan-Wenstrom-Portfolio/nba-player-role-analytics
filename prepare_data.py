import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
STATIC_DATA_DIR = ROOT / "static" / "data"

PLAYER_FILE = RAW_DIR / "NBA Player Stats and Salaries_2010-2025.csv"
GAMES_FILE = RAW_DIR / "Games.csv"

PLAYER_OUTPUT = PROCESSED_DIR / "player_seasons_rebuilt.csv"
TEAM_OUTPUT = PROCESSED_DIR / "team_season_records.csv"
APP_PLAYER_OUTPUT = STATIC_DATA_DIR / "player_seasons.csv"
APP_JSON_OUTPUT = STATIC_DATA_DIR / "nba_app_data.json"

START_YEAR = 2010
END_YEAR = 2025
MIN_GAMES = 20
MIN_MINUTES_PER_GAME = 10

SUCCESS_LABELS = [
    "Low-winning teams",
    "Middle-winning teams",
    "High-winning teams",
]

TEAM_MAP = {
    ("Atlanta", "Hawks"): "ATL",
    ("Boston", "Celtics"): "BOS",
    ("Brooklyn", "Nets"): "BRK",
    ("Charlotte", "Bobcats"): "CHA",
    ("Charlotte", "Hornets"): "CHO",
    ("Chicago", "Bulls"): "CHI",
    ("Cleveland", "Cavaliers"): "CLE",
    ("Dallas", "Mavericks"): "DAL",
    ("Denver", "Nuggets"): "DEN",
    ("Detroit", "Pistons"): "DET",
    ("Golden State", "Warriors"): "GSW",
    ("Houston", "Rockets"): "HOU",
    ("Indiana", "Pacers"): "IND",
    ("LA", "Clippers"): "LAC",
    ("Los Angeles", "Clippers"): "LAC",
    ("Los Angeles", "Lakers"): "LAL",
    ("Memphis", "Grizzlies"): "MEM",
    ("Miami", "Heat"): "MIA",
    ("Milwaukee", "Bucks"): "MIL",
    ("Minnesota", "Timberwolves"): "MIN",
    ("New Jersey", "Nets"): "NJN",
    ("New Orleans", "Hornets"): "NOH",
    ("New Orleans", "Pelicans"): "NOP",
    ("New York", "Knicks"): "NYK",
    ("Oklahoma City", "Thunder"): "OKC",
    ("Orlando", "Magic"): "ORL",
    ("Philadelphia", "76ers"): "PHI",
    ("Phoenix", "Suns"): "PHO",
    ("Portland", "Trail Blazers"): "POR",
    ("Sacramento", "Kings"): "SAC",
    ("San Antonio", "Spurs"): "SAS",
    ("Toronto", "Raptors"): "TOR",
    ("Utah", "Jazz"): "UTA",
    ("Washington", "Wizards"): "WAS",
}

FINAL_2025_RECORDS = {
    "ATL": (40, 42),
    "BOS": (61, 21),
    "BRK": (26, 56),
    "CHO": (19, 63),
    "CHI": (39, 43),
    "CLE": (64, 18),
    "DAL": (39, 43),
    "DEN": (50, 32),
    "DET": (44, 38),
    "GSW": (48, 34),
    "HOU": (52, 30),
    "IND": (50, 32),
    "LAC": (50, 32),
    "LAL": (50, 32),
    "MEM": (48, 34),
    "MIA": (37, 45),
    "MIL": (48, 34),
    "MIN": (49, 33),
    "NOP": (21, 61),
    "NYK": (51, 31),
    "OKC": (68, 14),
    "ORL": (41, 41),
    "PHI": (24, 58),
    "PHO": (36, 46),
    "POR": (36, 46),
    "SAC": (40, 42),
    "SAS": (34, 48),
    "TOR": (30, 52),
    "UTA": (17, 65),
    "WAS": (18, 64),
}

OUTPUT_COLUMNS = [
    "year",
    "player",
    "team",
    "pos",
    "position_group",
    "salary_m",
    "minutes_per_game",
    "points_per_game",
    "points_per_36",
    "fga_per_game",
    "efg_pct",
    "assists_per_36",
    "rebounds_per_36",
    "stocks_per_36",
    "turnovers_per_36",
    "role_category_count",
    "win_pct",
    "team_success_bucket",
    "profile_group",
    "efficient_lower_shot_label",
    "defensive_event_profile",
]


def map_team(city: object, name: object) -> str | None:
    """Convert game-data city and team names to player-data abbreviations."""
    if pd.isna(city) or pd.isna(name):
        return None

    key = (str(city).strip(), str(name).strip())
    return TEAM_MAP.get(key)


def position_group(position: object) -> str:
    """Collapse listed positions into Guard, Wing, or Big."""
    if pd.isna(position):
        return "Unknown"

    position = str(position).strip()

    guards = {
        "PG",
        "PG-SG",
        "SG",
        "SG-PF",
        "SG-PG",
        "SG-SF",
        "SF-SG",
    }

    wings = {
        "SF",
        "SF-C",
        "SF-PF",
        "PF-SF",
    }

    bigs = {
        "C",
        "C-PF",
        "PF",
        "PF-C",
    }

    if position in guards:
        return "Guard"

    if position in wings:
        return "Wing"

    if position in bigs:
        return "Big"

    return "Unknown"

def build_team_records() -> pd.DataFrame:
    """Create regular-season team records for 2010–2025."""
    games = pd.read_csv(GAMES_FILE, low_memory=False)

    games["gameDate"] = pd.to_datetime(
        games["gameDate"],
        errors="coerce",
    )

    # The season is labeled by the calendar year in which it ends.
    games["year"] = (
        games["gameDate"].dt.year
        + (games["gameDate"].dt.month >= 10).astype(int)
    )

    # Emirates Cup games counted toward regular-season records.
    # The separate NBA Cup championship game did not.
    included_game_types = {
        "Regular Season",
        "NBA Emirates Cup",
    }

    games = games[
        games["gameType"].isin(included_game_types)
        & games["year"].between(START_YEAR, END_YEAR)
    ].copy()

    cup_championship = (
        games["gameLabel"]
        .fillna("")
        .eq("Emirates NBA Cup")
        & games["gameSubLabel"]
        .fillna("")
        .eq("Championship")
)

    games = games[~cup_championship].copy()

    games["homeScore"] = pd.to_numeric(
        games["homeScore"],
        errors="coerce",
    )

    games["awayScore"] = pd.to_numeric(
        games["awayScore"],
        errors="coerce",
    )

    games["home_team"] = [
        map_team(city, name)
        for city, name in zip(
            games["hometeamCity"],
            games["hometeamName"],
        )
    ]

    games["away_team"] = [
        map_team(city, name)
        for city, name in zip(
            games["awayteamCity"],
            games["awayteamName"],
        )
    ]

    unmapped = games[
        games["home_team"].isna()
        | games["away_team"].isna()
    ]

    if not unmapped.empty:
        missing_names = unmapped[
            [
                "hometeamCity",
                "hometeamName",
                "awayteamCity",
                "awayteamName",
            ]
        ].drop_duplicates()

        raise ValueError(
            "Unmapped team names found:\n"
            + missing_names.to_string(index=False)
        )

    home_rows = pd.DataFrame(
        {
            "year": games["year"],
            "team": games["home_team"],
            "win": (
                games["homeScore"] > games["awayScore"]
            ).astype(int),
        }
    )

    away_rows = pd.DataFrame(
        {
            "year": games["year"],
            "team": games["away_team"],
            "win": (
                games["awayScore"] > games["homeScore"]
            ).astype(int),
        }
    )

    team_games = pd.concat(
        [home_rows, away_rows],
        ignore_index=True,
    )

    team_records = (
        team_games.groupby(
            ["year", "team"],
            as_index=False,
        )
        .agg(
            games_played=("win", "size"),
            wins=("win", "sum"),
        )
    )

    team_records["losses"] = (
        team_records["games_played"]
        - team_records["wins"]
    )

    team_records["win_pct"] = (
        team_records["wins"]
        / team_records["games_played"]
    )
    official_2025 = pd.DataFrame(
        [
            {
                "year": 2025,
                "team": team,
                "games_played": wins + losses,
                "wins": wins,
                "losses": losses,
                "win_pct": wins / (wins + losses),
            }
            for team, (wins, losses) in FINAL_2025_RECORDS.items()
        ]
    )

    team_records = pd.concat(
        [
            team_records[team_records["year"] != 2025],
            official_2025,
        ],
        ignore_index=True,
    )

    records_2025 = team_records[
        team_records["year"] == 2025
    ]

    if (
        len(records_2025) != 30
        or not records_2025["games_played"].eq(82).all()
    ):
        raise ValueError(
            "The corrected 2025 standings must contain "
            "30 teams with 82 games each."
        )

    team_records["team_success_bucket"] = pd.qcut(
        team_records["win_pct"],
        q=3,
        labels=SUCCESS_LABELS,
    ).astype(str)

    return team_records.sort_values(
        ["year", "team"]
    ).reset_index(drop=True)


def build_player_seasons(
    team_records: pd.DataFrame,
) -> pd.DataFrame:
    """Create the cleaned player-team-season analysis table."""
    players = pd.read_csv(
        PLAYER_FILE,
        low_memory=False,
    )

    numeric_columns = [
        "Salary",
        "Year",
        "G",
        "GS",
        "MP",
        "FG",
        "FGA",
        "3P",
        "AST",
        "TRB",
        "STL",
        "BLK",
        "TOV",
        "PTS",
        "eFG%",
    ]

    for column in numeric_columns:
        players[column] = pd.to_numeric(
            players[column],
            errors="coerce",
        )

    players = players[
        players["Year"].between(START_YEAR, END_YEAR)
        & (players["G"] >= MIN_GAMES)
        & (players["MP"] >= MIN_MINUTES_PER_GAME)
    ].copy()

    players = players.rename(
        columns={
            "Player": "player",
            "Year": "year",
            "Team": "team",
            "Pos": "pos",
        }
    )

    players["position_group"] = players["pos"].apply(
        position_group
    )

    players["salary_m"] = players["Salary"] / 1_000_000
    players["minutes_per_game"] = players["MP"]
    players["points_per_game"] = players["PTS"]
    players["fga_per_game"] = players["FGA"]

    calculated_efg = (
        players["FG"] + 0.5 * players["3P"]
    ) / players["FGA"]

    players["efg_pct"] = players["eFG%"].fillna(
        calculated_efg
    )

    players["points_per_36"] = (
        players["PTS"] / players["MP"] * 36
    )

    players["assists_per_36"] = (
        players["AST"] / players["MP"] * 36
    )

    players["rebounds_per_36"] = (
        players["TRB"] / players["MP"] * 36
    )

    players["steals_per_36"] = (
        players["STL"] / players["MP"] * 36
    )

    players["blocks_per_36"] = (
        players["BLK"] / players["MP"] * 36
    )

    players["stocks_per_36"] = (
        (players["STL"] + players["BLK"])
        / players["MP"]
        * 36
    )

    players["turnovers_per_36"] = (
        players["TOV"] / players["MP"] * 36
    )

    # Role breadth counts six metrics at or above
    # the global eligible-player median.
    role_metrics = [
        "points_per_36",
        "assists_per_36",
        "rebounds_per_36",
        "steals_per_36",
        "blocks_per_36",
        "efg_pct",
    ]

    players["role_category_count"] = 0

    for metric in role_metrics:
        metric_median = players[metric].median()

        players["role_category_count"] += (
            players[metric] >= metric_median
        ).astype(int)

    players["profile_group"] = pd.cut(
        players["role_category_count"],
        bins=[-1, 1, 3, 6],
        labels=[
            "Narrow profile",
            "Mixed profile",
            "Balanced profile",
        ],
    ).astype(str)

    efg_median = players["efg_pct"].median()
    fga_median = players["fga_per_game"].median()

    players["efficient_lower_shot_label"] = (
        "Other core player"
    )

    players.loc[
        (players["efg_pct"] >= efg_median)
        & (players["fga_per_game"] < fga_median),
        "efficient_lower_shot_label",
    ] = "Efficient lower-shot player"

    # The original project rounded stocks/36 to three
    # decimals before determining the top quartile.
    players["stocks_per_36_rounded"] = (
        players["stocks_per_36"].round(3)
    )

    scoring_cutoff = players["points_per_game"].quantile(
        0.75
    )

    defensive_cutoff = (
        players["stocks_per_36_rounded"].quantile(0.75)
    )

    top_scorer = (
        players["points_per_game"] >= scoring_cutoff
    )

    top_defensive_events = (
        players["stocks_per_36_rounded"]
        >= defensive_cutoff
    )

    players["defensive_event_profile"] = (
        "Other core player"
    )

    players.loc[
        top_scorer & top_defensive_events,
        "defensive_event_profile",
    ] = "Top steals + blocks + top scorer"

    players.loc[
        ~top_scorer & top_defensive_events,
        "defensive_event_profile",
    ] = "Top steals + blocks, not top scorer"

    players.loc[
        top_scorer & ~top_defensive_events,
        "defensive_event_profile",
    ] = "Top scorer, not top steals + blocks"

    players = players.merge(
        team_records[
            [
                "year",
                "team",
                "win_pct",
                "team_success_bucket",
            ]
        ],
        on=["year", "team"],
        how="left",
        validate="many_to_one",
    )

    missing_team_context = players["win_pct"].isna().sum()

    if missing_team_context:
        missing = players.loc[
            players["win_pct"].isna(),
            ["year", "team"],
        ].drop_duplicates()

        raise ValueError(
            "Player rows are missing team records:\n"
            + missing.to_string(index=False)
        )

    output = players[OUTPUT_COLUMNS].copy()

    numeric_output_columns = [
        "salary_m",
        "minutes_per_game",
        "points_per_game",
        "points_per_36",
        "fga_per_game",
        "efg_pct",
        "assists_per_36",
        "rebounds_per_36",
        "stocks_per_36",
        "turnovers_per_36",
        "win_pct",
    ]

    output[numeric_output_columns] = output[
        numeric_output_columns
    ].round(3)

    return output.sort_values(
        ["year", "player", "team"]
    ).reset_index(drop=True)

def write_app_files(
    players: pd.DataFrame,
    teams: pd.DataFrame,
) -> None:
    """Write the CSV and JSON consumed by the public website."""
    STATIC_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    players.to_csv(
        APP_PLAYER_OUTPUT,
        index=False,
    )

    app_data = build_app_data(
        players,
        teams,
    )

    with APP_JSON_OUTPUT.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            app_data,
            handle,
            separators=(",", ":"),
            allow_nan=False,
        )



def print_validation(
    players: pd.DataFrame,
    teams: pd.DataFrame,
) -> None:
    """Print the main reproducibility checks."""
    duplicate_players = players.duplicated(
        ["player", "year", "team"]
    ).sum()

    duplicate_teams = teams.duplicated(
        ["year", "team"]
    ).sum()

    print("\n=== PIPELINE VALIDATION ===")
    print(f"Player rows: {len(players):,}")
    print(f"Team-season rows: {len(teams):,}")
    print(
        f"Player year range: "
        f"{players['year'].min()}–{players['year'].max()}"
    )
    print(
        f"Team year range: "
        f"{teams['year'].min()}–{teams['year'].max()}"
    )
    print(
        "Duplicate player-year-team rows: "
        f"{duplicate_players:,}"
    )
    print(
        "Duplicate team-season rows: "
        f"{duplicate_teams:,}"
    )
    print(
        "Missing player win percentages: "
        f"{players['win_pct'].isna().sum():,}"
    )

    print("\nProfile groups:")
    print(
        players["profile_group"]
        .value_counts()
        .to_string()
    )

    print("\nTeam-success buckets:")
    print(
        teams["team_success_bucket"]
        .value_counts()
        .to_string()
    )

    print("\nDefensive-label thresholds:")
    print(
        "Top-scorer cutoff: "
        f"{players['points_per_game'].quantile(0.75):.3f}"
    )
    print(
        "Top defensive-events cutoff: "
        f"{players['stocks_per_36'].round(3).quantile(0.75):.3f}"
    )

    print("\nFiles created:")
    print(PLAYER_OUTPUT)
    print(TEAM_OUTPUT)
    print(APP_PLAYER_OUTPUT)
    print(APP_JSON_OUTPUT)

def sample_evenly(
    frame: pd.DataFrame,
    max_rows: int = 1200,
) -> pd.DataFrame:
    """Return an evenly distributed sample while preserving row order."""
    if len(frame) <= max_rows:
        return frame.copy()

    indices = [
        int(index * len(frame) / max_rows)
        for index in range(max_rows)
    ]

    return frame.iloc[indices].copy()


def json_records(frame: pd.DataFrame) -> list[dict]:
    """Convert a DataFrame into JSON-safe records."""
    return json.loads(
        frame.round(3).to_json(
            orient="records",
        )
    )


def build_app_data(
    players: pd.DataFrame,
    teams: pd.DataFrame,
) -> dict:
    """Create the summary and chart data used by the D3 app."""
    profile_mix = (
        players.groupby(
            [
                "team_success_bucket",
                "profile_group",
            ],
            as_index=False,
        )
        .agg(
            players=("player", "size"),
            median_win_pct=("win_pct", "median"),
        )
        .rename(
            columns={
                "profile_group": "profile",
            }
        )
    )

    profile_mix["share_of_bucket"] = (
        profile_mix["players"]
        / profile_mix.groupby(
            "team_success_bucket"
        )["players"].transform("sum")
    )

    efficient_lower_shot = (
        players.groupby(
            [
                "team_success_bucket",
                "efficient_lower_shot_label",
            ],
            as_index=False,
        )
        .agg(
            players=("player", "size"),
            median_win_pct=("win_pct", "median"),
        )
        .rename(
            columns={
                "efficient_lower_shot_label": "profile",
            }
        )
    )

    efficient_lower_shot["share_of_bucket"] = (
        efficient_lower_shot["players"]
        / efficient_lower_shot.groupby(
            "team_success_bucket"
        )["players"].transform("sum")
    )

    defensive_profiles = {
        "Top steals + blocks + top scorer",
        "Top steals + blocks, not top scorer",
    }

    defensive_rows = players[
        players["defensive_event_profile"].isin(
            defensive_profiles
        )
    ].copy()

    defense_overlap = (
        defensive_rows.groupby(
            [
                "team_success_bucket",
                "defensive_event_profile",
            ],
            as_index=False,
        )
        .agg(
            players=("player", "size"),
            median_win_pct=("win_pct", "median"),
        )
        .rename(
            columns={
                "defensive_event_profile": "profile",
            }
        )
    )

    defense_overlap["share_of_bucket"] = (
        defense_overlap["players"]
        / defense_overlap.groupby(
            "team_success_bucket"
        )["players"].transform("sum")
    )

    ordered_players = players.sort_values(
        ["year", "player", "team"]
    ).reset_index(drop=True)

    scoring_scatter = sample_evenly(
        ordered_players[
            [
                "year",
                "player",
                "team",
                "points_per_game",
                "win_pct",
                "profile_group",
                "team_success_bucket",
            ]
        ]
    )

    efficiency_scatter = sample_evenly(
        ordered_players[
            [
                "year",
                "player",
                "team",
                "fga_per_game",
                "efg_pct",
                "team_success_bucket",
            ]
        ]
    )

    defense_scatter = sample_evenly(
        ordered_players[
            [
                "year",
                "player",
                "team",
                "points_per_game",
                "stocks_per_36",
                "defensive_event_profile",
                "team_success_bucket",
            ]
        ].rename(
            columns={
                "stocks_per_36": "steals_blocks_per_36",
            }
        )
    )

    efficient_examples = (
        players[
            players["efficient_lower_shot_label"]
            == "Efficient lower-shot player"
        ]
        .sort_values(
            ["efg_pct", "fga_per_game"],
            ascending=[False, True],
        )
        .head(3)
    )

    defensive_examples = (
        players[
            players["defensive_event_profile"]
            == "Top steals + blocks, not top scorer"
        ]
        .sort_values(
            "stocks_per_36",
            ascending=False,
        )
        .head(3)
    )

    examples = []

    for row in efficient_examples.itertuples():
        examples.append(
            {
                "year": int(row.year),
                "player": row.player,
                "team": row.team,
                "note": (
                    "Efficient lower-shot contributor: "
                    f"{row.efg_pct:.1%} eFG on "
                    f"{row.fga_per_game:.1f} FGA/game."
                ),
            }
        )

    for row in defensive_examples.itertuples():
        examples.append(
            {
                "year": int(row.year),
                "player": row.player,
                "team": row.team,
                "note": (
                    "Non-top scorer with defensive-event "
                    f"production: {row.stocks_per_36:.2f} "
                    "steals + blocks per 36."
                ),
            }
        )

    high_winning = players[
        players["team_success_bucket"]
        == "High-winning teams"
    ]

    low_winning = players[
        players["team_success_bucket"]
        == "Low-winning teams"
    ]

    efficient_label = "Efficient lower-shot player"

    top_stocks_not_scorer_share = (
        defensive_rows["defensive_event_profile"]
        .eq("Top steals + blocks, not top scorer")
        .mean()
    )

    return {
        "summary": {
            "playerSeasonRows": int(len(players)),
            "teamSeasonRecords": int(len(teams)),
            "pointsWinCorrelation": round(
                float(
                    players["points_per_game"].corr(
                        players["win_pct"]
                    )
                ),
                3,
            ),
            "roleCountWinCorrelation": round(
                float(
                    players["role_category_count"].corr(
                        players["win_pct"]
                    )
                ),
                3,
            ),
            "highWinningEfficientLowerShotShare": round(
                float(
                    high_winning[
                        "efficient_lower_shot_label"
                    ].eq(efficient_label).mean()
                ),
                3,
            ),
            "lowWinningEfficientLowerShotShare": round(
                float(
                    low_winning[
                        "efficient_lower_shot_label"
                    ].eq(efficient_label).mean()
                ),
                3,
            ),
            "topStocksNotTopScorerShare": round(
                float(top_stocks_not_scorer_share),
                3,
            ),
        },
        "profileMix": json_records(profile_mix),
        "efficientLowerShot": json_records(
            efficient_lower_shot
        ),
        "defenseOverlap": json_records(defense_overlap),
        "scoringScatter": json_records(scoring_scatter),
        "efficiencyScatter": json_records(
            efficiency_scatter
        ),
        "defenseScatter": json_records(defense_scatter),
        "examples": examples,
    }


def main() -> None:
    if not PLAYER_FILE.exists():
        raise FileNotFoundError(
            f"Missing player file: {PLAYER_FILE}"
        )

    if not GAMES_FILE.exists():
        raise FileNotFoundError(
            f"Missing games file: {GAMES_FILE}"
        )

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    team_records = build_team_records()
    player_seasons = build_player_seasons(team_records)

    team_records.to_csv(
        TEAM_OUTPUT,
        index=False,
    )

    player_seasons.to_csv(
        PLAYER_OUTPUT,
        index=False,
    )

    write_app_files(
        player_seasons,
        team_records,
    )

    print_validation(
        player_seasons,
        team_records,
    )


if __name__ == "__main__":
    main()