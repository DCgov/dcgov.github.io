import requests
import json
from jsonschema import validate
from settings import ACCESS_TOKEN


def format_activity(data):
    return [d['total'] for d in data]


def format_teams(data):
    return [d['name'] for d in data]


def github_api_items(full_name):
    return [
        {
            "name": "activity",
            "url": 'https://api.github.com/repos/{}/stats/commit_activity'.format(full_name),
            "formatter": format_activity
        },
        {
            "name": "teams",
            "url": 'https://api.github.com/repos/{}/teams'.format(full_name),
            "formatter": format_teams
        },
        {
            "name": "languages",
            "url": 'https://api.github.com/repos/{}/languages'.format(full_name),
            "formatter": ""
        }
    ]


def get_github(full_name, github_headers):
    github = {}
    items = github_api_items(full_name)
    for item in items:
        response = requests.get(item['url'], headers=github_headers)
        response_data = response.json()
        if item['formatter']:
            response_data = item['formatter'](response_data)
        github[item['name']] = response_data
    return github


def get_civic(full_name, default_branch, schema):
    civic_url = 'https://raw.githubusercontent.com/{0}/{1}/civic.json'.format(full_name, default_branch)
    civic_response = requests.get(civic_url)
    try:
        civic_data = civic_response.json()
        civic_data['name'] = civic_data['name'].lower()
        validate(civic_data, schema)
        return civic_data
    except:
        return None


if __name__ == '__main__':
    metadata = []
    github_headers = {'Authorization': 'token {}'.format(ACCESS_TOKEN)}
    schema = requests.get('https://raw.githubusercontent.com/DCgov/civic.json/master/schema.json').json()
    repos = requests.get('https://api.github.com/orgs/dcgov/repos').json()
    for repo in repos:
        civic = get_civic(repo['full_name'], repo['default_branch'], schema)
        if civic:
            civic['github'] = get_github(repo['full_name'], github_headers)
            metadata.append(civic)

    with open('_data/projects.json', 'w') as outfile:
        json.dump(metadata, outfile, indent=4)
