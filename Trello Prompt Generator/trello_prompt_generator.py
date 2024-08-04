import pandas as pd
import trello_api as trello
import trello_action_handler as action_handlers
import helpers as helpers

BOARD_NAME = 'psw'

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
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(prompt)

def create_number_of_file_for_ordering(length_of_list, index):
    order_of_10_expontents = len(str(length_of_list))

    return str(index).zfill(order_of_10_expontents)

board_id = "tHpvYHXl"
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

actions_for_cards = actions_with_cards.groupby('card_id').apply(
    lambda x: sorted(list(zip(x['date'], x['id_action'])), key=lambda y: y[0])
).reset_index(name='date_id_action_tuples')

#Get data where 
actions_that_move_cards = actions_with_cards[(actions_with_cards['type'] == 'updateCard') & (actions_with_cards['data.listAfter.id'] != None)]
actions_that_move_cards = actions_that_move_cards.reset_index(drop=True)

actions_that_update_cards = actions_with_cards[(actions_with_cards['type'] == 'updateCard') & (actions_with_cards['data.listAfter.id'] == None)]
actions_that_update_cards = actions_that_update_cards.reset_index(drop=True)

history_of_actions_prompts = action_handlers.generate_prompt_for_actions_that_move_cards(actions_that_move_cards, members_df, actions_for_cards)
consistancy_of_actions_prompt = action_handlers.generate_prompt_for_action_consistancy_for_users(actions_for_specific_users_sorted, members_df)

for i in range(len(history_of_actions_prompts)):
    write_prompt_to_file(history_of_actions_prompts[i], f'generated_files/trello_prompt_actions-{create_number_of_file_for_ordering(len(history_of_actions_prompts), i)}.txt')

final_prompt = f"""
Consistancy of actions:

{consistancy_of_actions_prompt}
"""

write_prompt_to_file(final_prompt, 'generated_files/trello_prompt_consistancy.txt')





