#! /usr/bin/python2
# vim: set fileencoding=utf-8
import tasks
import nose.tools as must


class TestTask:
    def setUp(self):
        self.tasks = ['finnish', 'monde', 'bio', 'bold']

    def tearDown(self):
        pass

    def test_levenshtein(self):
        must.eq_(tasks._levenshtein("kitten",    ""),   len('kitten'))
        #from http://awk.freeshell.org/LevenshteinEditDistance
        must.eq_(tasks._levenshtein("kitten",    "sitting"),   3)
        must.eq_(tasks._levenshtein("Saturday",  "Sunday"),    3)
        must.eq_(tasks._levenshtein("acc",       "ac"),        1)
        must.eq_(tasks._levenshtein("foo",       "four"),      2)
        must.eq_(tasks._levenshtein("foo",       "foo"),       0)
        must.eq_(tasks._levenshtein("cow",       "cat"),       2)
        must.eq_(tasks._levenshtein("cat",       "moocow"),    5)
        must.eq_(tasks._levenshtein("cat",       "cowmoo"),    5)
        must.eq_(tasks._levenshtein("sebastian", "sebastien"), 1)
        must.eq_(tasks._levenshtein("more",      "cowbell"),   5)
        must.eq_(tasks._levenshtein("freshpack", "freshpak"),  1)
        must.eq_(tasks._levenshtein("freshpak",  "freshpack"), 1)

    def test_find_task(self):
        must.eq_(tasks.find_task('', []), '')
        must.eq_(tasks.find_task('req', []), 'req')
        must.eq_(tasks.find_task('finnish', self.tasks), 'finnish')
        must.eq_(tasks.find_task('monde', self.tasks), 'monde')
        must.eq_(tasks.find_task('m', self.tasks), 'monde')
        must.eq_(tasks.find_task('_', self.tasks), None)
