"""Tests for ArangoDB Monitoring."""

import unittest

from arango import Arango


class MonitoringTest(unittest.TestCase):

    def setUp(self):
        self.arango = Arango()

    def test_get_log(self):
        self.arango.read_log()

    def test_get_statistics(self):
        self.arango.statistics()

    def test_get_server_role(self):
        self.arango.role()


if __name__ == "__main__":
    unittest.main()
