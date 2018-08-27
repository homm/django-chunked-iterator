# Django chunked iterator

Django provides a simple way to make complex queries.
Unfortunately, another side of the coin is
high memory consumption for really huge datasets.

The thing is that when you are getting an object from
[QuerySet](https://docs.djangoproject.com/en/2.1/ref/models/querysets/),
Django makes a query for all objects and makes model instances
for *all returned rows in memory*.
Even if you only need one object at a time.
Memory also will be consumed for holding result rows
in the database and in Python's database driver.

```python
for e in Entry.objects.all():
    print(e.headline)
```

There is a way to improve it:
[iterator](https://docs.djangoproject.com/en/2.1/ref/models/querysets/#iterator).

```python
for e in Entry.objects.iterator():
    print(e.headline)
```

In this way, Django will construct model instances
on the fly only for current iteration.
Depending on your database and settings,
Django can also get all rows from database in one query,
or it can use server-side cursors to get rows by chunks.

In the latter case (with server-side cursors),
only limited amount of memory will be consumed
in the database and in Python's database driver.
But this only works with certain databases
and without connection poolers (like [pgbouncer](https://pgbouncer.github.io)).
There is no way for your code to be sure that
the memory-efficient method is used.

## Design

This chunked iterator takes queryset and makes serial queries
returning fixed number of rows or model instances.
This allows iterating really huge amount of rows
with fixed memory consumption on the database,
Python's driver, and application layers.
As a side effect, the first portion of rows is returned much quicker,
which allows starting processing in parallel in some cases.

There is only one limitation: the model should have a unique field
which will be used for sorting and pagination.
For most cases, this is the primary key, but you can use other fields.

## Installing

```bash
$ pip install django-chunked-iterator
```

## Using

#### Iterate over `QuerySet` by chunks

```python
from django_chunked_iterator import batch_iterator

for entries in batch_iterator(Entry.objects.all()):
    for e in entries:
        print(e.headline)
```

#### Iterate over `QuerySet` by items

```python
from django_chunked_iterator import iterator

for e in iterator(Entry.objects.all()):
    print(e.headline)
```

#### Limit number of returned rows

WRONG!

```python
for e in iterator(Entry.objects.all()[:10000]):
    print(e.headline)
AssertionError: Cannot reorder a query once a slice has been taken.
```

Right:

```python
for e in iterator(Entry.objects.all(), limit=10000):
    print(e.headline)
```

#### Change batch size

The smaller batch size, the faster first item is returned, 
the larger overhead for additional queries.
Optimal values from 100 to 1000.

```python
for e in iterator(Entry.objects.all(), batch_size=150):
    print(e.headline)
```

#### Change ordering

Returns items in reverse creation order.
`created` field **should** have `uniquie=True`
(this is not hard when datetime has microseconds accuracy).

```python
for e in iterator(Entry.objects.all(), order_by='-created'):
    print(e.headline)
```


## Testing

```bash
$ pip install -r ./requirements.txt
$ ./test_project/manage.py test -v 2 --with-coverage --cover-package=django_chunked_iterator
```
