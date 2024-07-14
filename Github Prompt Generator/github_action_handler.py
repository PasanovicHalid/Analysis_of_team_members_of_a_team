import pandas as pd
import json

def generate_prompt_for_commit_consistancy(commits_df):
    commit_prompts = []
    for _, row in commits_df.iterrows():
        commit_prompt = f'Commit "{row["commit.message"]}" has been made by "{row["commit.author.name"]}" at "{row["commit.author.date"]}".\n'
        commit_prompts.append(commit_prompt)

    prompt = f"""The following commits have been made:\n
{'\n'.join(commit_prompts)}
    """

    return prompt

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
    for _, row in pull_df.iterrows():
        pull_prompt = f'Pull request "{row["title"]}" has been made by "{row["user.login"]}" at "{row["created_at"]}".\n'
        pull_prompt += f'Description: "{row["body"]}".\n'

        if(comments_df.empty):
            pull_prompt += f'This pull request has no comments.\n'
        else:
            comments = comments_df[comments_df['pull_request_id'] == row['id']]
            for _, comment in comments.iterrows():
                pull_prompt += f'Comment: "{comment["body"]}" by "{comment["user.login"]}" at "{comment["created_at"]}".\n'
        
        if(review_comments_df.empty):
            pull_prompt += f'This pull request has no review comments.\n'
        else:
            review_comments = review_comments_df[review_comments_df['pull_request_id'] == row['id']]
            for _, review_comment in review_comments.iterrows():
                pull_prompt += f'Review comment: "{review_comment["body"]}" by "{review_comment["user.login"]}" at "{review_comment["created_at"]}".\n'
        
        if row['merged_at'] != None:
            pull_prompt += f'This pull request was merged at "{row["merged_at"]}".\n'
        else:
            pull_prompt += f'This pull request was not merged.\n'

        pull_prompts.append(pull_prompt)

    prompt = f"""The following pull requests have been made:\n
{'\n'.join(pull_prompts)}
    """

    return prompt

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

