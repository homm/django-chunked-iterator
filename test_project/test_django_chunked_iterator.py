import random
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone
from django.test import TestCase

from django_chunked_iterator import iterator_batch, iterator

from test_project.models import Item


class DjangoChunkedIteratorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(DjangoChunkedIteratorTest, cls).setUpClass()

        N = 5000  # Number of test files
        now = timezone.now()
        offsets = list(range(N))
        random.shuffle(offsets)
        Item.objects.bulk_create([
            Item(created=now - timedelta(offsets[i]))
            for i in range(N)
        ])

    def test_batch_size(self):
        # default is 1000
        it = iterator_batch(Item.objects.all())
        for i, batch in enumerate(it):
            self.assertEqual(len(batch), 1000)
            if i > 3:
                break

        it = iterator_batch(Item.objects.all(), batch_size=11)
        for i, batch in enumerate(it):
            self.assertEqual(len(batch), 11)
            if i > 5:
                break

        it = iterator_batch(Item.objects.all(), 9)
        for i, batch in enumerate(it):
            self.assertEqual(len(batch), 9)
            if i > 5:
                break

    def test_order_by(self):
        # default is pk
        last_pk = None
        it = iterator_batch(Item.objects.all(), 9)
        for i, batch in enumerate(it):
            for item in batch:
                self.assertGreater(item.pk, last_pk)
                last_pk = item.pk
            if i > 9:
                break

        last_pk = 1e100
        it = iterator_batch(Item.objects.all(), 9, order_by='-pk')
        for i, batch in enumerate(it):
            for item in batch:
                self.assertLess(item.pk, last_pk)
                last_pk = item.pk
            if i > 9:
                break

        last_created = datetime.min
        it = iterator_batch(Item.objects.all(), 9, 'created')
        for i, batch in enumerate(it):
            for item in batch:
                self.assertGreater(item.created, last_created)
                last_created = item.created
            if i > 9:
                break

        last_created = datetime.max
        it = iterator_batch(Item.objects.all(), 9, '-created')
        for i, batch in enumerate(it):
            for item in batch:
                self.assertLess(item.created, last_created)
                last_created = item.created
            if i > 9:
                break
