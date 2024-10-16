# goblin-chaos-populator
Goblin Chaos Populator is a fun and chaotic GitHub Action designed to populate your repository with random issues, pull requests, commits, releases, branches, and files. It’s perfect for testing automation, load testing, or just causing delightful goblin-themed chaos in your repositories! 🐲⚔️ 

## Example workflow

Create a workflow file, ie. `.github/workflows/populate.yml` and add the following to test the action.

``` yaml
name: Populate Repo with Chaos

on: [push]

jobs:
  chaos:
    runs-on: ubuntu-latest
    steps:
      - uses: ./  # Use your action from the same repo
        with:
          num_issues: 3
          num_prs: 2
          num_commits: 4
          num_releases: 1
          num_files: 2
```
