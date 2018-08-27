from __future__ import unicode_literals, absolute_import


def batch_iterator(qs, batch_size=1000,
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
            last_item = items[-1]
            try:
                start_with = getattr(last_item, order_by)
            except AttributeError:
                try:
                    start_with = last_item[order_by]
                except (KeyError, TypeError):
                    raise ValueError(
                        '`{0}` field should be in returned objects. '
                        'Please add it to `.values()` or `.values_list()` or '
                        'use different field as `order_by`.'.format(order_by))

            yield items

        # If the number of returned items is less than requested
        if returned < batch_size or limit == 0:
            break


def iterator(qs, batch_size=1000, order_by='pk', start_with=None, limit=None):
    for batch in batch_iterator(qs, batch_size, order_by, start_with, limit):
        for item in batch:
            yield item
