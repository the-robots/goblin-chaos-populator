# Goblin Chaos Populator 🧙‍♂️🐲

**Goblin Chaos Populator** is a fun and dynamic GitHub Action designed to populate your repository with random chaos! Automate the creation of random issues, pull requests, commits, branches, releases, and files to test workflows, simulate a busy repository, or just add some goblin mischief to your projects.

With customizable inputs, you can specify the number of each element to create, bringing controlled chaos to your repository in seconds. Perfect for **repository stress testing**, **demo repositories**, and **fun experiments**!

---

## 🚀 Key Features

- **📝 Random Issue Creation**: Generate custom issues with goblin-themed titles and bodies.
- **🔀 Random Pull Requests**: Automatically create goblin-style pull requests with random content.
- **⚙️ Random Commits**: Add random commits to new branches with goblin-inspired code snippets.
- **🏷 Branch Creation**: Automatically create branches with unique names for PRs and commits.
- **🚀 Random Releases**: Publish goblin-themed releases with random version numbers.
- **📄 Random File Uploads**: Upload random files to newly created branches.

---

## 🔧 Inputs

| Input         | Description                                  | Required | Default |
|---------------|----------------------------------------------|----------|---------|
| `num_issues`  | Number of issues to create                   | No       | 5       |
| `num_prs`     | Number of pull requests to create            | No       | 5       |
| `num_commits` | Number of commits to create                  | No       | 5       |
| `num_releases`| Number of releases to create                 | No       | 2       |
| `num_files`   | Number of files to upload per branch         | No       | 3       |

---

## 📦 Usage

Use this action in your GitHub workflows to populate your repository with goblin-inspired randomness!

### Example Workflow

Create a workflow in `.github/workflows/populate.yml`:

```yaml
name: "🔥 Goblins are populating your repo with chaos 🔥"

on: 
  workflow_dispatch:
    inputs:
      num_issues:
        description: "Number of issues to create"
        required: false
        default: 5
      num_prs:
        description: "Number of pull requests to create"
        required: false
        default: 5
      num_commits:
        description: "Number of commits to create"
        required: false
        default: 5
      num_releases:
        description: "Number of releases to create"
        required: false
        default: 2
      num_files:
        description: "Number of files to upload per branch"
        required: false
        default: 3

jobs:
  chaos:
    runs-on: ubuntu-latest

    permissions:
      contents: write       
      issues: write          
      pull-requests: write      

    steps:
      - name: Run Goblin Chaos Populator
        uses: the-robots/goblin-chaos-populator@v1.3
        with:
          num_issues: ${{ inputs.num_issues }}
          num_prs: ${{ inputs.num_prs }}
          num_commits: ${{ inputs.num_commits }}
          num_releases: ${{ inputs.num_releases }}
          num_files: ${{ inputs.num_files }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## 🤖 Permissions

This action requires the following permissions to function properly:

```
permissions:
  contents: write
  issues: write
  pull-requests: write
  metadata: read
  actions: read
```

## 🛠 How It Works

- Issues: Random goblin-inspired issues with quirky titles and bodies are created.
- Pull Requests: New branches are generated with pull requests to merge them into main.
- Commits: Each new branch contains random commits with goblin content.
- Releases: Goblin-themed releases are published with fun version numbers.
- Files: Random files are uploaded to branches with creative content.

## 📥 Installation

1. Create a new repository or navigate to an existing one.
2. Add the Goblin Chaos Populator to your workflow using the example above.
3. Commit and push the changes to your repository.
4. Watch as the goblins bring controlled chaos to your repository!

## 🎯 Use Cases

- Repository Stress Testing: Simulate a busy repository to test workflows and CI/CD pipelines.
- Demo Repositories: Showcase how your project handles multiple pull requests and commits.
- Fun Experiments: Add some randomness to your repository for fun or testing.

## ⚠️ Disclaimer

This action adds random data to your repository. Use with caution, especially on production repositories!
Disclaimer: This is not an official GitHub repository or Action!

## 📝 License

This project is licensed under the MIT License.

## 🙌 Contributions

Feel free to fork this repository and submit pull requests with your improvements. Let’s bring even more chaos together!

## 📧 Contact

For any questions or issues submit an issue in this repository. Disclaimer: This is not an official GitHub repository or Action!

## Let the goblins bring some organized chaos to your repository! 🧙‍♂️✨🐲





