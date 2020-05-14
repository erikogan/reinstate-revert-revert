import re

from dulwich.repo import Repo


class Parser:
    head_pattern = re.compile(r'^(Revert|Reinstate) "(Revert|Reinstate) "(.*)""')
    tail_pattern = re.compile(r"This reverts commit ([0-9a-f]{40}).")

    def __init__(self, encoding="UTF-8", repo=Repo(".")):
        self.encoding = encoding
        self.repo = repo

    def run(self, files):
        for file in files:
            self.mutate_file(file)

    def mutate_data(self, str):
        match = self.head_pattern.match(str)
        if not match:
            return str

        str = self.head_pattern.sub(r'Reinstate "\3"', str)

        sha = self.extract_sha(str)

        try:
            previous_message = self.message_for_sha(sha)
            previous_sha = self.extract_sha(previous_message)
        except (KeyError, AttributeError):
            previous_sha = "== MISSING =="

        str += f"And reinstates {previous_sha}.\n"

        return str

    def mutate_file(self, file):
        before = None

        with open(file) as f:
            before = f.read()

        after = self.mutate_data(before)

        if after != before:
            with open(file, "w") as f:
                f.write(after)

    def message_for_sha(self, sha):
        return self.repo[bytes(sha, "ascii")].message.decode(self.encoding)

    def extract_sha(self, str):
        return self.tail_pattern.search(str).group(1)
