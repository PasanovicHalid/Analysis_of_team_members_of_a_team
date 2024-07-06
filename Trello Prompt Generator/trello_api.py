import requests
import json
import os

TRELLO_API_KEY = os.environ.get('TRELLO_API_KEY')
TRELLO_API_TOKEN = os.environ.get('TRELLO_API_TOKEN')

def get_board_id(board_name):
    url = f"https://api.trello.com/1/members/me/boards?key={TRELLO_API_KEY}&token={TRELLO_API_TOKEN}"
    response = requests.request("GET", url)
    boards = json.loads(response.text)
    for board in boards:
        if board['name'] == board_name:
            return board['id']
    return None

def get_actions_for_card(card_id):
    url = f"https://api.trello.com/1/cards/{card_id}/actions?key={TRELLO_API_KEY}&token={TRELLO_API_TOKEN}"
    response = requests.request("GET", url)
    actions = json.loads(response.text)
    return actions

def get_cards(board_id):
    url = f"https://api.trello.com/1/boards/{board_id}/cards?key={TRELLO_API_KEY}&token={TRELLO_API_TOKEN}"
    response = requests.request("GET", url)
    cards = json.loads(response.text)
    return cards

def get_members(board_id):
    url = f"https://api.trello.com/1/boards/{board_id}/members?key={TRELLO_API_KEY}&token={TRELLO_API_TOKEN}"
    response = requests.request("GET", url)
    members = json.loads(response.text)
    return members

def get_trello_cards(board_id):
    cards = get_cards(board_id)
    return cards