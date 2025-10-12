# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import urllib.request

import pandas as pd


def read_table(url, table_file, html_file):
    # Download file
    urllib.request.urlretrieve(url=url, filename=table_file)

    # Load file
    table_xls = pd.ExcelFile(table_file)

    # Load data from the "Ergebnisse" sheet
    df_ergebnisse = pd.read_excel(table_xls, sheet_name="Ergebnisse", header=1)

    #   Spieltag    Spielnummer  Datum              Heimmannschaft              Gastmannschaft      Endstand
    #   559         12           09.03.2025 18:00   ESV Flügelrad Nürnberg 2    TV 1861 Hersbruck   52:73

    # Remove the last row
    row_len = df_ergebnisse.__len__() - 1
    df_drop_row = df_ergebnisse.drop([row_len])

    # Extract relevant columns and remove empty rows
    df_reduce = df_drop_row[["Heimmannschaft", "Gastmannschaft", "Endstand"]].dropna()

    # Remove non-numeric rows in "Endstand"
    df = df_reduce[df_reduce["Endstand"].str.contains(r"^\d+ : \d+$", regex=True, na=False)]

    # Split results into Home Points and Guest Points
    df[['Home Points', 'Guest Points']] = df['Endstand'].str.split(' : ', expand=True).astype(int)

    # Capture teams
    teams = set(df["Heimmannschaft"]).union(set(df["Gastmannschaft"]))

    # Create the point table
    table = {team: {"Games": 0, "Wins": 0, "Losses": 0, "Points": 0, "Points Made": 0, "Points Get": 0, "Diff": 0}
             for team in teams}

    # Calculate table
    for _, row in df.iterrows():
        home, guest = row["Heimmannschaft"], row["Gastmannschaft"]
        points_home, points_guest = row["Home Points"], row["Guest Points"]

        table[home]["Games"] += 1
        table[guest]["Games"] += 1

        table[home]["Diff"] += points_home - points_guest
        table[home]["Points Made"] += points_home
        table[home]["Points Get"] += points_guest

        table[guest]["Diff"] += points_guest - points_home
        table[guest]["Points Made"] += points_guest
        table[guest]["Points Get"] += points_home

        if points_home > points_guest:
            table[home]["Wins"] += 1
            table[home]["Points"] += 2
            table[guest]["Losses"] += 1
        else:
            table[guest]["Wins"] += 1
            table[guest]["Points"] += 2
            table[home]["Losses"] += 1

    # Convert to DataFrame and sort by points
    df_table = pd.DataFrame.from_dict(table, orient="index")
    df_table = df_table.reset_index()
    df_table.rename(columns={"index": "Team"}, inplace=True)
    df_table = df_table.sort_values(by=["Points", "Diff"], ascending=[False, False])

    # Display final table
    print(df_table.head())

    # Save final table as HTML
    html_table = df_table.to_html(index=False, border=1, justify="center")

    # Save HTML file
    with open(html_file, "w", encoding="utf-16") as file:
        file.write(html_table)

    print("HTML table has been saved as '" + html_file + "'")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    root_url = "https://www.basketball-bund.net/servlet/sport.dbb.export.ExcelExportErgebnissePublic"
    league_stuff = "?liga_id="
    end_key = "&sessionkey=sport.dbb.liga.ErgebnisseViewPublic/index.jsp_"

    leagues = \
        [
            {
                "name": "U12",
                "league_id": "51502",
                "table_file": "MFR_U12_mix_Kreisliga_Nord-2025.xls"
            },
            {
                "name": "H3",
                "league_id": "48511",
                "table_file": "MFR_Bezirksklasse_Herren-2025.xls"
            }
        ]

    for league in leagues:
        league_url = root_url + league_stuff + league["league_id"] + end_key
        print(league_url)
        league_table_file = league["table_file"]
        league_html_file = f"Tabelle_{league["name"]}.html"
        read_table(league_url, league_table_file, league_html_file)
