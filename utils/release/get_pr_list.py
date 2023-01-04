# Extract a list of PRs from a given tag.
#
# The `git` and `gh` CLI tools should be installed, and the script should be run in a clone
# of the go-obscuro repository.
#
import re, argparse
from subprocess import Popen, PIPE

REGEX1 = "(?P<hash>[0-9A-Za-z]{8}) (?P<title>.*) \(#(?P<number>[0-9]*)\)$"
REGEX2 = "(?P<hash>[0-9A-Za-z]{8}) Merge pull request #(?P<number>[0-9]*).*$"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract merged PRs from given tag to current main. ')
    parser.add_argument('--from', help='Tag to extract PRs from, e.g. v0.7')
    args = parser.parse_args()

    process = Popen(['git', 'log', '%s..' % args.from_tag, '--show-pulls', '--first-parent', 'main', '--oneline'],
                    stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    for line in stdout.split(b'\n'):
        value = line.decode("utf-8")

        regex = re.compile(REGEX1, re.M)
        result = regex.search(value)
        if result is not None:
            hash = result.group('hash')
            title = result.group('title')
            number = result.group('number')
            print("    * `%s` %s (#%s)" % (hash, title.capitalize(), number))
        else:
            regex = re.compile(REGEX2, re.M)
            result = regex.search(value)
            if result is not None:
                hash = result.group('hash')
                number = result.group('number')

                process = Popen(['gh', 'pr', 'view', number], stdout=PIPE, stderr=PIPE)
                stdout, stderr = process.communicate()
                fl = (stdout.split(b'\n')[0]).decode("utf-8")
                title = fl.replace('title:', '').strip()
                print("    * `%s` %s (#%s)" % (hash, title.capitalize(), number))