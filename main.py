import urllib.request
from tkinter.font import names
from typing import Dict
import pandas as pd


def read_table(url_tbl: str, table_file: str, html_file: str) -> None:
    """Download, process, and generate a basketball league standings HTML table.
    :param url_tbl:    str: 'https://www.basketball-bund.net/servlet/...'
    :param table_file: str: 'MFR_U12_mix_Kreisliga_Nord-2025.xls'
    :param html_file:  str: 'Tabelle_U12.html'
    """

    # Download the Excel file
    urllib.request.urlretrieve(url_tbl, table_file)

    # Read 'Ergebnisse' sheet directly (skipping first row header)
    df = pd.read_excel(table_file, sheet_name="Ergebnisse", header=1)

    # Drop the last row (often metadata) and remove incomplete rows
    df = df.iloc[:-1].dropna(subset=["Heimmannschaft", "Gastmannschaft", "Endstand"])

    # Filter valid score formats like "52 : 73"
    df = df[df["Endstand"].str.match(r"^\d+\s*:\s*\d+$", na=False)]

    # Split 'Endstand' into numeric columns
    df[["Home Points", "Guest Points"]] = df["Endstand"].str.split(":", expand=True).astype(int)

    # Initialize team stats dictionary
    teams = pd.unique(df[["Heimmannschaft", "Gastmannschaft"]].values.ravel("K"))
    for team_str in teams:
        team_str = str(team_str).replace("ü","ue").replace("ö","oe")
    stats: Dict[str, Dict[str, int]] = {
        team: {"Games": 0, "Wins": 0, "Losses": 0, "Points": 0,
               "Points Made": 0, "Points Get": 0, "Diff": 0}
        for team in teams
    }

    # Process match results efficiently
    for _, row in df.iterrows():
        home, guest = row["Heimmannschaft"], row["Gastmannschaft"]
        home_pts, guest_pts = row["Home Points"], row["Guest Points"]

        # Update basic stats
        for team, pts_for, pts_against in [(home, home_pts, guest_pts), (guest, guest_pts, home_pts)]:
            stats[team]["Games"] += 1
            stats[team]["Points Made"] += pts_for
            stats[team]["Points Get"] += pts_against
            stats[team]["Diff"] += pts_for - pts_against

        # Determine win/loss
        if home_pts > guest_pts:
            stats[home]["Wins"] += 1
            stats[home]["Points"] += 2
            stats[guest]["Losses"] += 1
        else:
            stats[guest]["Wins"] += 1
            stats[guest]["Points"] += 2
            stats[home]["Losses"] += 1

    # Convert to DataFrame, sort, and export to HTML
    df_table = (
        pd.DataFrame.from_dict(stats, orient="index")
        .reset_index()
        .rename(columns={"index": "Team"})
        .sort_values(by=["Points", "Diff"], ascending=[False, False])
    )

    # Save to HTML (UTF-8 for better compatibility)
    df_table.to_html(html_file, index=False, border=1, justify="center", encoding="utf-8")

    print(f"✅ HTML table saved as '{html_file}'")
    print(df_table.head())


if __name__ == '__main__':
    BASE_URL = "https://www.basketball-bund.net/servlet/sport.dbb.export.ExcelExportErgebnissePublic"
    END_KEY = "&sessionkey=sport.dbb.liga.ErgebnisseViewPublic/index.jsp_"
    LEAGUES = [
        {"name": "U12", "league_id": "51502", "file": "MFR_U12_mix_Kreisliga_Nord-2025.xls"},
        {"name": "U10", "league_id": "51505", "file": "MFR_U10_mix_Kreisliga_Nord-2025.xls"},
        {"name": "H3", "league_id": "48511", "file": "MFR_Bezirksklasse_Herren-2025.xls"},
    ]

    for league in LEAGUES:
        url = f"{BASE_URL}?liga_id={league['league_id']}{END_KEY}"
        print(f"Fetching {league['name']} data from {url}")
        read_table(url_tbl=url, table_file=league["file"], html_file=f"Tabelle_{league['name']}.html")
