"""Populate a GitHub repository with opt-in goblin-themed test content."""

import base64
import json
import os
import secrets
import string
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid


API_ROOT = "https://api.github.com"
API_VERSION = "2022-11-28"


class GitHubAPIError(RuntimeError):
    """An unsuccessful request to the GitHub REST API."""


class GitHubClient:
    def __init__(self, token, repository):
        self.base_url = f"{API_ROOT}/repos/{repository}"
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": "goblin-chaos-populator",
        }

    def request(self, method, path, payload=None):
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=body,
            headers=self.headers,
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                response_body = response.read()
        except urllib.error.HTTPError as error:
            details = error.read().decode("utf-8", errors="replace")
            try:
                message = json.loads(details).get("message", details)
            except (json.JSONDecodeError, AttributeError):
                message = details
            raise GitHubAPIError(
                f"GitHub API {method} {path} failed ({error.code}): {message}"
            ) from error
        except urllib.error.URLError as error:
            raise GitHubAPIError(
                f"GitHub API {method} {path} could not be reached: {error.reason}"
            ) from error

        if not response_body:
            return {}
        try:
            result = json.loads(response_body)
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise GitHubAPIError(
                f"GitHub API {method} {path} returned invalid JSON"
            ) from error
        if not isinstance(result, dict):
            raise GitHubAPIError(
                f"GitHub API {method} {path} returned an unexpected response"
            )
        return result


def random_string(prefix="goblin-", length=8):
    alphabet = string.ascii_lowercase + string.digits
    return prefix + "".join(secrets.choice(alphabet) for _ in range(length))


def read_count(name, default):
    raw_value = os.getenv(f"INPUT_{name.upper()}", str(default)).strip()
    try:
        value = int(raw_value)
    except ValueError as error:
        raise ValueError(
            f"{name} must be a non-negative integer; got {raw_value!r}"
        ) from error
    if value < 0:
        raise ValueError(f"{name} must be a non-negative integer; got {value}")
    return value


def create_issue(client):
    issue = client.request(
        "POST",
        "/issues",
        {
            "title": random_string(prefix="Goblin issue: "),
            "body": "Goblins have raised an issue: " + random_string(length=20),
        },
    )
    print(f"Created issue: {issue['html_url']}")


def create_branch(client, branch_name, base_branch):
    encoded_base = urllib.parse.quote(base_branch, safe="/")
    ref = client.request("GET", f"/git/ref/heads/{encoded_base}")
    client.request(
        "POST",
        "/git/refs",
        {"ref": f"refs/heads/{branch_name}", "sha": ref["object"]["sha"]},
    )


def create_commit(client, branch_name):
    filename = random_string(prefix="goblin-file-") + ".txt"
    content = "Goblins added some code:\n" + random_string(length=50)
    path = "/contents/" + urllib.parse.quote(filename, safe="")
    client.request(
        "PUT",
        path,
        {
            "message": "Add goblin chaos",
            "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
            "branch": branch_name,
        },
    )


def upload_random_file(client, branch_name):
    filename = random_string(prefix="goblin-attachment-") + ".txt"
    content = "This is a random file uploaded by goblins.\n" + random_string(length=100)
    path = "/contents/" + urllib.parse.quote(filename, safe="")
    client.request(
        "PUT",
        path,
        {
            "message": f"Add {filename}",
            "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
            "branch": branch_name,
        },
    )


def create_pull_request(client, branch_name, base_branch):
    pull_request = client.request(
        "POST",
        "/pulls",
        {
            "title": random_string(prefix="Goblin PR: "),
            "head": branch_name,
            "base": base_branch,
            "body": "This goblin PR comes from the depths of the cave: "
            + random_string(length=20),
        },
    )
    print(f"Created pull request: {pull_request['html_url']}")


def create_release(client, base_branch):
    tag = f"goblin-{uuid.uuid4().hex[:12]}"
    release = client.request(
        "POST",
        "/releases",
        {
            "tag_name": tag,
            "target_commitish": base_branch,
            "name": random_string(prefix="Goblin release: "),
            "body": "This goblin release contains treasure: "
            + random_string(length=20),
        },
    )
    print(f"Created release: {release['html_url']}")


def populate_repo(
    client, base_branch, num_issues, num_prs, num_commits, num_releases, num_files
):
    for _ in range(num_issues):
        create_issue(client)
        time.sleep(1)

    for _ in range(num_releases):
        create_release(client, base_branch)
        time.sleep(1)

    for _ in range(num_prs):
        branch_name = random_string(prefix="goblin-chaos-")
        create_branch(client, branch_name, base_branch)
        for _ in range(num_commits):
            create_commit(client, branch_name)
        for _ in range(num_files):
            upload_random_file(client, branch_name)
        create_pull_request(client, branch_name, base_branch)
        time.sleep(1)


def main():
    token = os.getenv("INPUT_GITHUB_TOKEN", "").strip()
    repository = os.getenv("GITHUB_REPOSITORY", "").strip()
    if not token:
        raise ValueError(
            "github-token is required; pass secrets.GITHUB_TOKEN to the action"
        )
    if (
        not repository
        or repository.count("/") != 1
        or any(not part for part in repository.split("/"))
    ):
        raise ValueError("GITHUB_REPOSITORY must be set to owner/repository")

    counts = {
        "num_issues": read_count("num_issues", 5),
        "num_prs": read_count("num_prs", 5),
        "num_commits": read_count("num_commits", 1),
        "num_releases": read_count("num_releases", 2),
        "num_files": read_count("num_files", 3),
    }
    if counts["num_prs"] and not (counts["num_commits"] or counts["num_files"]):
        raise ValueError("num_prs requires at least one commit or file per pull request branch")

    client = GitHubClient(token, repository)
    repository_info = client.request("GET", "")
    base_branch = os.getenv("INPUT_BASE_BRANCH", "").strip() or repository_info.get(
        "default_branch"
    )
    if not base_branch:
        raise ValueError("Could not determine the repository default branch")

    print(f"Populating {repository} from base branch {base_branch}...")
    populate_repo(client, base_branch, **counts)


if __name__ == "__main__":
    try:
        main()
    except (GitHubAPIError, ValueError, KeyError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
