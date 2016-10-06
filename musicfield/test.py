# ~ # -*- coding: utf-8 -*-

from django.test import TestCase

_running_test = False


class ExampleTestCase(TestCase):
    def setUp(self):
        print('setup')

    def tearDown(self):
        print('teardown')

    def test_something(self):
        """Animals that can speak are correctly identified"""
        print('it\'s really something')
