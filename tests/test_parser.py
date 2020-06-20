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
        def test_does_not_mutate_on_no_match(self, subject):
            assert subject.mutate_data("No match") == "No match"

        def test_does_not_fetch_chain_without_modifying(self, subject, mocker):
            mocked_method = mocker.patch.object(subject, "rebuild_sha_list")
            subject.mutate_data('Reinstate "Testing revert revert resolution"')

            mocked_method.assert_not_called

        # We’ve moved the tests of these methods to their own classes
        def test_normalize_then_rebuild_chain(self, subject, mocker):
            norm = mocker.patch.object(
                subject, "normalize_description", return_value="normalized"
            )
            chained = mocker.patch.object(
                subject, "rebuild_sha_list", return_value="chained"
            )
            assert subject.mutate_data("mutate me") == "chained"
            chained.assert_called_once_with("normalized")
            norm.assert_called()

    class TestNormalizeDescription:
        def test_no_match(self, subject):
            assert subject.normalize_description("no match") == "no match"

        def test_single_match(self, subject):
            msg = 'Reinstate "my error"'
            assert subject.normalize_description(msg) == msg

        def test_revert_revert(self, subject):
            msg = '''Revert "Revert "my error""'''
            assert subject.normalize_description(msg) == 'Reinstate "my error"'

        def test_revert_reinstate(self, subject):
            msg = '''Revert "Reinstate "my error""'''
            assert subject.normalize_description(msg) == 'Revert "my error"'

        def test_many_levels(self, subject):
            msg = '''Revert "Revert "Revert "Revert "my error""""'''
            assert subject.normalize_description(msg) == 'Reinstate "my error"'

        def test_with_extra_data(self, subject):
            message = dedent(
                '''
                Revert "Revert "Revert "my error"""

                This reverts commit deadbeefdeadbeefdeadbeefdeadbeefdeadbeef.
                '''
            ).strip()
            expected = dedent(
                """
                Revert "my error"

                This reverts commit deadbeefdeadbeefdeadbeefdeadbeefdeadbeef.
                """
            ).strip()
            assert subject.normalize_description(message) == expected

    class TestRebuildSHAs:
        message = dedent(
            '''
            Revert "Revert "Revert "my error"""

            This reverts commit deadbeefdeadbeefdeadbeefdeadbeefdeadbeef.

            # fnord
            '''
        ).strip()

        def test_no_match(self, subject):
            assert subject.rebuild_sha_list("no match") == "no match"

        def test_single_level(self, subject, mocker):
            self.build_message_chain(mocker, subject, [])
            assert subject.rebuild_sha_list(self.message) == self.message

        def test_full_chain(self, subject, mocker):
            self.build_message_chain(
                mocker,
                subject,
                [
                    "1337beef1337beef1337beef1337beef1337beef",
                    "1337f0011337f0011337f0011337f0011337f001",
                    "1337c0de1337c0de1337c0de1337c0de1337c0de",
                ],
            )

            expected = dedent(
                '''
                Revert "Revert "Revert "my error"""

                This reverts commit deadbeefdeadbeefdeadbeefdeadbeefdeadbeef.
                And reinstates 1337beef1337beef1337beef1337beef1337beef.
                And reverts 1337f0011337f0011337f0011337f0011337f001.
                And reinstates 1337c0de1337c0de1337c0de1337c0de1337c0de.

                # fnord
                '''
            ).strip()

            assert subject.rebuild_sha_list(self.message) == expected

        @staticmethod
        def build_message_chain(mocker, subject, shas):
            messages = [
                dedent(
                    f"""
                    Revert "my {sha} example"

                    This reverts commit {sha}.
                    """
                ).strip()
                for sha in shas
            ]
            messages.append("Final boss")

            def closure(sha):
                return messages.pop(0)

            mocker.patch.object(subject, "message_for_sha", closure)
