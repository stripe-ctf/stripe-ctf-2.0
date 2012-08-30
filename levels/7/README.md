# WaffleCopter

WaffleCopter delivers hot waffles fresh off the iron straight to your location
using quad-rotor GPS-enabled helicopters. The service is currently being tested
in private beta in select locations.

Your goal is to order one of the decadent Liège waffles, offered only to the
first premium subscribers of the service.

## The API

The WaffleCopter API is quite simple. All users have a secret API token that is
used to sign POST requests to /v1/orders. Parameters such as the waffle product
code and target GPS coordinates are encoded as if for a query string and placed
in the request body.

## The Code

You can use `client.py` to talk to the API, specifying an appropriate API
endpoint, user id, and secret key. The app itself is `wafflecopter.py`, which
will use a SQLite database created by `initialize_db.py`. To edit flask
settings, just create a `local_settings.py` file. The page templates can be
found under `templates/`.

The provided API client requires the `requests` module, which can be installed
from pip with `pip install requests`. The server requires modules `flask` and
`bcrypt`, which can be installed from pip with `pip install flask py-bcrypt`.
