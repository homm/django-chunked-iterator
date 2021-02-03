from __future__ import unicode_literals, absolute_import

from django.db.models import Model


MODEL_GETTER = lambda order_by: lambda item: getattr(item, order_by)
DICT_GETTER = lambda order_by: lambda item: item[order_by]
LIST_GETTER = lambda item: item[0]
FLAT_GETTER = lambda item: item


def batch_iterator(qs, batch_size=1000,
                   order_by='pk', start_with=None, limit=None):
    qs = qs.order_by(order_by)

    getter = None
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
            if not getter:
                getter = _detect_getter(last_item, order_by, qs)
            start_with = getter(last_item)
            yield items

        # If the number of returned items is less than requested
        if returned < batch_size or limit == 0:
            break


def iterator(qs, batch_size=1000, order_by='pk', start_with=None, limit=None):
    for batch in batch_iterator(qs, batch_size, order_by, start_with, limit):
        for item in batch:
            yield item


def _detect_getter(item, order_by, qs):
    getter = None
    try:
        if isinstance(item, (Model)) or (
                # Namedtuple aka Django Row case:
                isinstance(item, tuple) and hasattr(item, '_fields')):
            getter = MODEL_GETTER(order_by)

        elif isinstance(item, dict):
            getter = DICT_GETTER(order_by)

        elif isinstance(item, (list, tuple)):
            if not qs._fields or qs._fields[0] != order_by:
                raise IndexError()
            getter = LIST_GETTER

        elif isinstance(item, (str, int, float)):
            if not qs._fields or qs._fields[0] != order_by:
                raise IndexError()
            getter = FLAT_GETTER

        else:
            raise AttributeError()

        getter(item)  # Test getter on a real item.
        return getter

    except (AttributeError, KeyError, IndexError):
        raise ValueError(
            '`{0}` field should be in returned objects. '
            'Please add it to `.values()`'
            ' or `.values_list()` (and it should go first in the fields list)'
            ' or use different field as `order_by`.'.format(order_by))
