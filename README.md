# Goblin Chaos Populator

Goblin Chaos Populator is a composite GitHub Action for creating sample issues, pull requests, commits, releases, and files in a repository. Use it in a disposable or dedicated test repository to exercise workflows and demos; it creates persistent repository content and does not clean it up.

## Usage

Run it manually in a test repository:

```yaml
name: Populate test repository

on:
  workflow_dispatch:
    inputs:
      num_issues:
        description: Number of issues to create
        type: number
        default: 1
      num_prs:
        description: Number of pull requests to create
        type: number
        default: 1
      num_commits:
        description: Number of commits per pull-request branch
        type: number
        default: 1
      num_releases:
        description: Number of releases to create
        type: number
        default: 0
      num_files:
        description: Additional files per pull-request branch
        type: number
        default: 0

permissions:
  contents: write
  issues: write
  pull-requests: write

jobs:
  populate:
    runs-on: ubuntu-latest
    steps:
      - name: Add goblin chaos
        uses: the-robots/goblin-chaos-populator@v2
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          num_issues: ${{ inputs.num_issues }}
          num_prs: ${{ inputs.num_prs }}
          num_commits: ${{ inputs.num_commits }}
          num_releases: ${{ inputs.num_releases }}
          num_files: ${{ inputs.num_files }}
```

The workflow token needs `contents: write` to create branches, commits, files, and releases; `issues: write` to create issues; and `pull-requests: write` to open pull requests. Keep these permissions scoped to the job that runs the action.

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `github-token` | Token used for GitHub API calls. Usually `${{ secrets.GITHUB_TOKEN }}`. | Yes | — |
| `base_branch` | Branch for new branches, pull requests, and releases. Defaults to the repository's default branch. | No | `""` |
| `num_issues` | Number of issues to create. | No | `5` |
| `num_prs` | Number of pull requests and branches to create. | No | `5` |
| `num_commits` | Number of commits to create on each pull-request branch. | No | `1` |
| `num_releases` | Number of releases to create. | No | `2` |
| `num_files` | Additional files to commit on each pull-request branch. Each file is a separate commit. | No | `3` |

Counts must be non-negative integers. Set a count to `0` to skip that type of content. Pull requests need at least one commit or file on each branch, so `num_prs` cannot be positive when both `num_commits` and `num_files` are zero.

## Development

The action uses only the Python standard library and runs on `ubuntu-latest`. Run its unit tests with:

```sh
python3 -m unittest discover -s tests -v
```

## License

MIT. See [LICENSE](LICENSE).
