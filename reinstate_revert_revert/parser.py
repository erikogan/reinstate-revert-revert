import re

from dulwich.repo import Repo


class Parser:
    head_pattern = re.compile(r'^(Revert|Reinstate) "(.*)"')
    tail_pattern = re.compile(r"\n+(#|\Z)")
    extract_pattern = re.compile(r"This reverts commit ([0-9a-f]{40}).")

    MISSING_SHA = "== MISSING =="

    def __init__(self, encoding="UTF-8", repo=Repo(".")):
        self.encoding = encoding
        self.repo = repo

    def run(self, files):
        for file in files:
            self.mutate_file(file)

    def mutate_data(self, str):
        normalized = self.normalize_description(str)
        if normalized == str:
            return str

        return self.rebuild_sha_list(normalized)

    def mutate_file(self, file):
        before = None

        with open(file) as f:
            before = f.read()

        after = self.mutate_data(before)

        if after != before:
            with open(file, "w") as f:
                f.write(after)

    @classmethod
    def normalize_description(cls, desc, depth=None):
        match = cls.head_pattern.match(desc)
        if not match:
            return [0, desc] if depth else desc

        result = cls.normalize_description(match[2], depth + 1 if depth else 1)
        unraveled = cls.unravel(match[1], result[0])

        if depth is None:
            action = "Revert" if unraveled < 0 else "Reinstate"
            return cls.head_pattern.sub(f'{action} "{result[1]}"', desc)

        return [unraveled, result[1]]

    @staticmethod
    def unravel(action, previous):  # TODO: Rename
        if action == "Revert":
            if previous >= 0:  # Base description or a Reinstate
                return -1
            return 1
        # Reinstate, this should only ever be the innermost, but we must
        # handle erroneous cases
        if previous == 0:
            return 1
        # I’m not 100% convinced this is the right answer
        return -previous

    def rebuild_sha_list(self, message, depth=None):
        extracted = self.extract_sha(message)
        if extracted is None:
            return message if depth is None else []

        try:
            result = self.rebuild_sha_list(
                self.message_for_sha(extracted), depth + 1 if depth else 1
            )
        except (KeyError, AttributeError):
            return [self.MISSING_SHA]

        if depth is None:
            if not result:
                return message
            return self.tail_pattern.sub(self.build_reinstate_chain(result), message, 1)

        return [extracted] + result

    @staticmethod
    def build_reinstate_chain(shas):
        def closure(match):
            lines = []
            for i, sha in enumerate(shas):
                action = "reinstate" if i % 2 == 0 else "revert"
                lines.append(f"And {action}s {sha}.")
            lines = "\n".join(lines)
            return f"\n{lines}{match[0]}"

        return closure

    def message_for_sha(self, sha):
        return self.repo[bytes(sha, "ascii")].message.decode(self.encoding)

    def extract_sha(self, str):
        match = self.extract_pattern.search(str)
        if match is None:
            return None
        return match.group(1)
