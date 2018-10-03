v1.0.3
======

Minor
-----
- Support for Django cache framework.
- Dropping support for Python 2 < 2.7, and Python 3 < 3.4.
- `etag`, `max_age`, and `expiry` can take functions.

Fixes
-----
- Fixed bug where Redis timeout sleep could be negative.


v1.0.2
======
- Use getfullargspec in Python 3.


v1.0.1
======
- Fixed bug where kwargs were not passed through.


v1.0.0
======

- Renamed `maxage` parameter to `max_age`.
- Methods can now be decorated.
- Partials can be created from decorated functions.


v0.1.1
======
- Python 3 compatibility.


v0.1.0
======
- Start of versioned history; first release.
