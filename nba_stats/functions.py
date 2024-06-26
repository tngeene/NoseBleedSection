from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import base64
from .models import PlayerHeadshot
from io import BytesIO

# career stats
def player_career_numbers(player_id):
    player_stats = playercareerstats.PlayerCareerStats(player_id=player_id)
    dict_response = player_stats.get_normalized_dict()  # Getting dictionary response

    player_career_regular_season_totals = dict_response['CareerTotalsRegularSeason']

    return player_career_regular_season_totals


# regular season totals
def player_regular_season(player_id):
    player_stats = playercareerstats.PlayerCareerStats(player_id=player_id)
    dict_response = player_stats.get_normalized_dict()  # Getting dictionary response

    regular_season_totals = dict_response['SeasonTotalsRegularSeason']

    return regular_season_totals


# playoff totals
def player_post_season(player_id):
    player_stats = playercareerstats.PlayerCareerStats(player_id=player_id)
    dict_response = player_stats.get_normalized_dict()  # Getting dictionary response

    post_season_totals = dict_response['SeasonTotalsPostSeason']

    return post_season_totals


def rankings_regular_season(player_id):
    player_stats = playercareerstats.PlayerCareerStats(player_id=player_id)
    dict_response = player_stats.get_normalized_dict()  # Getting dictionary response

    regular_season_rankings = dict_response['SeasonRankingsRegularSeason']

    return regular_season_rankings


def rankings_post_season(player_id):
    player_stats = playercareerstats.PlayerCareerStats(player_id=player_id)
    dict_response = player_stats.get_normalized_dict()  # Getting dictionary response

    post_season_rankings = dict_response['SeasonRankingsPostSeason']

    return post_season_rankings


def get_player_image(player_id, player_name):
    # Check for player image
    player = PlayerHeadshot.objects.filter(player_id=player_id).first()

    if player:
        return player.head_shot_url

    else:

        url = f'https://www.nba.com/player/{player_id}'

        # Make an HTTP GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the player image tag within the appropriate class or element
        player_image_div = soup.find('div', {'class': 'PlayerSummary_mainInnerTeam____nFZ'})
        if player_image_div:
            img_tag = player_image_div.find('img',
                                            {'class': 'PlayerImage_image__wH_YX PlayerSummary_playerImage__sysif'})

            if img_tag:
                head_shot_url = img_tag['src']

                # save image to database
                instance = PlayerHeadshot(player_id=player_id, player_name=player_name, head_shot_url=head_shot_url)
                instance.save()
                return head_shot_url

    return None


# function for getting player graph
def get_graph(player1_id, player1_name, player2_id, player2_name, stat_category, title):
    # Get players yearly stats
    player1_stats = player_regular_season(player1_id)
    player2_stats = player_regular_season(player2_id)

    # getting per game averages
    for season_data in player1_stats:

        # points per game
        if season_data['GP'] > 0:
            season_data['PPG'] = round(season_data['PTS'] / season_data['GP'], 2)
        else:
            season_data['PPG'] = 0  # To avoid division by zero in case GP is 0

        # assists per game
        if season_data['GP'] > 0:
            season_data['APG'] = round(season_data['AST'] / season_data['GP'], 1)
        else:
            season_data['APG'] = 0

        # blocks per game
        if season_data['GP'] > 0:
            season_data['BLKPG'] = round(season_data['BLK'] / season_data['GP'], 1)
        else:
            season_data['BLKPG'] = 0

        # rebounds per game
        if season_data['GP'] > 0:
            season_data['RPG'] = round(season_data['REB'] / season_data['GP'], 1)
        else:
            season_data['RPG'] = 0

        # steals per game
        if season_data['GP'] > 0:
            season_data['STLPG'] = round(season_data['STL'] / season_data['GP'], 1)
        else:
            season_data['STLPG'] = 0

    for season_data in player2_stats:
        # points per game
        if season_data['GP'] > 0:
            season_data['PPG'] = round(season_data['PTS'] / season_data['GP'], 2)
        else:
            season_data['PPG'] = 0  # To avoid division by zero in case GP is 0

        # assists per game
        if season_data['GP'] > 0:
            season_data['APG'] = round(season_data['AST'] / season_data['GP'], 1)
        else:
            season_data['APG'] = 0

        # blocks per game
        if season_data['GP'] > 0:
            season_data['BLKPG'] = round(season_data['BLK'] / season_data['GP'], 1)
        else:
            season_data['BLKPG'] = 0

        # rebounds per game
        if season_data['GP'] > 0:
            season_data['RPG'] = round(season_data['REB'] / season_data['GP'], 1)
        else:
            season_data['RPG'] = 0

        # steals per game
        if season_data['GP'] > 0:
            season_data['STLPG'] = round(season_data['STL'] / season_data['GP'], 1)
        else:
            season_data['STLPG'] = 0

    #  We need to find which player has had the the shorter season between the two
    # The shorter season will be used to plot the x axis
    if len(player1_stats) > len(player2_stats):
        seasons = len(player2_stats)

    else:
        seasons = len(player1_stats)

    # Extract stat category we are comparing for both players
    player1_numbers = [player1_stats[i][stat_category] for i in range(seasons)]
    player2_numbers = [player2_stats[i][stat_category] for i in range(seasons)]

    # Create a line chart using Matplotlib
    plt.figure(figsize=(10, 6))

    # plot both line graphs
    # x-axis values to range(1, seasons + 1) to match the length of player1_numbers and player2_numbers.
    plt.plot(range(1, seasons + 1), player1_numbers, label=player1_name, marker='o')
    plt.plot(range(1, seasons + 1), player2_numbers, label=player2_name, marker='o')

    # Chart labels
    plt.title(f'{player1_name} and {player2_name} {title} Comparison')
    plt.xlabel('Year')
    plt.ylabel(title)
    plt.legend()
    plt.grid(True)

    # Set x-axis ticks to be integer values only
    # The plt.xticks function is used to set the x-axis ticks, and it expects a 1D array-like iterable input
    plt.xticks(range(1, seasons + 1))

    # Save the plot to a BytesIO object
    img_data = BytesIO()
    plt.savefig(img_data, format='png')
    plt.close()

    # Move the buffer's position to the start
    img_data.seek(0)
    encoded_image = base64.b64encode(img_data.read()).decode("utf-8")

    return encoded_image
