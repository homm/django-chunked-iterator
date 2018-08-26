import random
from datetime import datetime, timedelta

from django.utils import timezone
from django.test import TestCase
from nose_parameterized import parameterized

from django_chunked_iterator import iterator_batch, iterator

from test_project.models import Item


class DjangoChunkedIteratorTest(TestCase):
    N = 5000  # Number of test files
    qs = Item.objects.all()

    @classmethod
    def setUpClass(cls):
        super(DjangoChunkedIteratorTest, cls).setUpClass()

        now = timezone.now()
        offsets = list(range(cls.N))
        random.shuffle(offsets)
        Item.objects.bulk_create([
            Item(created=now - timedelta(offsets[i]))
            for i in range(cls.N)
        ])

    @parameterized.expand([
        (None, (1000,), N),  # No limit
        (N*2, (1000,), N),  # Huge limit
        (N, (1000,), N),  # Exact limit
        (2000, (1000,), 2000),  # Smaller limit
        (2333, (1000, 333), 2333),  # Smaller limit
        (333, (333,), 333),  # Small limit
    ])
    def test_limit(self, limit, batch_sizes, total):
        count = 0
        for batch in iterator_batch(self.qs, limit=limit):
            self.assertIn(len(batch), batch_sizes)
            count += len(batch)
        self.assertEqual(count, total)

    def test_batch_size(self):
        for batch in iterator_batch(self.qs, batch_size=11, limit=33):
            self.assertEqual(len(batch), 11)

        for batch in iterator_batch(self.qs, 345):
            self.assertIn(len(batch), (345, 170))

    def test_order_by(self):
        # default is pk
        last_pk = 0
        for item in iterator(self.qs, 9, limit=100):
            self.assertEqual(item.pk - last_pk, 1)
            last_pk = item.pk

        last_pk = 1e100
        for item in iterator(self.qs, 9, order_by='-pk', limit=100):
            self.assertLess(item.pk, last_pk)
            last_pk = item.pk

        last_created = datetime.min
        for item in iterator(self.qs, 9, 'created', limit=100):
            self.assertGreater(item.created, last_created)
            last_created = item.created

        last_created = datetime.max
        for item in iterator(self.qs, 9, '-created', limit=100):
            self.assertLess(item.created, last_created)
            last_created = item.created

    def test_start_with(self):
        last_pk = 333
        for item in iterator(self.qs, 9, start_with=last_pk, limit=100):
            self.assertEqual(item.pk - last_pk, 1)
            last_pk = item.pk

        last_pk = 333
        for item in iterator(self.qs, 9, '-pk', last_pk, limit=100):
            self.assertEqual(item.pk - last_pk, -1)
            last_pk = item.pk

