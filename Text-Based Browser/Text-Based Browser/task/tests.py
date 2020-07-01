from hstest.stage_test import StageTest
from hstest.test_case import TestCase
from hstest.check_result import CheckResult

import os
import shutil

from colorama import Fore

import sys
if sys.platform.startswith("win"):
    import _locale
    # pylint: disable=protected-access
    _locale._getdefaultlocale = (lambda *args: ['en_US', 'utf8'])

CheckResult.correct = lambda: CheckResult(True, '')
CheckResult.wrong = lambda feedback: CheckResult(False, feedback)


class TextBasedBrowserTest(StageTest):

    def generate(self):

        dir_for_files = os.path.join(os.curdir, 'tb_tabs')
        return [
            TestCase(
                stdin='2.python-requests.org\nexit',
                attach='requests',
                args=[dir_for_files]
            ),
            TestCase(
                stdin='en.wikipedia.org\nwiki\nexit',
                attach='Wikipedia',
                args=[dir_for_files]
            ),
            TestCase(
                stdin='nytimescom\nexit',
                args=[dir_for_files]
            ),
            TestCase(
                stdin='bloombergcom\nexit',
                args=[dir_for_files]
            ),
        ]

    def _check_files(self, path_for_tabs: str, right_word: str) -> bool:
        """
        Helper which checks that browser saves visited url in files and
        provides access to them.

        :param path_for_tabs: directory which must contain saved tabs
        :param right_word: Word-marker which must be in right tab
        :return: True, if right_words is present in saved tab
        """

        path, dirs, filenames = next(os.walk(path_for_tabs))

        for file in filenames:

            with open(os.path.join(path_for_tabs, file), 'r', encoding='utf-8') as tab:
                content = tab.read()

                if '</p>' not in content and '</script>' not in content:
                    if '</div>' not in content and right_word in content:
                        return True

        return False

    def check(self, reply, attach):

        # Incorrect URL
        if attach is None:
            if '<p>' in reply:
                return CheckResult.wrong('You haven\'t checked was URL correct')
            else:
                return CheckResult.correct()

        # Correct URL
        if isinstance(attach, str):
            right_word = attach

            path_for_tabs = os.path.join(os.curdir, 'tb_tabs')

            if not os.path.isdir(path_for_tabs):
                return CheckResult.wrong("There are no directory for tabs")

            if not self._check_files(path_for_tabs, right_word):
                return CheckResult.wrong('There are no correct saved tabs')

            try:
                shutil.rmtree(path_for_tabs)
            except PermissionError:
                return CheckResult.wrong("Impossible to remove the directory for tabs. Perhaps you haven't closed some file?")


            if not Fore.BLUE in reply:
                return CheckResult.wrong('There are no blue refs in output')

            if '</p>' not in reply and '</div>' not in reply:
                if right_word in reply:
                    return CheckResult.correct()

            return CheckResult.wrong('You haven\'t parsed result of request')


TextBasedBrowserTest('browser.browser').run_tests()
