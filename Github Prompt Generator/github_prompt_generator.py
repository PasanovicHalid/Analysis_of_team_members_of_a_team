import pandas as pd
import github_api as github
import github_action_handler as action_handlers

GITHUB_OWNER = 'Grupa-6-PSW'
GITHUB_REPOS = ['front-end', 'back-end']

def write_prompt_to_file(prompt, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(prompt)

def get_commits_df():
    github_commits = []
    for GITHUB_REPO in GITHUB_REPOS:
        github_commits_for_repo = github.get_commits(GITHUB_OWNER, GITHUB_REPO)
        github_commits = github_commits + github_commits_for_repo
    df = pd.json_normalize(github_commits)
    return df

def get_pull_requests_df():
    github_pull_requests = []
    for GITHUB_REPO in GITHUB_REPOS:
        github_pull_requests_for_repo = github.get_pull_requests(GITHUB_OWNER, GITHUB_REPO)
        github_pull_requests = github_pull_requests + github_pull_requests_for_repo
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

def create_number_of_file_for_ordering(length_of_list, index):
    order_of_10_expontents = len(str(length_of_list))

    return str(index).zfill(order_of_10_expontents)
    
    
commits_df = get_commits_df()

commits_df['commit.author.date'] = pd.to_datetime(commits_df['commit.author.date'])
commits_df = commits_df.sort_values(by='commit.author.date', ascending=True, ignore_index=True)

commit_consistancy_prompts = action_handlers.generate_prompt_for_commit_consistancy(commits_df)

commit_consistancy_df = action_handlers.generate_df_for_commit_consistancy(commits_df)

for i in range(len(commit_consistancy_prompts)):
    write_prompt_to_file(commit_consistancy_prompts[i], f'generated_files/commit_consistancy/commit_consistancy_prompt-{create_number_of_file_for_ordering(len(commit_consistancy_prompts), i + 1)}.txt')

commit_consistancy_df.to_csv('generated_files/commit_consistancy_df.csv', index=False)

pull_requests_df = get_pull_requests_df()
comments_df = get_comments_of_pull_request_and_add_to_df(pull_requests_df)
review_comments_df = get_review_comments_of_pull_request_and_add_to_df(pull_requests_df)
#order by created_at
pull_requests_df['created_at'] = pd.to_datetime(pull_requests_df['created_at'])
pull_requests_df = pull_requests_df.sort_values(by='created_at', ascending=True, ignore_index=True)

pull_request_handling_prompt = action_handlers.generate_prompt_for_pull_request_handling(pull_requests_df, comments_df, review_comments_df)
pull_request_handling_df = action_handlers.generate_df_for_pull_request_handling(pull_requests_df, comments_df, review_comments_df)

for i in range(len(pull_request_handling_prompt)):
    write_prompt_to_file(pull_request_handling_prompt[i], f'generated_files/pull_request_handling/pull_request_handling_prompt-{create_number_of_file_for_ordering(len(pull_request_handling_prompt), i + 1)}.txt')

pull_request_handling_df.to_csv('generated_files/pull_request_handling_df.csv', index=False)




