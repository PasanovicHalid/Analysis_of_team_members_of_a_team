import re
import pandas as pd
import json

def generate_prompt_for_commit_consistancy(commits_df):
    commit_prompts = []

    merge_commit_pattern = re.compile(r'^(Merge (pull request|branch)|merge)', re.IGNORECASE)

    count_of_commits_for_each_user = commits_df['commit.author.name'].value_counts()

    for i, row in commits_df.iterrows():

        #remove commits that are merge commits
        # check if the commit message contains all possible merge messages
        if merge_commit_pattern.match(row['commit.message']):
            continue

        commit_prompt = f'{i + 1}. Commit "{row["commit.message"]}" has been made by "{row["commit.author.name"]}" at "{row["commit.author.date"]}".\n'
        commit_prompts.append(commit_prompt)

    prompts = []

    for i in range(0, len(commit_prompts), 50):
        prompt = f"""The following commits have been made:\n
{'\n'.join(commit_prompts[i:i+50])}
    """
        prompts.append(prompt)

    prompt_for_count = []

    for user, count in count_of_commits_for_each_user.items():
        prompt_for_count.append(f'User "{user}" has made {count} commits.\n')

    prompts.append(f"""Overview of commits:
Number of commits: {len(commits_df)}
Number of commits by each user:
{"\n".join(prompt_for_count)}
""")

    return prompts

def generate_df_for_commit_consistancy(commits_df):
    result_df = pd.DataFrame(columns=['commit.message', 'commit.author.name', 'commit.author.date'])

    for _, row in commits_df.iterrows():
        result_df = pd.concat([result_df, pd.DataFrame([[
            row['commit.message'],
            row['commit.author.name'],
            row['commit.author.date']
        ]], columns=['commit.message', 'commit.author.name', 'commit.author.date'])], ignore_index=True)

    return result_df

# Generare prompt for pull request handling
# Describes who made the pull request, when it was made, and the comments made on it. when it was merged...
def generate_prompt_for_pull_request_handling(pull_df, comments_df, review_comments_df):
    pull_prompts = []
    number_of_pull_requests_without_comments = 0
    number_of_pull_requests_that_are_quiclky_merged = 0
    number_of_pull_requests_without_assignees = 0

    count_of_pull_request_for_each_user = pull_df['user.login'].value_counts()
    count_of_comments_and_review_comments_for_each_user = pd.concat([comments_df['user.login'].value_counts(), review_comments_df['user.login'].value_counts()], axis=1).sum(axis=1)

    pull_df['created_at'] = pd.to_datetime(pull_df['created_at'])
    pull_df['merged_at'] = pd.to_datetime(pull_df['merged_at'])

    for _, row in pull_df.iterrows():
        pull_prompt = f'Pull request "{row["title"]}" has been made by "{row["user.login"]}" at "{row["created_at"]}".\n'
        pull_prompt += f'Description: "{row["body"]}".\n'
        has_comments = False
        has_review_comments = False
        has_assignees = True

        if row['created_at'] - row['merged_at'] < pd.Timedelta('5 minutes'):
            number_of_pull_requests_that_are_quiclky_merged += 1

        if row['assignees'] == [] and row['requested_reviewers'] == [] and row['requested_teams'] == []:
            has_assignees = False
            number_of_pull_requests_without_assignees += 1

        if(comments_df.empty):
            pull_prompt += f'This pull request has no comments.\n'
        else:
            comments = comments_df[comments_df['pull_request_id'] == row['id']]

            if not comments.empty:
                has_comments = True

            for _, comment in comments.iterrows():
                pull_prompt += f'Comment: "{comment["body"]}" by "{comment["user.login"]}" at "{comment["created_at"]}".\n'
        
        if(review_comments_df.empty):
            pull_prompt += f'This pull request has no review comments.\n'
        else:
            review_comments = review_comments_df[review_comments_df['pull_request_id'] == row['id']]

            if not review_comments.empty:
                has_review_comments = True

            for _, review_comment in review_comments.iterrows():
                pull_prompt += f'Review comment: "{review_comment["body"]}" by "{review_comment["user.login"]}" at "{review_comment["created_at"]}".\n'
        
        if row['merged_at'] != None:
            pull_prompt += f'This pull request was merged at "{row["merged_at"]}".\n'
            pull_prompt += f'Time to merge: {row["merged_at"] - row["created_at"]}\n'
        else:
            pull_prompt += f'This pull request was not merged.\n'

        if not has_assignees:
            pull_prompt += f'This pull request has no assignees.\n'
        else:
            if row['assignees'] != None and row['assignees'] != []:
                pull_prompt += f'This pull request has assignees: {", ".join([assignee["login"] for assignee in row["assignees"]])}.\n'
            if row['requested_reviewers'] != None and row['requested_reviewers'] != []:
                pull_prompt += f'This pull request has requested reviewers: {", ".join([reviewer["login"] for reviewer in row["requested_reviewers"]])}.\n'
            if row['requested_teams'] != None and row['requested_teams'] != []:
                pull_prompt += f'This pull request has requested teams: {", ".join([team["name"] for team in row["requested_teams"]])}.\n'

        if not has_comments and not has_review_comments:
            number_of_pull_requests_without_comments += 1
            continue

        pull_prompts.append(f"""{pull_prompt}\n
{"-" * 50}""")

    prompts = []

    for i in range(0, len(pull_prompts), 15):
        prompt = f"""Analyze the following pull requests have been made:\n
{'\n'.join(pull_prompts[i:i+15])}
    """
        prompts.append(prompt)

    prompt_for_comments = []
    prompt_for_count_of_pull_request_for_each_user = []

    for user, count in count_of_pull_request_for_each_user.items():
        prompt_for_count_of_pull_request_for_each_user.append(f'User "{user}" has made {count} pull requests.\n')

    for user, count in count_of_comments_and_review_comments_for_each_user.items():
        prompt_for_comments.append(f'User "{user}" has made {count} comments and review comments.\n')        

    prompts.append(f"""Overview of pull requests:
Number of pull requests: {len(pull_df)}       
Number of pull requests that are merged under 5 minutes: {number_of_pull_requests_that_are_quiclky_merged}
Number of pull requests without comments: {number_of_pull_requests_without_comments}
Number of pull requests without assignees: {number_of_pull_requests_without_assignees}
{"\n".join(prompt_for_count_of_pull_request_for_each_user)}
{"\n".join(prompt_for_comments)}
""")  

    return prompts

def generate_df_for_pull_request_handling(pull_df, comments_df, review_comments_df):
    result_df = pd.DataFrame(columns=['title', 'user.login', 'user.id', 'created_at', 'body', 'merged_at', "number_of_comments" , "number_of_review_comments"])

    for _, row in pull_df.iterrows():
        number_of_comments = 0
        if not comments_df.empty:
            comments = comments_df[comments_df['pull_request_id'] == row['id']]
            number_of_comments = len(comments)

        number_of_review_comments = 0
        if not review_comments_df.empty:
            review_comments = review_comments_df[review_comments_df['pull_request_id'] == row['id']]
            number_of_review_comments = len(review_comments)

        result_df = pd.concat([result_df, pd.DataFrame([[
            row['title'],
            row['user.login'],
            row['user.id'],
            row['created_at'],
            row['body'],
            row['merged_at'],
            number_of_comments,
            number_of_review_comments,
        ]], columns=['title', 'user.login', 'user.id', 'created_at', 'body', 'merged_at', "number_of_comments" ,"number_of_review_comments"])], ignore_index=True)

    return result_df

