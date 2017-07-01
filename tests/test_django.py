import memoize.djangocache

import django
from django.test import TestCase
from django.core.cache import caches


class DjangoTest(TestCase):
    @classmethod
    def setUpClass(cls):
        from django.test.utils import setup_test_environment
        from django.core.management import call_command

        from django.conf import settings
        """
        This is mandatory to spin up django
        """
        settings.configure(
            INSTALLED_APPS=[],
            DATABASES={
                'default': {
                    'NAME': ':memory:', 'ENGINE': 'django.db.backends.sqlite3'}
            },
        )
        django.setup()
        setup_test_environment()
        super(DjangoTest, cls).setUpClass()

    def test_can_memoize_using_django_cache(self):
        cache = caches['default']

        def f(number):
            return number

        store = memoize.djangocache.Cache('default')
        memo = memoize.Memoizer(store)

        self.assertFalse(store.exists('test'))

        r = memo.get('test', f, (1,), max_age=16)

        self.assertEqual(r, 1)
        self.assertEqual(cache.get('test')[-1], 1)
        self.assertTrue(store.exists('test'))
