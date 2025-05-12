import os
import random
import string
import requests
import base64
import time

# Get the GitHub token and repository information from the environment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY")  # e.g., owner/repo

API_URL = f"https://api.github.com/repos/{REPO}"
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def random_string(prefix="goblin-", length=5):
    return prefix + ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def create_issue():
    issue_data = {
        "title": random_string(prefix="Goblin-Issue-", length=10),
        "body": "Goblins have raised an issue: " + random_string(length=20),
    }
    response = requests.post(f"{API_URL}/issues", headers=HEADERS, json=issue_data)
    print("Goblin Issue: " + str(response.status_code))

def create_pr(branch_name):
    pr_data = {
        "title": random_string(prefix="Goblin-PR-", length=10),
        "head": branch_name,
        "base": "main",
        "body": "This goblin PR comes from the depths of the cave: " + random_string(length=20),
    }
    response = requests.post(f"{API_URL}/pulls", headers=HEADERS, json=pr_data)
    print("Goblin PR: " + str(response.status_code))

def create_branch(branch_name):
    ref_response = requests.get(f"{API_URL}/git/ref/heads/main", headers=HEADERS)
    source_sha = ref_response.json()["object"]["sha"]
    data = {"ref": f"refs/heads/{branch_name}", "sha": source_sha}
    response = requests.post(f"{API_URL}/git/refs", headers=HEADERS, json=data)
    print("Goblin Branch: " + str(response.status_code))
    return branch_name if response.status_code == 201 else None

def create_commit(branch_name):
    content = "Goblins added some code:\n" + random_string(length=50)
    filename = random_string(prefix="goblin-file-", length=8) + ".txt"
    data = {
        "message": "Goblin commit",
        "content": base64.b64encode(content.encode()).decode(),
        "branch": branch_name,
    }
    response = requests.put(f"{API_URL}/contents/{filename}", headers=HEADERS, json=data)
    print("Goblin Commit: " + str(response.status_code))

def create_release():
    release_data = {
        "tag_name": f"v{random.randint(1, 100)}.{random.randint(0, 10)}.{random.randint(0, 10)}",
        "name": random_string(prefix="Goblin-Release-", length=10),
        "body": "This goblin release contains treasure: " + random_string(length=20),
    }
    response = requests.post(f"{API_URL}/releases", headers=HEADERS, json=release_data)
    print("Goblin Release: " + str(response.status_code))

def upload_random_file(branch_name):
    filename = random_string(prefix="goblin-attachment-", length=8) + ".txt"
    content = "This is a random file uploaded by goblins.\n" + random_string(length=100)
    data = {
        "message": "Uploading " + filename,
        "content": base64.b64encode(content.encode()).decode(),
        "branch": branch_name,
    }
    response = requests.put(f"{API_URL}/contents/{filename}", headers=HEADERS, json=data)
    print("Goblin File: " + str(response.status_code))

def create_fake_binaries(count, size_kb):
    print(f"Creating {count} fake binaries of {size_kb}KB each...")
    os.makedirs("binaries", exist_ok=True)
    for i in range(count):
        path = os.path.join("binaries", f"goblin_binary_{i+1}.bin")
        with open(path, "wb") as f:
            f.write(os.urandom(size_kb * 1024))
    print("Goblin Binaries: Done")

def populate_repo(num_issues, num_prs, num_commits, num_releases, num_files, num_binaries, binary_size_kb):
    for _ in range(num_issues):
        create_issue()
        time.sleep(1)

    for _ in range(num_releases):
        create_release()
        time.sleep(1)

    for _ in range(num_prs):
        branch_name = random_string(prefix="goblin-branch-", length=8)
        if create_branch(branch_name):
            create_commit(branch_name)
            create_pr(branch_name)
            for _ in range(num_files):
                upload_random_file(branch_name)
        time.sleep(1)

    if num_binaries > 0:
        create_fake_binaries(num_binaries, binary_size_kb)

if __name__ == "__main__":
    # Get inputs from the environment
    num_issues = int(os.getenv("INPUT_NUM_ISSUES", 5))
    num_prs = int(os.getenv("INPUT_NUM_PRS", 5))
    num_commits = int(os.getenv("INPUT_NUM_COMMITS", 5))
    num_releases = int(os.getenv("INPUT_NUM_RELEASES", 2))
    num_files = int(os.getenv("INPUT_NUM_FILES", 3))
    num_binaries = int(os.getenv("INPUT_NUM_BINARIES", 0))
    binary_size_kb = int(os.getenv("INPUT_BINARY_SIZE_KB", 128))

    print("The goblins are populating the repository with chaos...")
    populate_repo(num_issues, num_prs, num_commits, num_releases, num_files, num_binaries, binary_size_kb)

