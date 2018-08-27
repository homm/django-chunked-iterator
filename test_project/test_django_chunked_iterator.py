from __future__ import print_function, unicode_literals, division

import time
import math
import random
from datetime import datetime, timedelta

from django.utils import timezone
from django.test import TestCase
from parameterized import parameterized

from django_chunked_iterator import batch_iterator, iterator

from test_project.models import Item


class DjangoChunkedIteratorTest(TestCase):
    N = 7000  # Number of test files
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
        for batch in batch_iterator(self.qs, limit=limit):
            self.assertIn(len(batch), batch_sizes)
            count += len(batch)
        self.assertEqual(count, total)

    def test_batch_size(self):
        with self.assertNumQueries(3):
            for batch in batch_iterator(self.qs, batch_size=11, limit=33):
                self.assertEqual(len(batch), 11)

        with self.assertNumQueries(math.ceil(self.N / 345)):
            for batch in batch_iterator(self.qs, 345):
                self.assertIn(len(batch), (345, self.N % 345))

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

    def test_first_start_time(self):
        start = time.time()
        for item in self.qs.all():
            break
        default_time = time.time() - start

        start = time.time()
        for item in self.qs.iterator():
            break
        iterator_time = time.time() - start

        start = time.time()
        for item in iterator(self.qs, 100):
            break
        chunked_iterator_time = time.time() - start

        print('>>> Default', default_time)
        print('>>> Iterator', iterator_time)
        print('>>> Chunked iterator', chunked_iterator_time)

        self.assertLess(chunked_iterator_time * 10, iterator_time)
        self.assertLess(chunked_iterator_time * 20, default_time)

    def test_total_time(self):
        start = time.time()
        for item in self.qs.all():
            pass
        default_time = time.time() - start

        start = time.time()
        for item in self.qs.iterator():
            pass
        iterator_time = time.time() - start

        start = time.time()
        for item in iterator(self.qs, 200):
            pass
        chunked_iterator_time = time.time() - start

        print('>>> Default', default_time)
        print('>>> Iterator', iterator_time)
        print('>>> Chunked iterator', chunked_iterator_time)

        self.assertLess(chunked_iterator_time, iterator_time * 1.6)
        self.assertLess(chunked_iterator_time, default_time * 1.6)

