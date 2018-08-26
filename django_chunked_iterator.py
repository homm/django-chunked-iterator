from __future__ import unicode_literals, absolute_import


def iterator_batch(qs, batch_size=1000,
                   order_by='pk', start_with=None, limit=None):
    qs = qs.order_by(order_by)

    cond = order_by + '__gt'
    if order_by.startswith('-'):
        order_by = order_by[1:]
        cond = order_by + '__lt'

    while True:
        if limit is not None and batch_size > limit:
            batch_size = limit

        local_qs = qs
        if start_with is not None:
            local_qs = qs.filter(**{cond: start_with})
        # Make query explicitly
        items = list(local_qs[:batch_size])
        returned = len(items)

        if limit is not None:
            limit -= returned
        if returned:
            start_with = getattr(items[-1], order_by)

            yield items

        # If the number of returned items is less than requested
        if returned < batch_size or limit == 0:
            break


def iterator(qs, batch_size=1000, order_by='pk', start_with=None, limit=None):
    for batch in iterator_batch(qs, batch_size, order_by, start_with, limit):
        for item in batch:
            yield item
