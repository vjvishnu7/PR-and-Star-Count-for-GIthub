import csv
import requests
import os
import argparse

def get_open_pull_requests_count(owner, repo, access_token=None):
    headers = {}
    if access_token:
        headers['Authorization'] = f'token {access_token}'
    headers['Cache-Control'] = 'no-cache'  # Ensure fresh data is retrieved

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    params = {'state': 'open', 'per_page': 100}  # Adjust per_page based on expected number of open pull requests

    open_pull_requests_count = 0
    page = 1
    while True:
        params['page'] = page
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            pull_requests = response.json()
            if not pull_requests:  # No more pull requests available
                break
            open_pull_requests_count += len(pull_requests)
            page += 1
        else:
            print(f"Failed to fetch open pull requests for repository '{owner}/{repo}'")
            return None

    return open_pull_requests_count

def get_stars_count(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(url)
    if response.status_code == 200:
        repo_data = response.json()
        return repo_data.get('stargazers_count', None)
    else:
        print(f"Failed to fetch stars count for repository '{owner}/{repo}'")
        return None

def save_to_csv(data, csv_file_path):
    with open(csv_file_path, 'w', newline='') as csvfile:
        fieldnames = ['Repository', 'Stars', 'Open Pull Requests']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

def main(args):
    repositories = []
    for repo_info in args.repositories:
        owner, repo = repo_info.split("/")
        if not is_valid_repository(owner, repo, args.token):
            print(f"Invalid owner or repository name: {owner}/{repo}")
            continue
        repositories.append({"owner": owner, "repo": repo})

    access_token = args.token

    script_dir = os.path.dirname(os.path.realpath(__file__))
    csv_file_name = "github_data.csv"
    csv_file_path = os.path.join(script_dir, csv_file_name)

    data = []
    for repo_info in repositories:
        owner = repo_info["owner"]
        repo = repo_info["repo"]

        open_pull_requests_count = get_open_pull_requests_count(owner, repo, access_token=access_token)
        stars_count = get_stars_count(owner, repo)

        if open_pull_requests_count is not None and stars_count is not None:
            data.append({'Repository': f"{owner}/{repo}", 'Stars': stars_count, 'Open Pull Requests': open_pull_requests_count})
        else:
            print(f"Failed to obtain information for repository '{owner}/{repo}'")

    save_to_csv(data, csv_file_path)
    print("CSV file saved successfully.")

def is_valid_repository(owner, repo, access_token):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {}
    if access_token:
        headers['Authorization'] = f'token {access_token}'
    response = requests.get(url, headers=headers)
    return response.status_code == 200

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GitHub Repository Data Collector")
    parser.add_argument("--token", help="GitHub Personal Access Token")
    parser.add_argument("repositories", nargs="+", help="List of repositories in the format owner/repo")

    args = parser.parse_args()
    main(args)
