from .common import *


class TestCore(TestCase):

    def test_get(self):
        self.assertFalse(self.memo.exists('key'))
        self.assertEqual(self.memo.get('key', self.append_args), 1)
        self.assertTrue(self.memo.exists('key'))
        self.assertEqual(self.memo.get('key', self.append_args), 1)

    def test_max_age(self):
        self.assertEqual(self.memo.get('key', self.append_args, max_age=1), 1)
        self.assertTrue(self.memo.exists('key'))
        sleep(2)
        self.assertFalse(self.memo.exists('key'))
        self.assertEqual(self.memo.get('key', self.append_args, max_age=1), 2)

    def test_ttl(self):
        self.memo.get('key', self.append_args, max_age=2)
        self.assertAlmostEqual(self.memo.ttl('key'), 2, 2)
        sleep(1)
        self.assertAlmostEqual(self.memo.ttl('key'), 1, 2)
        sleep(2)
        self.assertAlmostEqual(self.memo.ttl('key') or 0, 0, 2)
        self.assertFalse(self.memo.exists('key'))


    def test_static_etag(self):

        assert self.memo.get('key', self.append_args) == 1
        assert self.memo.etag('key') is None

        assert self.memo.get('key', self.append_args, etag='a') == 2
        assert self.memo.etag('key') == 'a'

        assert self.memo.get('key', self.append_args, etag='b') == 3
        assert self.memo.etag('key') == 'b'

        # It does not go up here.
        assert self.memo.get('key', self.append_args) == 3

    