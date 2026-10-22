import unittest

from scripts.sync_readme_repositories import (
    escape_markdown,
    rank_featured_repositories,
    render_featured_block,
    render_starred_block,
    replace_marked_block,
)


class SyncReadmeRepositoriesTests(unittest.TestCase):
    def test_escape_markdown_handles_table_characters_and_newlines(self):
        self.assertEqual(escape_markdown("Line 1|part\nLine 2"), "Line 1\\|part<br/>Line 2")
        self.assertEqual(escape_markdown(None), "—")

    def test_replace_marked_block_only_updates_inside_markers(self):
        content = (
            "A\n"
            "<!-- FEATURED-REPOS:START -->\nold\n<!-- FEATURED-REPOS:END -->\n"
            "B\n"
            "<!-- STARRED-REPOS:START -->\nold\n<!-- STARRED-REPOS:END -->\n"
            "C\n"
        )
        updated = replace_marked_block(content, "FEATURED-REPOS:START", "FEATURED-REPOS:END", "new")
        self.assertIn("A\n<!-- FEATURED-REPOS:START -->\nnew\n<!-- FEATURED-REPOS:END -->\nB", updated)
        self.assertIn("<!-- STARRED-REPOS:START -->\nold\n<!-- STARRED-REPOS:END -->", updated)

    def test_rank_featured_repositories_sorts_by_stars_then_recent_push(self):
        repos = [
            {"name": "older", "stargazers_count": 3, "pushed_at": "2025-01-01T00:00:00Z", "fork": False, "private": False},
            {"name": "newer", "stargazers_count": 3, "pushed_at": "2025-02-01T00:00:00Z", "fork": False, "private": False},
            {"name": "popular", "stargazers_count": 10, "pushed_at": "2024-01-01T00:00:00Z", "fork": False, "private": False},
            {"name": "forked", "stargazers_count": 99, "pushed_at": "2025-03-01T00:00:00Z", "fork": True, "private": False},
        ]
        ranked = rank_featured_repositories(repos, limit=3)
        self.assertEqual([repo["name"] for repo in ranked], ["popular", "newer", "older"])

    def test_render_blocks_cover_normal_and_empty_data(self):
        repos = [
            {
                "name": "repo-one",
                "full_name": "JMAdikari/repo-one",
                "html_url": "https://github.com/JMAdikari/repo-one",
                "description": "desc | with pipe\nnewline",
                "language": "Python",
                "stargazers_count": 5,
                "pushed_at": "2025-03-01T00:00:00Z",
                "fork": False,
                "private": False,
            }
        ]
        featured = render_featured_block("JMAdikari", repos, limit=1)
        self.assertIn("[repo-one](https://github.com/JMAdikari/repo-one)", featured)
        self.assertIn("desc \\| with pipe<br/>newline", featured)

        starred = render_starred_block([], limit=15)
        self.assertIn("_No starred repositories found._", starred)


if __name__ == "__main__":
    unittest.main()
