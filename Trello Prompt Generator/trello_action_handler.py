import pandas as pd

def _extract_names_of_members(members_df, members_ids):
    members_names = []
    for member_id in members_ids:
        member_name = members_df[members_df['id'] == member_id]['fullName'].values[0]
        members_names.append(member_name)
    return members_names

def _get_difference_in_time_between_actions(actions_for_specific_users_sorted):
    time_diff = {}
    for _, row in actions_for_specific_users_sorted.iterrows():
        date_id_tuples = row['date_id_action_tuples']
        for i in range(1, len(date_id_tuples)):
            time_diff[date_id_tuples[i][1]] = date_id_tuples[i][0] - date_id_tuples[i-1][0]
    return time_diff

def _time_to_string(time):
    total_seconds = int(time.total_seconds())
    days, remainder_seconds = divmod(total_seconds, 86400)
    hours, remainder_seconds = divmod(remainder_seconds, 3600)
    minutes, remainder_seconds = divmod(remainder_seconds, 60)
    return f'{days} days, {hours} hours, {minutes} minutes, {remainder_seconds} seconds'
    
# for each user, return tupple of time difference between actions and action id
def _get_difference_in_time_between_actions_for_specific_users(actions_for_specific_users_sorted):
    time_diffs = {}
    for _, row in actions_for_specific_users_sorted.iterrows():
        time_diffs[row['memberCreator.id']] = []
        date_id_tuples = row['date_id_action_tuples']
        for i in range(1, len(date_id_tuples)):
            time_diffs[row['memberCreator.id']].append((date_id_tuples[i][0] - date_id_tuples[i-1][0], date_id_tuples[i][1]))
        
    return time_diffs

def generate_prompt_for_action_consistancy_for_users(actions_for_specific_users_sorted, members_df):
    time_diffs = _get_difference_in_time_between_actions_for_specific_users(actions_for_specific_users_sorted)
    action_prompts = []

    for _, row in actions_for_specific_users_sorted.iterrows():
        user_id = row['memberCreator.id']
        user_name = members_df[members_df['id'] == row['memberCreator.id']]['fullName'].values[0]
        time_diffs_for_user = time_diffs[user_id]

        user_prompt = f'User "{user_name}" has performed the following actions:\n'

        for time_diff, _ in time_diffs_for_user:
            user_prompt += f'Time difference between this action and the previous one is "{_time_to_string(time_diff)}".\n'
        
        action_prompts.append(user_prompt)

    prompt = f"""The following actions have been performed:\n
{'\n'.join(action_prompts)}
    """

    return prompt

def generate_action_consistancy_df(actions_for_specific_users_sorted, members_df):
    time_diffs = _get_difference_in_time_between_actions_for_specific_users(actions_for_specific_users_sorted)
    result_df = pd.DataFrame(columns=['user_name', 'time_diff'])

    for _, row in actions_for_specific_users_sorted.iterrows():
        user_id = row['memberCreator.id']
        user_name = members_df[members_df['id'] == row['memberCreator.id']]['fullName'].values[0]
        time_diffs_for_user = time_diffs[user_id]

        for time_diff, _ in time_diffs_for_user:
            result_df = pd.concat([result_df, pd.DataFrame([[user_name, time_diff]], columns=result_df.columns)], ignore_index=True)

    return result_df


def generate_prompt_for_actions_that_move_cards(actions_that_move_cards_pd, members_df, actions_for_specific_users_sorted):
    time_diffs = _get_difference_in_time_between_actions(actions_for_specific_users_sorted)
    action_prompts = []

    for _, row in actions_that_move_cards_pd.iterrows():
        card_name = row['name']
        list_before = row['data.listBefore.name']
        list_after = row['data.listAfter.name']
        moved_by = row['memberCreator.fullName']
        card_asignees = row['idMembers']
        date = row['date']
        card_asignees_names = _extract_names_of_members(members_df, card_asignees)
        card_asignees_names = ', '.join(card_asignees_names)
        time_diff = time_diffs.get(row['id_action'], pd.Timedelta(seconds=0))
        action_prompts.append(f'Card with name: "{card_name}" moved from "{list_before}" to "{list_after}" by "{moved_by}" on "{date.strftime("%Y-%m-%d %H:%M:%S")}". The task is assignet to "{card_asignees_names}". Time difference between this action and the previous one of the member performed this action is "{_time_to_string(time_diff)}".')

    prompt = f"""The following actions have been performed:\n
{'\n'.join(action_prompts)}
    """

    return prompt

def generate_move_cards_df(actions_that_move_cards_pd, members_df, actions_for_specific_users_sorted):
    time_diffs = _get_difference_in_time_between_actions(actions_for_specific_users_sorted)
    result_df = pd.DataFrame(columns=['card_name', 'list_before', 'list_after', 'moved_by', 'date', 'card_asignees', 'time_diff'])

    for _, row in actions_that_move_cards_pd.iterrows():
        card_name = row['name']
        list_before = row['data.listBefore.name']
        list_after = row['data.listAfter.name']
        moved_by = row['memberCreator.fullName']
        card_asignees = row['idMembers']
        date = row['date']
        card_asignees_names = _extract_names_of_members(members_df, card_asignees)
        card_asignees_names = ', '.join(card_asignees_names)
        time_diff = time_diffs.get(row['id_action'], pd.Timedelta(seconds=0))
        result_df = pd.concat([result_df, pd.DataFrame([[card_name, list_before, list_after, moved_by, date, card_asignees_names, time_diff]], columns=result_df.columns)], ignore_index=True)
    return result_df