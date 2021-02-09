#!/usr/bin/env python3

import tempfile

from github import Github
from git import Repo, remote

from msrest.authentication import BasicAuthentication
from azure.devops.connection import Connection
from azure.devops.v6_0.git import GitRepositoryCreateOptions

# Fill in with your personal access token and org URL
personal_access_token = "azure_token"
organization_url = "https://dev.azure.com/ORGANIZATION"
project = "AZURE_ORG"
gh_token = 'some_token'
gh_organization_name = 'github_account_name'

# Create a connection to the org
credentials = BasicAuthentication("", personal_access_token)
connection = Connection(base_url=organization_url, creds=credentials)

git_client = connection.clients_v6_0.get_git_client()

g = Github(gh_token)

gh_organization = g.get_organization(gh_organization_name)

for repo in gh_organization.get_repos():
    if not repo.private:
        continue
    print(f"repo: {repo.name}")

    repo_options = GitRepositoryCreateOptions(name=repo.name)
    azure_repo = git_client.create_repository(repo_options, project=project)
    print(f"Create {azure_repo.name}: {azure_repo.ssh_url} => {azure_repo.web_url}")

    with tempfile.TemporaryDirectory(prefix='git-migration-') as tmprepo:
        gh_repo = Repo.clone_from(repo.ssh_url, tmprepo)

        remote.Remote.add(gh_repo, 'azure', azure_repo.ssh_url)

        gh_repo.remotes[-1].push()
