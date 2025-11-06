import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="🏏 IPL Match Insights", layout="wide")

st.title("🏏 IPL Match Data Analysis Dashboard")

# File uploader
uploaded_file = st.file_uploader("📤 Upload IPL matches.csv file", type="csv")

if uploaded_file is not None:
    # Load data
    df = pd.read_csv(uploaded_file, header=None)
    df.columns = [
        'id', 'season', 'city', 'date', 'team1', 'team2',
        'toss_winner', 'toss_decision', 'result', 'winner', 'venue'
    ]

    st.success("✅ File uploaded successfully!")
    st.dataframe(df.head())

    # Core derived columns
    df['toss_winner'] = df['toss_winner'].astype(str)
    df['winner'] = df['winner'].astype(str)

    # Identify batting first
    def get_opponent(row):
        if row['toss_winner'] == row['team1']:
            return row['team2']
        elif row['toss_winner'] == row['team2']:
            return row['team1']
        else:
            return None

    def batting_first(row):
        if row['toss_decision'] == 'bat':
            return row['toss_winner']
        elif row['toss_decision'] == 'field':
            return get_opponent(row)
        return None

    df['batting_first'] = df.apply(batting_first, axis=1)
    df['winner_batted_first'] = df['winner'] == df['batting_first']
    df['toss_winner_won_match'] = df['toss_winner'] == df['winner']

    st.header("📊 Key Insights")

    # 1. Team with most wins in 2008
    wins_2008 = df[df['season'] == 2008]['winner'].value_counts().idxmax()
    st.write(f"🏆 *Team with most wins in 2008:* {wins_2008}")

    # 2. City hosting most matches
    top_city = df['city'].value_counts().idxmax()
    st.write(f"🌆 *City hosting the most matches:* {top_city}")

    # 3. Team winning more often while batting first
    batting_first_wins = df[df['winner_batted_first']]['winner'].value_counts().idxmax()
    st.write(f"🔥 *Team winning more often while batting first:* {batting_first_wins}")

    # 4. Team winning more often while fielding first
    fielding_first_wins = df[~df['winner_batted_first']]['winner'].value_counts().idxmax()
    st.write(f"💪 *Team winning more often while fielding first:* {fielding_first_wins}")

    # 5. Toss influence
    toss_win_pct = (df['toss_winner_won_match'].mean() * 100).round(2)
    st.write(f"🎯 *Does winning the toss help?* Yes, {toss_win_pct}% of toss winners won the match.")

    # 6. Toss decision success
    df['toss_decision_norm'] = df['toss_decision'].replace({'bowl': 'field'})
    decision_success = (
        df[df['toss_winner_won_match']]['toss_decision_norm']
        .value_counts()
        .idxmax()
    )
    st.write(f"🧠 *Toss decision leading to more wins:* {decision_success}")

    st.divider()
    st.subheader("🏟 Venue & City Analysis")

    st.write("*Most matches by stadium:*", df['venue'].value_counts().idxmax())
    st.write("*Average matches per city:*", round(df['city'].value_counts().mean(), 2))

    # Home/away logic (approximation using city/team match)
    df['home_team'] = df.apply(lambda r: r['team1'] if str(r['team1']).split()[-1] in str(r['city']) else None, axis=1)
    df['away_team'] = df.apply(lambda r: r['team2'] if r['team2'] != r['home_team'] else None, axis=1)

    # Venue where home team wins most
    home_wins = df[df['winner'] == df['home_team']]['venue'].value_counts()
    if not home_wins.empty:
        st.write("*Venue with most home wins:*", home_wins.idxmax())

    # Venue where away team wins most
    away_wins = df[df['winner'] == df['away_team']]['venue'].value_counts()
    if not away_wins.empty:
        st.write("*Venue with most away wins:*", away_wins.idxmax())

    st.divider()
    st.subheader("📈 Deeper Statistics")

    # Team with highest win percentage
    total_played = pd.concat([df['team1'], df['team2']]).value_counts()
    total_wins = df['winner'].value_counts()
    win_percentage = (total_wins / total_played * 100).sort_values(ascending=False).round(2)
    top_team = win_percentage.index[0]
    st.write(f"🏅 *Highest win percentage:* {top_team} ({win_percentage.iloc[0]}%)")

    # Toss winner losing %
    toss_lost_pct = 100 - toss_win_pct
    st.write(f"😅 *Toss winner lost match:* {toss_lost_pct:.2f}% of the time")

    # Matches per team
    st.write("*Teams with most appearances:*")
    st.bar_chart(total_played)

    # Batting vs fielding win share
    bat_win_pct = df['winner_batted_first'].mean() * 100
    field_win_pct = 100 - bat_win_pct
    st.write(f"⚖ *Batting first wins:* {bat_win_pct:.2f}% | *Fielding first wins:* {field_win_pct:.2f}%")

    st.divider()
    st.subheader("🧩 Additional Insights")

    st.write("*Cities where fielding gives higher chance of winning:*")
    city_fielding_success = (
        df.groupby('city')['winner_batted_first'].apply(lambda x: (1 - x.mean()) * 100).round(2)
    )
    st.dataframe(city_fielding_success.sort_values(ascending=False))

    st.write("*Most frequent opponent pairs:*")
    pair_counts = (
        df.groupby(['team1', 'team2']).size().reset_index(name='matches').sort_values('matches', ascending=False)
    )
    st.dataframe(pair_counts.head(10))

    st.write("*Teams dominating in home city (approx):*")
    st.dataframe(home_wins.head(10))

else:
    st.info("👆 Please upload your IPL matches.csv file to begin analysis.")
