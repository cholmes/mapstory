Enabling Time
.............

A feature can currently support one or two time attributes. If a single
attribute is used, the feature is considered relevant at that single point in time. If two
attributes are used, the second attribute represents the end of a valid period for the
feature.

Selecting An Attribute
......................

A time attribute can be one of:

* An existing date
* Text that can be converted to a timestamp
* A number representing a year

For text attributes, one can specify a custom format or use the 'best guess' approach.
The most common formatting flags are:

* ``y`` year
* ``M`` month
* ``d`` day of month
* ``H`` hour of day (0-23)
* ``k`` hour of day (1-24)
* ``m`` minute in hour
* ``s`` second in minute

.. note::
   :class: alert alert-info
   
   Note that single quotes represent a literal character.

.. note::
   :class: alert alert-info
   
   To remove ambiguity, repeat a code to represent the maximum number of digits - for example yyyy


The 'best guess' will handle date and optional time variants of `ISO-8601 <http://en.wikipedia.org/wiki/ISO_8601>`_
In terms of the formatting flags noted above, these are: ::

    yyyy-MM-dd'T'HH:mm:ss.SSS'Z'
    yyyy-MM-dd'T'HH:mm:sss'Z'
    yyyy-MM-dd'T'HH:mm:ss'Z'
    yyyy-MM-dd'T'HH:mm'Z'
    yyyy-MM-dd'T'HH'Z'
    yyyy-MM-dd
    yyyy-MM
    yyyy