import re
from textwrap import dedent

import pytest

from reinstate_revert_revert.parser import Parser


class TestParser:
    @pytest.fixture
    def subject(self, mocker):
        repo = mocker.MagicMock(name="repo")
        parser = Parser(repo=repo)
        return parser

    class TestMutateData:
        default_input = dedent(
            """
            Revert "Revert "Testing revert revert resolution""

            This reverts commit 4ecb0e7496c8013a6e5fbbcd7712a69836f82f22.

            # Please enter the commit message for your changes. Lines starting
            # with '#' will be ignored, and an empty message aborts the commit.
            #
            # On branch erik/test-reinstate
            # Changes to be committed:
            # modified:   pyproject.toml
            #
            # ------------------------ >8 ------------------------
            # Do not modify or remove the line above.
            # Everything below it will be ignored.
            diff --git a/pyproject.toml b/pyproject.toml
            index 7d1c9e2f..62b3a72a 100644
            --- a/pyproject.toml
            +++ b/pyproject.toml
            @@ -1,6 +1,6 @@
             [tool.poetry]
             name = "reinstate-revert-revert"
            -version = "0.1.2"
            +version = "0.1.3"
             description = "pre-commit plugin to improve default commit messages when reverting reverts"
             authors = ["Erik Ogan <erik@ogan.net>"]
             maintainers = ["Erik Ogan <erik@ogan.net>"]
            """
        ).lstrip()

        def test_does_not_mutate_on_no_match(self, subject):
            assert subject.mutate_data("No match") == "No match"

        def test_resolves_revert_revert(self, subject, mocker):
            mocker.patch.object(subject, "extract_sha", lambda x: "")
            result = subject.mutate_data(self.default_input)
            assert result.startswith('Reinstate "Testing revert revert resolution"\n')

        def test_adds_reinstate_context(self, subject):
            previous_sha = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
            subject.repo.__getitem__().message = bytes(
                dedent(
                    f"""
                    Revert "Testing revert revert resolution"

                    This reverts commit {previous_sha}.
                    """
                ).lstrip(),
                "ascii",
            )

            result = self.normalize_message(subject.mutate_data(self.default_input))
            assert result.endswith(f"\nAnd reinstates commit {previous_sha}.\n\n")

        def test_handles_previous_message_without_reverts_line(self, subject):
            subject.repo.__getitem__().message = bytes("fnord", "ascii")
            result = self.normalize_message(subject.mutate_data(self.default_input))
            assert result.endswith("\nAnd reinstates commit == MISSING ==.\n\n")

        def normalize_message(self, str):
            # Remove everything Git will
            str = re.sub(
                r"# ------------------------ >8 ------------------------.*",
                "",
                str,
                flags=(re.MULTILINE | re.DOTALL),
            )
            return re.sub(r"^#.*\n", "", str, flags=re.MULTILINE)
