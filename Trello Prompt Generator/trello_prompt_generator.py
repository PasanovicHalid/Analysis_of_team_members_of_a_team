import pandas as pd
import trello_api as trello
import trello_action_handler as action_handlers
import helpers as helpers

BOARD_NAME = 'Tim 9'

def get_trello_cards_df(board_id):
    cards = trello.get_trello_cards(board_id)
    df = pd.json_normalize(cards)
    return df

def get_actions(cards_df):
    actions = []
    for _, row in cards_df.iterrows():
        card_id = row['id']
        card_actions = trello.get_actions_for_card(card_id)
        for action in card_actions:
            action['card_id'] = card_id
            actions.append(action)
    return actions

def get_actions_df(cards_df):
    actions = get_actions(cards_df)
    df = pd.json_normalize(actions)
    return df

def get_members_df(board_id):
    members = trello.get_members(board_id)
    df = pd.json_normalize(members)
    return df

def write_prompt_to_file(prompt, filename):
    with open(filename, 'w') as f:
        f.write(prompt)

board_id = trello.get_board_id(BOARD_NAME)
cards_df = get_trello_cards_df(board_id)
actions_df = get_actions_df(cards_df)
members_df = get_members_df(board_id)

actions_df['date'] = pd.to_datetime(actions_df['date']) #convert date to datetime
actions_df = actions_df.sort_values('date') #sort by date
actions_df = actions_df.reset_index(drop=True) #reset index

actions_with_cards = pd.merge(actions_df, cards_df[['id', 'name', 'idMembers']], left_on='card_id', right_on='id', suffixes=('_action', '_card'))

actions_for_specific_users_sorted = actions_with_cards.groupby('memberCreator.id').apply(
    lambda x: sorted(list(zip(x['date'], x['id_action'])), key=lambda y: y[0])

).reset_index(name='date_id_action_tuples')

#Get data where 
actions_that_move_cards = actions_with_cards[(actions_with_cards['type'] == 'updateCard') & (actions_with_cards['data.listAfter.id'] != None)]
actions_that_move_cards = actions_that_move_cards.reset_index(drop=True)

actions_that_update_cards = actions_with_cards[(actions_with_cards['type'] == 'updateCard') & (actions_with_cards['data.listAfter.id'] == None)]
actions_that_update_cards = actions_that_update_cards.reset_index(drop=True)

history_df = action_handlers.generate_move_cards_df(actions_that_move_cards, members_df, actions_for_specific_users_sorted)
consistancy_df = action_handlers.generate_action_consistancy_df(actions_for_specific_users_sorted, members_df)


history_df.to_csv('history_df.csv', index=False)
consistancy_df.to_csv('consistancy_df.csv', index=False)

history_of_actions_prompt = action_handlers.generate_prompt_for_actions_that_move_cards(actions_that_move_cards, members_df, actions_for_specific_users_sorted)
consistancy_of_actions_prompt = action_handlers.generate_prompt_for_action_consistancy_for_users(actions_for_specific_users_sorted, members_df)

final_prompt = f"""
This is the complete trello history of the team. It includes the history of actions that move cards and the consistancy of actions for each team member.

History of actions that move cards:

{history_of_actions_prompt}

Consistancy of actions:

{consistancy_of_actions_prompt}
"""

write_prompt_to_file(final_prompt, 'trello_prompt.txt')





