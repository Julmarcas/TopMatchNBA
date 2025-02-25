from topmatchnba.data import Game


def calculate_game_rating(game: Game) -> Game:
    """
    Calculate the total game rating based on various statistics,
    including score difference, standings, maximum points by a player,
    and change in lead. The computed total is stored in game.game_rating.total.

    :param game: The game object containing game data and a game_rating attribute.
    :return: The computed total game rating as an integer.
    """
    # Calculate individual components of the game rating
    score_diff = calculate_score_difference(game)
    standings_rating = calculate_standings(game)
    max_points = calculate_maximum_points_player(game)
    lead_changes = calculate_change_lead(game)

    # Sum all components to get the total rating
    total_rating = score_diff + standings_rating + max_points + lead_changes

    # Update the game rating details in the game object
    game.game_rating.score_difference = score_diff
    game.game_rating.standings = standings_rating
    game.game_rating.maximum_points_player = max_points
    game.game_rating.change_lead = lead_changes
    # Max 32
    game.game_rating.total = total_rating

    return game


def calculate_change_lead(game: Game) -> int:
    """
    Calculate the game rating based on the number of lead changes.

    The rating is determined as follows:
        - More than 16 lead changes: 10 points
        - More than 10 lead changes: 8 points
        - More than 6 lead changes: 6 points
        - More than 3 lead changes: 2 points
        - Otherwise: 0 points

    :param game: A Game object with a 'lead_changes' attribute.
    :return: The calculated rating as an integer.
    """
    lead_changes = game.lead_changes

    if lead_changes > 16:
        return 10
    if lead_changes > 10:
        return 8
    if lead_changes > 6:
        return 6
    if lead_changes > 3:
        return 2
    return 0


def calculate_maximum_points_player(game: Game) -> int:
    """
    Calculate the rating based on the maximum points scored by any player.

    Returns:
        4 if maximum points > 50,
        2 if maximum points > 40,
        otherwise 0.
    """
    points = game.maximum_points_player
    if points > 50:
        return 4
    if points > 40:
        return 2
    return 0


def calculate_standings(game: Game) -> int:
    """
    Calculate the rating based on the conference positions of the home and visitor teams.

    Returns:
        8 if both teams are in the top 2,
        6 if both teams are in the top 4,
        4 if both teams are in the top 7,
        2 if either team is in the top 3,
        otherwise 0.
    """
    home_pos = game.home_team.conference_position
    visitor_pos = game.visitor_team.conference_position

    if home_pos <= 2 and visitor_pos <= 2:
        return 8
    if home_pos <= 4 and visitor_pos <= 4:
        return 6
    if home_pos <= 7 and visitor_pos <= 7:
        return 4
    if home_pos <= 3 or visitor_pos <= 3:
        return 2
    return 0


def calculate_score_difference(game: Game) -> int:
    """
    Calculate the rating based on the score difference between the teams.

    Returns:
        10 if the score difference is less than 2,
        8 if the score difference is less than 4,
        6 if the score difference is less than 6,
        4 if the score difference is less than 10,
        otherwise 0.
    """
    score_diff = abs(game.home_team_points - game.visitor_team_points)
    if score_diff < 2:
        return 10
    if score_diff < 4:
        return 8
    if score_diff < 6:
        return 6
    if score_diff < 10:
        return 4
    return 0
