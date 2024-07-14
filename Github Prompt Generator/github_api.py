import requests
import json
import os

GITHUB_API_KEY = os.environ.get('GITHUB_API_KEY')

def _generate_headers():
    return {
        'Authorization': f'token {GITHUB_API_KEY}',
        "Accept": "application/vnd.github+json",
        'X-GitHub-Api-Version': '2022-11-28'
    }

def get_commits(owner, repo, branch = 'main', per_page = 100, do_paginate = True):
    page = 1

    commits = []
    
    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/commits?sha={branch}&per_page={per_page}&page={page}"
        response = requests.request("GET", url, headers=_generate_headers())
        commits_from_page = json.loads(response.text)
        commits = commits + commits_from_page
        if len(commits_from_page) == 0 or not do_paginate:
            break
        page += 1

    return commits

def get_pull_requests(owner, repo, per_page = 100, do_paginate = True):
    page = 1

    pull_requests = []

    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=all&per_page={per_page}&page={page}"
        response = requests.request("GET", url, headers=_generate_headers())
        pull_requests_from_page = json.loads(response.text)
        pull_requests = pull_requests + pull_requests_from_page
        if len(pull_requests_from_page) == 0 or not do_paginate:
            break
        page += 1
    
    return pull_requests

def execute_url_request(url):
    response = requests.request("GET", url, headers=_generate_headers())
    return json.loads(response.text)
