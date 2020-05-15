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

            result = subject.mutate_data(self.default_input)
            assert result.endswith(f"\nAnd reinstates commit {previous_sha}.\n")

        def test_handles_previous_message_without_reverts_line(self, subject):
            subject.repo.__getitem__().message = bytes("fnord", "ascii")
            result = subject.mutate_data(self.default_input)
            assert result.endswith("\nAnd reinstates commit == MISSING ==.\n")
