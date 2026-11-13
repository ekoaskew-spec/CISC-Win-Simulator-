from drafter import *
from dataclasses import dataclass
import random

hide_debug_information()
set_website_title("Your Drafter Website")
set_website_framed(False)

set_site_information(
        author="Eko Askew",
        description="My site is a win simulator for soccer games. The user inputs information about the teams and the site outputs the simulated match",
        sources="I build it with help from an LLM.",
        planning="",
        links=["https://github.com/ekoaskew-spec/CISC-Win-Simulator-"]
        )

@dataclass
class RealLeague:
    league_average_goals: float
    name: str

@dataclass
class Team:
    name: str
    goals_scored_average: float
    goals_conceded_average: float
    points: int
    league: RealLeague

@dataclass
class State:
    round_robin_teams: list[Team]
    knockout_teams: list[Team]
    show_knockout_scores: bool
    knockout_winners: list[Team]
    
@dataclass    
class FantasyLeague:
    teams: list[Team]
    name: str

@dataclass
class SingleGame:
    home: Team
    away: Team
    home_goals: int
    away_goals: int
    
@dataclass
class TeamStanding:
    team: Team
    wins: int
    draws: int
    losses: int
    goals_scored: int
    goals_conceded: int
    points: int
    
@dataclass
class ResultsTable:
    name: str
    user_league: FantasyLeague
    matches: list[SingleGame]
    
LEAGUES = [
    RealLeague(2.8, "Premier League"),
    RealLeague(2.6, "La Liga"),
    RealLeague(2.8, "Bundesliga"),
    RealLeague(2.4, "Serie A"),
    RealLeague(2.5, "Ligue 1")
    ]
LEAGUE_NAMES = []

for league in LEAGUES:
    LEAGUE_NAMES.append(league.name)

    
def find_league(name: str) -> RealLeague:
    for league in LEAGUES:
        if league.name == name:
            return league

def make_team(name: str, scored: float, conceded: float, league_name: str) -> Team:
    league = find_league(league_name)
    return Team(name, scored, conceded, 0, league)

def find_overall_league_average() -> float:
    total = 0
    
    for league in LEAGUES:
        total += league.league_average_goals
    
    return total / len(LEAGUES)

def calculate_team_strength(team: Team, opponent: Team) -> float:
    overall_average = find_overall_league_average()
    
    league_adjustment = (team.league.league_average_goals / overall_average)
    
    attacking_strength = (team.goals_scored_average * league_adjustment)
    
    defending_strength = (opponent.goals_conceded_average * league_adjustment)
    
    return (attacking_strength + defending_strength) / 2

def simulate_game(team1: Team, team2: Team) -> Team:
    team1_strength = calculate_team_strength(team1, team2)
    team2_strength = calculate_team_strength(team2, team1)
    
    total_strength = team1_strength + team2_strength
    
    if total_strength == 0:
        team1_probability = 0.5
    else:
        team1_probability = team1_strength / total_strength
    
    coin_flip = random.random()
    
    if coin_flip < team1_probability:
        return team1
    else:
        return team2

def make_score(winner: Team, loser: Team) -> list[int]:
    """
    This makes a score by assigning a random number from 1 to 5 and giving that to the winning teams score
    and then randomly assigning a random number from 0 to n-1 for the lower teams score. n being the winning teams score

    args:
        winner(Team)
        loser(Team)
        
    returns:
        This returns a list of ints which would be the score of the match
    """
    winner_goals = random.randint(1, 5)
    loser_goals = random.randint(0, winner_goals - 1)
    
    return [winner_goals, loser_goals]

def start_round_robin(state: State, teams: list[Team]) -> Page:
    state.round_robin_teams = teams
    
    return Page(state, [
        Header("Your Round Robin", 1),
        "Your teams have been entered!",
        Button("Continue", "round_robin_results")
    ])

def simulate_round_robin_match(home: Team, away: Team) -> SingleGame:
    """
This assigns a 20% chance of a draw in any round robin match.
A random number gets drawn and if it is less than .2, the match is a draw.
If it is not, the match will be simulated like normal.

args:
    home(Team)
    away(Team)
    
Returns:
    This returns an instance of the dataclass SingleGame
    """
    draw_chance = random.random()
    
    if draw_chance < 0.2:
        goals = random.randint(0,3)
        home_goals = goals
        away_goals = goals
    
    else:
        winner = simulate_game(home, away)
        
        if winner == home:
            loser = away
        
        else:
            loser = home
        
        score = make_score(winner, loser)
        
        if winner == home:
            home_goals = score[0]
            away_goals = score[1]
        
        else:
            home_goals = score[1]
            away_goals = score[0]
    
    return SingleGame(home, away, home_goals, away_goals)

def simulate_round_robin(teams: list[Team]) -> list[SingleGame]:
    matches = []
    
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            home = teams[i]
            away = teams[j]
            
            match = simulate_round_robin_match(home, away)
            matches.append(match)
            
    return matches

def make_initial_standings(teams: list[Team]) -> list[TeamStanding]:
    standings = []
    
    for team in teams:
        standing = TeamStanding(team,0,0,0,0,0,0)
        
        standings.append(standing)
    return standings

def find_standing(standings: list[TeamStanding], team: Team) -> TeamStanding:
    for standing in standings:
        if standing.team == team:
            return standing

def update_standings(standings: list[TeamStanding],match: SingleGame) -> None:
    
    home_standing = find_standing(standings, match.home)
    away_standing = find_standing(standings, match.away)
    
    home_standing.goals_scored += match.home_goals
    home_standing.goals_conceded += match.away_goals
    
    away_standing.goals_scored += match.away_goals
    away_standing.goals_conceded += match.home_goals
    
    if match.home_goals > match.away_goals:
        home_standing.wins += 1
        home_standing.points += 3
        away_standing.losses += 1
        
    elif match.away_goals > match.home_goals:
        away_standing.wins += 1
        away_standing.points += 3
        home_standing.losses += 1
        
    else:
        home_standing.draws += 1
        away_standing.draws += 1
        home_standing.points += 1
        away_standing.points += 1
        
def calculate_standings(teams: list[Team], matches: list[SingleGame]) -> list[TeamStanding]:
    
    standings = make_initial_standings(teams)
    
    for match in matches:
        update_standings(standings, match)
    
    return standings

def calculate_goal_difference(standing: TeamStanding) -> int:
    return standing.goals_scored - standing.goals_conceded

def sort_standings(standings: list[TeamStanding]) -> list[TeamStanding]:
    for i in range(len(standings)):
        for j in range(i + 1, len(standings)):
            
            first = standings[i]
            second = standings[j]
            
            should_swap = False
            
            if second.points > first.points:
                should_swap = True
            
            elif second.points == first.points:
                first_goal_difference = calculate_goal_difference(first)
                second_goal_difference = calculate_goal_difference(second)
                
                if second_goal_difference > first_goal_difference:
                    should_swap = True
            if should_swap:
                standings[i] = second
                standings[j] = first
    return standings

def simulate_knockout_match(home: Team, away: Team) -> SingleGame:
    
    winner = simulate_game(home,away)
   
    if winner == home:
        loser = away
    else:
        loser = home
    
    score = make_score(winner, loser)
    
    if winner == home:
        home_goals = score[0]
        away_goals = score[1]
    
    else:
        home_goals = score[1]
        away_goals = score[0]
    
    return SingleGame(home,away,home_goals,away_goals)

def find_match_winner(match: SingleGame) -> Team:
    if match.home_goals > match.away_goals:
        return match.home
    else:
        return match.away

@route
def index(state: State) -> Page:
    return Page(state, [
        "Welcome to the Win Simulator.\n",
        "This is the Home Page.\n",
        "This site will simulate soccer games of your choosing for you.\n",
        "Click get started and you will be asked whether you want to do a Single Game, Round Robin, or Knockout Round.\n",
        "If you want to do a Single Game, you will enter in 2 teams and their statistics for the season.\n",
        "If you want to do a Round Robin, you will enter in 4-6 teams and their statistics for the season.\n",
        "If you want to do a Knockout Round, you will either enter in 4 teams or 8 teams and the statistics for the season.\n",
        "Good Luck!\n",
        Button("Get Started", "clicked_get_started"),
    ])


@route
def clicked_get_started(state: State) -> Page: 
    return Page(state, [
        "This is the Mode Selection Screen.\n",
        SelectBox("selected_mode", ["Single Game", "Round Robin", "Knockout Bracket"], ""),
        Button("Submit", "submitted_game_choice"),
   ])

@route
def submitted_game_choice(state: State, selected_mode: str) -> Page:
   if selected_mode == "Single Game":
       return Page(state, [
        Header("Single Game Mode"),
       "Enter information for both teams",
        
        Header("Home Team",2),
        "Team Name:",
        TextBox("home_name",""),
        "Average Goals Scored:",
        TextBox("home_scored", "0"),
        "Average Goals Conceded",
        TextBox("home_conceded","0"),
        "League:",
        SelectBox("home_league", LEAGUE_NAMES, LEAGUE_NAMES[0]),
        
        Header("Away Team",2),
        "Team Name:",
        TextBox("away_name",""),
        "Average Goals Scored:",
        TextBox("away_scored", "0"),
        "Average Goals Conceded",
        TextBox("away_conceded","0"),
        "League:",
        SelectBox("away_league", LEAGUE_NAMES, LEAGUE_NAMES[0]),
        
        Button("Submit Teams", "entered_single_game_teams")
       ])
   elif selected_mode == "Round Robin":
       return Page(state, [
        Header("Round Robin", 1),
        "On the next page, there will be 3 boxes per team.\n",
        "You will enter in your team's name, average goals per game, and average goals conceded per game respectively into those 3 boxes.\n",
        "You will do this for every team in your round robin.\n",
        
        "How many teams would you like to enter?",
        Button("4 Teams", "round_robin_four"),
        Button("5 Teams", "round_robin_five"),
        Button("6 Teams", "round_robin_six"),
       ])
   elif selected_mode == "Knockout Bracket":
       return Page(state, [
        Header("Knockout Bracket",1),
        "How many teams would you like to enter?",
        Button("4 Teams", "knockout_four"),
        Button("8 Teams", "knockout_eight"),
       ])
    

@route
def entered_single_game_teams(state: State,
    home_name: str,
    home_scored: float,
    home_conceded: float,
    home_league: str,
    away_name: str,
    away_scored: float,
    away_conceded: float,
    away_league: str,
                              
) -> Page:
    
    home_team = make_team(home_name, home_scored, home_conceded, home_league)
    
    away_team = make_team(away_name, away_scored, away_conceded, away_league)
    
    winner = simulate_game(home_team, away_team)
        
    if winner == home_team:
        loser = away_team
    else:
        loser = home_team
        
    score = make_score(winner, loser)

    if winner == home_team:
            home_goals = score[0]
            away_goals = score[1]
    else:
            home_goals = score[1]
            away_goals = score[0]
            
    return Page(state, [
        Header("Match Result", 1),
        home_team.name + " " + str(home_goals)
        + " - " + str(away_goals) + " " + away_team.name,
        Button("Play Again", "index")
    ])

@route
def round_robin_four(state: State) -> Page:
    
    return Page(state, [
        Header("Enter Your Four Teams", 1),
        
        Header("Team 1", 2),
        TextBox("team1_name", ""),
        TextBox("team1_scored", "0"),
        TextBox("team1_conceded", "0"),
        SelectBox("team1_league", LEAGUE_NAMES, LEAGUE_NAMES[0]),
        Header("Team 2", 2),
        TextBox("team2_name", ""),
        TextBox("team2_scored", "0"),
        TextBox("team2_conceded", "0"),
        SelectBox("team2_league", LEAGUE_NAMES, LEAGUE_NAMES[0]),
        
        Header("Team 3", 2),
        TextBox("team3_name", ""),
        TextBox("team3_scored", "0"),
        TextBox("team3_conceded", "0"),
        SelectBox("team3_league", LEAGUE_NAMES, LEAGUE_NAMES[0]),
        
        Header("Team 4", 2),
        TextBox("team4_name", ""),
        TextBox("team4_scored", "0"),
        TextBox("team4_conceded", "0"),
        SelectBox("team4_league", LEAGUE_NAMES, LEAGUE_NAMES[0]),
        
        Button("Submit Teams", "entered_round_robin_four")
    ])
    
@route
def round_robin_five(state: State) -> Page:
    return Page(state, [
        Header("Enter Your Five Teams", 1),
        
        Header("Team 1", 2),
        TextBox("team1_name", ""),
        TextBox("team1_scored", "0"),
        TextBox("team1_conceded", "0"),
        SelectBox("team1_league", LEAGUE_NAMES, LEAGUE_NAMES[0]),
        
        Header("Team 2", 2),
        TextBox("team2_name", ""),
        TextBox("team2_scored", "0"),
        TextBox("team2_conceded", "0"),
        SelectBox("team2_league", LEAGUE_NAMES, LEAGUE_NAMES[0]),
        
        Header("Team 3", 2),
        TextBox("team3_name", ""),
        TextBox("team3_scored", "0"),
        TextBox("team3_conceded", "0"),
        SelectBox("team3_league", LEAGUE_NAMES, LEAGUE_NAMES[0]),
        
        Header("Team 4", 2),
        TextBox("team4_name", ""),
        TextBox("team4_scored", "0"),
        TextBox("team4_conceded", "0"),
        SelectBox("team4_league", LEAGUE_NAMES, LEAGUE_NAMES[0]),
        
        Header("Team 5", 2),
        TextBox("team5_name", ""),
        TextBox("team5_scored", "0"),
        TextBox("team5_conceded", "0"),
        SelectBox("team5_league", LEAGUE_NAMES, LEAGUE_NAMES[0]),
        
        Button("Submit Teams", "entered_round_robin_five")
    ])

@route
def round_robin_six(state: State) -> Page:
    return Page(state, [
        Header("Enter Your Six Teams", 1),
        
        Header("Team 1", 2),
        TextBox("team1_name", ""),
        TextBox("team1_scored", "0"),
        TextBox("team1_conceded", "0"),
        SelectBox("team1_league", LEAGUE_NAMES, LEAGUE_NAMES[0]),
        
        Header("Team 2", 2),
        TextBox("team2_name", ""),
        TextBox("team2_scored", "0"),
        TextBox("team2_conceded", "0"),
        SelectBox("team2_league", LEAGUE_NAMES, LEAGUE_NAMES[0]),
        
        Header("Team 3", 2),
        TextBox("team3_name", ""),
        TextBox("team3_scored", "0"),
        TextBox("team3_conceded", "0"),
        SelectBox("team3_league", LEAGUE_NAMES, LEAGUE_NAMES[0]),
        
        Header("Team 4", 2),
        TextBox("team4_name", ""),
        TextBox("team4_scored", "0"),
        TextBox("team4_conceded", "0"),
        SelectBox("team4_league", LEAGUE_NAMES, LEAGUE_NAMES[0]),
        
        Header("Team 5", 2),
        TextBox("team5_name", ""),
        TextBox("team5_scored", "0"),
        TextBox("team5_conceded", "0"),
        SelectBox("team5_league", LEAGUE_NAMES, LEAGUE_NAMES[0]),
        
        Header("Team 6", 2),
        TextBox("team6_name", ""),
        TextBox("team6_scored", "0"),
        TextBox("team6_conceded", "0"),
        SelectBox("team6_league", LEAGUE_NAMES, LEAGUE_NAMES[0]),
        
        Button("Submit Teams", "entered_round_robin_six")
    ])


@route
def entered_round_robin_four(
    state: State,
    team1_name: str,
    team1_scored: float,
    team1_conceded: float,
    team1_league: str,
    team2_name: str,
    team2_scored: float,
    team2_conceded: float,
    team2_league: str,
    team3_name: str,
    team3_scored: float,
    team3_conceded: float,
    team3_league: str,
    team4_name: str,
    team4_scored: float,
    team4_conceded: float,
    team4_league: str
) -> Page:

    teams = []

    teams.append(make_team(team1_name, team1_scored, team1_conceded, team1_league))
    teams.append(make_team(team2_name, team2_scored, team2_conceded, team2_league))
    teams.append(make_team(team3_name, team3_scored, team3_conceded, team3_league))
    teams.append(make_team(team4_name, team4_scored, team4_conceded, team4_league))

    return start_round_robin(state, teams)

@route
def entered_round_robin_five(
    state: State,
    team1_name: str,
    team1_scored: float,
    team1_conceded: float,
    team1_league: str,
    team2_name: str,
    team2_scored: float,
    team2_conceded: float,
    team2_league: str,
    team3_name: str,
    team3_scored: float,
    team3_conceded: float,
    team3_league: str,
    team4_name: str,
    team4_scored: float,
    team4_conceded: float,
    team4_league: str,
    team5_name: str,
    team5_scored: float,
    team5_conceded: float,
    team5_league: str
) -> Page:

    teams = []

    teams.append(make_team(team1_name, team1_scored, team1_conceded, team1_league))
    teams.append(make_team(team2_name, team2_scored, team2_conceded, team2_league))
    teams.append(make_team(team3_name, team3_scored, team3_conceded, team3_league))
    teams.append(make_team(team4_name, team4_scored, team4_conceded, team4_league))
    teams.append(make_team(team5_name, team5_scored, team5_conceded, team5_league))

    return start_round_robin(state, teams)

@route
def entered_round_robin_six(
    state: State,
    team1_name: str,
    team1_scored: float,
    team1_conceded: float,
    team1_league: str,
    team2_name: str,
    team2_scored: float,
    team2_conceded: float,
    team2_league: str,
    team3_name: str,
    team3_scored: float,
    team3_conceded: float,
    team3_league: str,
    team4_name: str,
    team4_scored: float,
    team4_conceded: float,
    team4_league: str,
    team5_name: str,
    team5_scored: float,
    team5_conceded: float,
    team5_league: str,
    team6_name: str,
    team6_scored: float,
    team6_conceded: float,
    team6_league: str
) -> Page:

    teams = []

    teams.append(make_team(team1_name, team1_scored, team1_conceded, team1_league))
    teams.append(make_team(team2_name, team2_scored, team2_conceded, team2_league))
    teams.append(make_team(team3_name, team3_scored, team3_conceded, team3_league))
    teams.append(make_team(team4_name, team4_scored, team4_conceded, team4_league))
    teams.append(make_team(team5_name, team5_scored, team5_conceded, team5_league))
    teams.append(make_team(team6_name, team6_scored, team6_conceded, team6_league))

    return start_round_robin(state, teams)

@route
def round_robin_results(state: State) -> Page:
    teams = state.round_robin_teams
    
    matches = simulate_round_robin(teams)
    
    standings = calculate_standings(teams,matches)
    standings = sort_standings(standings)
    
    content = [Header("Round Robin Teams", 1)]
    
    content.append(Header("Match Results", 2))
    
    for match in matches:
        content.append(
            match.home.name + " "
            + str(match.home_goals) + " - "
            + str(match.away_goals) + " "
            + match.away.name
        )
    
    content.append(Header("League Table", 2))
    
    for standing in standings:
        content.append(
            standing.team.name
            + " | Points: " + str(standing.points)
            + " | GD: " + str(calculate_goal_difference(standing))
        )
        
    content.append(Button("Play Again", "index"))
    
    return Page(state, content)

@route
def entered_round_robin_teams(state: State) -> Page: 
    return Page(state, [
        "This will show the result of your round robin.\n",
        Button("Play Again", "index")
   ])

@route
def knockout_four(state: State) -> Page:
    return Page(state, [
        Header("Enter 4 Teams", 1),
        "You will enter teams next",
        
        "Would you like to display match scores?",
    CheckBox("show_scores", True),
        
        Header("Team 1", 2),
        "Team Name",
        TextBox("team1_name", ""),
        "Average Goals Scored",
        TextBox("team1_scored", "0"),
        "Average Goals Conceded",
        TextBox("team1_conceded", "0"),
        "Real League",
        SelectBox("team1_league", LEAGUE_NAMES, LEAGUE_NAMES[0]),
        
        Header("Team 2", 2),
        "Team Name",
        TextBox("team2_name", ""),
        "Average Goals Scored",
        TextBox("team2_scored", "0"),
        "Average Goals Conceded",
        TextBox("team2_conceded", "0"),
        "Real League",
        SelectBox("team2_league", LEAGUE_NAMES, LEAGUE_NAMES[0]),
        
        Header("Team 3", 2),
        "Team Name",
        TextBox("team3_name", ""),
        "Average Goals Scored",
        TextBox("team3_scored", "0"),
        "Average Goals Conceded",
        TextBox("team3_conceded", "0"),
        "Real League",
        SelectBox("team3_league", LEAGUE_NAMES, LEAGUE_NAMES[0]),
        
        Header("Team 4", 2),
        "Team Name",
        TextBox("team4_name", ""),
        "Average Goals Scored",
        TextBox("team4_scored", "0"),
        "Average Goals Conceded",
        TextBox("team4_conceded", "0"),
        "Real League",
        SelectBox("team4_league", LEAGUE_NAMES, LEAGUE_NAMES[0]),
        
        Button("Submit Teams", "entered_knockout_four")
    ])


@route
def knockout_eight(state: State) -> Page:
    return Page(state, [
        Header("Enter 8 Teams", 1),
        "You will enter teams next",
        
        "Would you like to display match scores?",
    CheckBox("show_scores", True),
        
         Header("Team 1", 2),
        "Team Name",
        TextBox("team1_name", ""),
        "Average Goals Scored",
        TextBox("team1_scored", "0"),
        "Average Goals Conceded",
        TextBox("team1_conceded", "0"),
        "Real League",
        SelectBox("team1_league", LEAGUE_NAMES, LEAGUE_NAMES[0]),
        
        Header("Team 2", 2),
        "Team Name",
        TextBox("team2_name", ""),
        "Average Goals Scored",
        TextBox("team2_scored", "0"),
        "Average Goals Conceded",
        TextBox("team2_conceded", "0"),
        "Real League",
        SelectBox("team2_league", LEAGUE_NAMES, LEAGUE_NAMES[0]),
        
        Header("Team 3", 2),
        "Team Name",
        TextBox("team3_name", ""),
        "Average Goals Scored",
        TextBox("team3_scored", "0"),
        "Average Goals Conceded",
        TextBox("team3_conceded", "0"),
        "Real League",
        SelectBox("team3_league", LEAGUE_NAMES, LEAGUE_NAMES[0]),
        
        Header("Team 4", 2),
        "Team Name",
        TextBox("team4_name", ""),
        "Average Goals Scored",
        TextBox("team4_scored", "0"),
        "Average Goals Conceded",
        TextBox("team4_conceded", "0"),
        "Real League",
        SelectBox("team4_league", LEAGUE_NAMES, LEAGUE_NAMES[0]),
        
        Header("Team 5", 2),
        "Team Name",
        TextBox("team5_name", ""),
        "Average Goals Scored",
        TextBox("team5_scored", "0"),
        "Average Goals Conceded",
        TextBox("team5_conceded", "0"),
        "Real League",
        SelectBox("team5_league", LEAGUE_NAMES, LEAGUE_NAMES[0]),
        
        Header("Team 6", 2),
        "Team Name",
        TextBox("team6_name", ""),
        "Average Goals Scored",
        TextBox("team6_scored", "0"),
        "Average Goals Conceded",
        TextBox("team6_conceded", "0"),
        "Real League",
        SelectBox("team6_league", LEAGUE_NAMES, LEAGUE_NAMES[0]),
        
        Header("Team 7", 2),
        "Team Name",
        TextBox("team7_name", ""),
        "Average Goals Scored",
        TextBox("team7_scored", "0"),
        "Average Goals Conceded",
        TextBox("team7_conceded", "0"),
        "Real League",
        SelectBox("team7_league", LEAGUE_NAMES, LEAGUE_NAMES[0]),
        
        Header("Team 8", 2),
        "Team Name",
        TextBox("team8_name", ""),
        "Average Goals Scored",
        TextBox("team8_scored", "0"),
        "Average Goals Conceded",
        TextBox("team8_conceded", "0"),
        "Real League",
        SelectBox("team8_league", LEAGUE_NAMES, LEAGUE_NAMES[0]),
        
        Button("Submit Teams", "entered_knockout_eight")
    ])

@route
def entered_knockout_four(
    state: State,
    team1_name: str,
    team1_scored: float,
    team1_conceded: float,
    team1_league: str,
    team2_name: str,
    team2_scored: float,
    team2_conceded: float,
    team2_league: str,
    team3_name: str,
    team3_scored: float,
    team3_conceded: float,
    team3_league: str,
    team4_name: str,
    team4_scored: float,
    team4_conceded: float,
    team4_league: str,
    show_scores: bool
) -> Page:
    
    team1 = make_team(team1_name, team1_scored, team1_conceded, team1_league)
    team2 = make_team(team2_name, team2_scored, team2_conceded, team2_league)
    team3 = make_team(team3_name, team3_scored, team3_conceded, team3_league)
    team4 = make_team(team4_name, team4_scored, team4_conceded, team4_league)
    
    teams = [team1, team2, team3, team4]
    
    state.knockout_teams = teams
    state.show_knockout_scores = show_scores
    
    return Page(state, [
        Header("Knockout Teams", 1),
        "Your four teams have been entered!",
        Button("Start Tournament", "start_knockout_four")
    ])
@route
def entered_knockout_eight(
    state: State,
    team1_name: str,
    team1_scored: float,
    team1_conceded: float,
    team1_league: str,
    team2_name: str,
    team2_scored: float,
    team2_conceded: float,
    team2_league: str,
    team3_name: str,
    team3_scored: float,
    team3_conceded: float,
    team3_league: str,
    team4_name: str,
    team4_scored: float,
    team4_conceded: float,
    team4_league: str,
    team5_name: str,
    team5_scored: float,
    team5_conceded: float,
    team5_league: str,
    team6_name: str,
    team6_scored: float,
    team6_conceded: float,
    team6_league: str,
    team7_name: str,
    team7_scored: float,
    team7_conceded: float,
    team7_league: str,
    team8_name: str,
    team8_scored: float,
    team8_conceded: float,
    team8_league: str,
    show_scores: bool
) -> Page:
    
    team1 = make_team(team1_name, team1_scored, team1_conceded, team1_league)
    team2 = make_team(team2_name, team2_scored, team2_conceded, team2_league)
    team3 = make_team(team3_name, team3_scored, team3_conceded, team3_league)
    team4 = make_team(team4_name, team4_scored, team4_conceded, team4_league)
    team5 = make_team(team5_name, team5_scored, team5_conceded, team5_league)
    team6 = make_team(team6_name, team6_scored, team6_conceded, team6_league)
    team7 = make_team(team7_name, team7_scored, team7_conceded, team7_league)
    team8 = make_team(team8_name, team8_scored, team8_conceded, team8_league)
    
    teams = [team1, team2, team3, team4, team5, team6, team7, team8]
    
    state.knockout_teams = teams
    state.show_knockout_scores = show_scores
    
    return Page(state, [
        Header("Knockout Teams", 1),
        "Your eight teams have been entered!",
        Button("Start Tournament", "start_knockout_eight")
    ])

@route
def start_knockout_eight(state: State) -> Page:
    teams = state.knockout_teams

    match1 = simulate_knockout_match(teams[0], teams[7])
    match2 = simulate_knockout_match(teams[1], teams[6])
    match3 = simulate_knockout_match(teams[2], teams[5])
    match4 = simulate_knockout_match(teams[3], teams[4])

    winners = [
        find_match_winner(match1),
        find_match_winner(match2),
        find_match_winner(match3),
        find_match_winner(match4)
    ]

    state.knockout_teams = winners

    content = [
        Header("Knockout Quarterfinals", 1)
    ]

    if state.show_knockout_scores:
        content.append(
            match1.home.name + " " + str(match1.home_goals) +
            " - " + str(match1.away_goals) + " " + match1.away.name
        )
        content.append(
            match2.home.name + " " + str(match2.home_goals) +
            " - " + str(match2.away_goals) + " " + match2.away.name
        )
        content.append(
            match3.home.name + " " + str(match3.home_goals) +
            " - " + str(match3.away_goals) + " " + match3.away.name
        )
        content.append(
            match4.home.name + " " + str(match4.home_goals) +
            " - " + str(match4.away_goals) + " " + match4.away.name
        )
    else:
        content.append(match1.home.name + " vs " + match1.away.name)
        content.append(match2.home.name + " vs " + match2.away.name)
        content.append(match3.home.name + " vs " + match3.away.name)
        content.append(match4.home.name + " vs " + match4.away.name)

    content.append(Header("Quarterfinal Winners", 2))

    for winner in winners:
        content.append(winner.name)

    content.append(
        Button("Continue to Semifinals", "start_knockout_four")
    )

    return Page(state, content)

@route
def start_knockout_four(state: State) -> Page:
    teams = state.knockout_teams
    
    match1 = simulate_knockout_match(teams[0], teams[3])
    match2 = simulate_knockout_match(teams[1], teams[2])
    
    if match1.home_goals > match1.away_goals:
        winner1 = match1.home
    else:
        winner1 = match1.away
    
    if match2.home_goals > match2.away_goals:
        winner2 = match2.home
    else: winner2 = match2.away
    
    state.knockout_winners = [winner1, winner2]
    
    content = [Header("Knockout Semifinals", 1)]
               
    if state.show_knockout_scores:
        content.append(Header("Semifinal 1", 2))
               
        content.append(match1.home.name + " " +
                       str(match1.home_goals) + " - " +
                       str(match1.away_goals) + " " +
                       match1.away.name)
               
        content.append(Header("Semifinal 2", 2))
        
        content.append(match2.home.name + " " +
                       str(match2.home_goals) + " - " +
                       str(match2.away_goals) + " " +
                       match2.away.name
                    )
    else:
        content.append("Semifinal 1")
        content.append(
            match1.home.name + " vs " + match1.away.name
        )
        content.append("Semifinal 2")
        content.append(match2.home.name + " vs" + match2.away.name)
        
    content.append("Finalists: " + winner1.name + " and " + winner2.name)
    
    content.append(
        Button("Continue to Final", "knockout_final"))
    return Page(state,content)
                       
@route
def knockout_final(state: State) -> Page:
    finalists = state.knockout_winners
    
    final_match = simulate_knockout_match(finalists[0], finalists[1])
    
    if final_match.home_goals > final_match.away_goals:
        champion = final_match.home
    else:
        champion = final_match.away
        
    content = [Header("Final", 1)]
    
    if state.show_knockout_scores:
        content.append(
            final_match.home.name + " " +
            str(final_match.home_goals) + " - " +
            str(final_match.away_goals) + " " +
            final_match.away.name
        )
    else:
        content.append(final_match.home.name + " vs " + final_match.away.name)
    content.append(Header("Champion!", 2))
    content.append(champion.name)
    
    return Page(state,content)

@route
def entered_knockout_bracket_teams(state: State) -> Page:
    return Page(state, [
        "This will show the result of your knockout bracket.\n",
        Button("Play Again", "index")
   ])
  
start_server(State([], [], True, []))
