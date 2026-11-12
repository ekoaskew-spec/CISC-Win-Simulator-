from drafter import *
from dataclasses import dataclass


@dataclass
class State:
    """
league: RealLeague 
fantasy_league_teams: Team[list] 
fantasy_league: FantasyLeague 
table: ResultsTable 
One_game: SingleGame 
    """


@route
def index(state: State) -> Page:
    return Page(state, [
        "Welcome to the Win Simulator.\n",
        "This is the Home Page.\n",
        "<Explain What site does>",
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
        "This is the Single Game Option.\n",
       "<Fields to enter 2 teams>",
        Button("Submit Teams", "entered_single_game_teams")
       ])
   elif selected_mode == "Round Robin":
       return Page(state, [
        "This is the Round Robin Option.\n",
        "<Fields to enter 4-6 teams>",
        Button("Submit Teams", "entered_round_robin_teams")
       ])
   elif selected_mode == "Knockout Bracket":
       return Page(state, [
        "This is the Knockout Bracket Option.\n",
        "<Fields to enter 4 or 8 teams>",
        Button("Submit Teams", "entered_knockout_bracket_teams")
       ]) 
    

@route
def entered_single_game_teams(state: State) -> Page:
    return Page(state, [
        "This will show the result of your single game.\n",
        Button("Play Again", "index")
    ])


@route
def entered_round_robin_teams(state: State) -> Page: 
    return Page(state, [
        "This will show the result of your round robin.\n",
        Button("Play Again", "index")
   ])

@route
def entered_knockout_bracket_teams(state: State) -> Page:
    return Page(state, [
        "This will show the result of your knockout bracket.\n",
        Button("Play Again", "index")
   ])
  
  
start_server(State())
