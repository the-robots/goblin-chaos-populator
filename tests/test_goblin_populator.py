import io
import json
import os
import unittest
import urllib.error
from unittest.mock import patch

import goblin_populator as populator


class FakeGitHubClient:
    def __init__(self):
        self.calls = []

    def request(self, method, path, payload=None):
        self.calls.append((method, path, payload))
        if method == "GET":
            return {"object": {"sha": "base-sha"}}
        if path == "/pulls":
            return {"html_url": "https://github.com/example/test/pull/1"}
        if path == "/releases":
            return {"html_url": "https://github.com/example/test/releases/tag/example"}
        if path == "/issues":
            return {"html_url": "https://github.com/example/test/issues/1"}
        return {}


class ReadCountTests(unittest.TestCase):
    def test_reads_non_negative_integer(self):
        with patch.dict(os.environ, {"INPUT_NUM_ISSUES": "4"}):
            self.assertEqual(populator.read_count("num_issues", 5), 4)

    def test_rejects_invalid_and_negative_values(self):
        for value in ("many", "-1"):
            with self.subTest(value=value), patch.dict(
                os.environ, {"INPUT_NUM_ISSUES": value}
            ):
                with self.assertRaisesRegex(ValueError, "non-negative integer"):
                    populator.read_count("num_issues", 5)


class PopulateRepoTests(unittest.TestCase):
    @patch.object(populator.time, "sleep")
    def test_creates_configured_commits_files_and_pull_request(self, _sleep):
        client = FakeGitHubClient()

        populator.populate_repo(
            client,
            "trunk",
            num_issues=1,
            num_prs=1,
            num_commits=2,
            num_releases=1,
            num_files=3,
        )

        self.assertEqual(sum(call[1] == "/issues" for call in client.calls), 1)
        self.assertEqual(sum(call[1] == "/releases" for call in client.calls), 1)
        self.assertEqual(sum(call[1] == "/git/refs" for call in client.calls), 1)
        self.assertEqual(sum(call[0] == "PUT" for call in client.calls), 5)
        pull_request = next(call[2] for call in client.calls if call[1] == "/pulls")
        self.assertEqual(pull_request["base"], "trunk")

    def test_uses_escaped_default_branch_ref(self):
        client = FakeGitHubClient()

        populator.create_branch(client, "goblin-branch", "release/v2")

        self.assertEqual(client.calls[0][1], "/git/ref/heads/release/v2")


class GitHubClientTests(unittest.TestCase):
    @patch("goblin_populator.urllib.request.urlopen")
    def test_sends_bearer_token_and_json_payload(self, urlopen):
        urlopen.return_value = io.BytesIO(b'{"ok": true}')
        client = populator.GitHubClient("secret-token", "example/repository")

        result = client.request("POST", "/issues", {"title": "Goblin"})

        self.assertEqual(result, {"ok": True})
        request = urlopen.call_args.args[0]
        self.assertEqual(request.get_header("Authorization"), "Bearer secret-token")
        self.assertEqual(request.get_header("Content-type"), "application/json")
        self.assertEqual(json.loads(request.data), {"title": "Goblin"})
        self.assertEqual(request.get_header("X-github-api-version"), populator.API_VERSION)

    @patch("goblin_populator.urllib.request.urlopen")
    def test_reports_github_http_errors_with_api_message(self, urlopen):
        urlopen.side_effect = urllib.error.HTTPError(
            "https://api.github.com/repos/example/repository/issues",
            403,
            "Forbidden",
            {},
            io.BytesIO(b'{"message": "Resource not accessible by integration"}'),
        )
        client = populator.GitHubClient("token", "example/repository")

        with self.assertRaisesRegex(
            populator.GitHubAPIError,
            r"POST /issues failed \(403\): Resource not accessible by integration",
        ):
            client.request("POST", "/issues", {"title": "Goblin"})

    @patch("goblin_populator.urllib.request.urlopen")
    def test_reports_network_errors(self, urlopen):
        urlopen.side_effect = urllib.error.URLError("connection refused")
        client = populator.GitHubClient("token", "example/repository")

        with self.assertRaisesRegex(
            populator.GitHubAPIError, "could not be reached: connection refused"
        ):
            client.request("GET", "")

    @patch("goblin_populator.urllib.request.urlopen")
    def test_rejects_invalid_or_unexpected_json(self, urlopen):
        client = populator.GitHubClient("token", "example/repository")
        for response, message in (
            (b"{invalid", "returned invalid JSON"),
            (b"[]", "returned an unexpected response"),
            (b"\xff", "returned invalid JSON"),
        ):
            with self.subTest(response=response):
                urlopen.return_value = io.BytesIO(response)
                with self.assertRaisesRegex(populator.GitHubAPIError, message):
                    client.request("GET", "")

    @patch("goblin_populator.urllib.request.urlopen")
    def test_accepts_empty_success_response(self, urlopen):
        urlopen.return_value = io.BytesIO(b"")
        client = populator.GitHubClient("token", "example/repository")

        self.assertEqual(client.request("DELETE", "/resource"), {})


class MainValidationTests(unittest.TestCase):
    def test_requires_token_and_valid_repository(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "github-token is required"):
                populator.main()

        for repository in ("", "owner", "/repo", "owner/", "owner/repo/extra"):
            with self.subTest(repository=repository), patch.dict(
                os.environ,
                {
                    "INPUT_GITHUB_TOKEN": "token",
                    "GITHUB_REPOSITORY": repository,
                },
                clear=True,
            ):
                with self.assertRaisesRegex(ValueError, "owner/repository"):
                    populator.main()

    @patch.dict(
        os.environ,
        {
            "INPUT_GITHUB_TOKEN": "token",
            "GITHUB_REPOSITORY": "owner/repo",
            "INPUT_NUM_PRS": "2",
            "INPUT_NUM_COMMITS": "0",
            "INPUT_NUM_FILES": "0",
        },
        clear=True,
    )
    @patch("goblin_populator.GitHubClient")
    def test_rejects_empty_pull_request_branches_before_api_call(self, github_client):
        with self.assertRaisesRegex(ValueError, "requires at least one commit or file"):
            populator.main()
        github_client.assert_not_called()

    @patch.dict(
        os.environ,
        {
            "INPUT_GITHUB_TOKEN": "token",
            "GITHUB_REPOSITORY": "owner/repo",
            "INPUT_NUM_ISSUES": "not-a-number",
        },
        clear=True,
    )
    @patch("goblin_populator.GitHubClient")
    def test_rejects_invalid_count_before_api_call(self, github_client):
        with self.assertRaisesRegex(ValueError, "num_issues must be a non-negative integer"):
            populator.main()
        github_client.assert_not_called()

    @patch.dict(
        os.environ,
        {
            "INPUT_GITHUB_TOKEN": "token",
            "GITHUB_REPOSITORY": "owner/repo",
            "INPUT_NUM_ISSUES": "0",
            "INPUT_NUM_PRS": "0",
            "INPUT_NUM_COMMITS": "0",
            "INPUT_NUM_RELEASES": "0",
            "INPUT_NUM_FILES": "0",
        },
        clear=True,
    )
    @patch("goblin_populator.populate_repo")
    @patch("goblin_populator.GitHubClient")
    def test_uses_configured_base_branch(self, github_client, populate_repo):
        github_client.return_value.request.return_value = {"default_branch": "main"}

        populator.main()

        populate_repo.assert_called_once_with(
            github_client.return_value,
            "main",
            num_issues=0,
            num_prs=0,
            num_commits=0,
            num_releases=0,
            num_files=0,
        )


if __name__ == "__main__":
    unittest.main()
