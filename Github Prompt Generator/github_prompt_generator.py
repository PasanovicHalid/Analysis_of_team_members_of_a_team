import pandas as pd
import github_api as github
import github_action_handler as action_handlers

GITHUB_OWNER = 'PSW-Group-3'
GITHUB_REPO = 'PSW-Projekat'

def write_prompt_to_file(prompt, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(prompt)

def get_commits_df():
    github_commits = github.get_commits(GITHUB_OWNER, GITHUB_REPO)
    df = pd.json_normalize(github_commits)
    return df

def get_pull_requests_df():
    github_pull_requests = github.get_pull_requests(GITHUB_OWNER, GITHUB_REPO)
    df = pd.json_normalize(github_pull_requests)
    return df

def get_comments_of_pull_request_and_add_to_df(pull_requests_df):
    comments = []
    for _, row in pull_requests_df.iterrows():
        comments_url = row['comments_url']
        comments_for_pull_request = github.execute_url_request(comments_url)
        for comment in comments_for_pull_request:
            comment['pull_request_id'] = row['id']
            comments.append(comment)
    comments_df = pd.json_normalize(comments)
    return comments_df

def get_review_comments_of_pull_request_and_add_to_df(pull_requests_df):
    comments = []
    for _, row in pull_requests_df.iterrows():
        comments_url = row['review_comments_url']
        comments_for_pull_request = github.execute_url_request(comments_url)
        for comment in comments_for_pull_request:
            comment['pull_request_id'] = row['id']
            comments.append(comment)
    comments_df = pd.json_normalize(comments)
    return comments_df
    
commits_df = get_commits_df()
pull_requests_df = get_pull_requests_df()
comments_df = get_comments_of_pull_request_and_add_to_df(pull_requests_df)
review_comments_df = get_review_comments_of_pull_request_and_add_to_df(pull_requests_df)

commit_consistancy_prompt = action_handlers.generate_prompt_for_commit_consistancy(commits_df)
pull_request_handling_prompt = action_handlers.generate_prompt_for_pull_request_handling(pull_requests_df, comments_df, review_comments_df)

commit_consistancy_df = action_handlers.generate_df_for_commit_consistancy(commits_df)
pull_request_handling_df = action_handlers.generate_df_for_pull_request_handling(pull_requests_df, comments_df, review_comments_df)

write_prompt_to_file(commit_consistancy_prompt, 'generated_files/commit_consistancy_prompt.txt')
write_prompt_to_file(pull_request_handling_prompt, 'generated_files/pull_request_handling_prompt.txt')

commit_consistancy_df.to_csv('generated_files/commit_consistancy_df.csv', index=False)
pull_request_handling_df.to_csv('generated_files/pull_request_handling_df.csv', index=False)




