# Level 8

Welcome to the final level, Level 8.

HINT 1: No, really, we're not looking for a timing attack.

HINT 2: Running the server locally is probably a good place to start. Anything
interesting in the output?

Because password theft has become such a rampant problem, a
security firm has decided to create PasswordDB, a new and secure way
of storing and validating passwords. You've recently learned that the
Flag itself is protected in a PasswordDB instance.

PasswordDB exposes a simple JSON API. You just `POST` a payload of the form
`{"password": "password-to-check", "webhooks": ["mysite.com:3000", ...]}` to
PasswordDB, which will respond with a `{"success": true}"` or
`{"success": false}"` to you and your specified webhook endpoints.

(For example, try running `curl <%= url %> -d '{"password": "password-to-check", "webhooks": []}'`.)

In PasswordDB, the password is never stored in a single location or process,
making it the bane of attackers' respective existences. Instead, the password
is "chunked" across multiple processes, called "chunk servers". These may live
on the same machine as the HTTP-accepting "primary server", or for added
security may live on a different machine. PasswordDB comes with built-in
security features such as timing attack prevention and protection against using
unequitable amounts of CPU time (relative to other PasswordDB instances on the
same machine).

As a secure cherry on top, the machine hosting the primary server has very
locked down network access. It can only make outbound requests to other
`stripe-ctf.com` servers. As you learned in Level 5, someone forgot to
internally firewall off the high ports from the Level 2 server. (It's almost
like someone on the inside is helping you &mdash; there's an
[sshd](http://linux.about.com/od/commands/l/blcmdl8_sshd.htm) running on the
Level 2 server as well.)

*NB: During the actual Stripe CTF, the Level 8 server could access all high TCP
ports on the Level 2 server, and the Level 2 server was running an SSHD.*

To maximize adoption, usability is also a goal of PasswordDB. Hence a launcher
script, `password_db_launcher`, has been created for the express purpose of
securing the Flag. It validates that your password looks like a valid Flag and
automatically spins up 4 chunk servers and a primary server.

# Run

- Run `password_db_launcher`. For example:

    ./password_db_launcher 123456789012 127.0.0.1:3000

  will start a PasswordDB instance running on 127.0.0.1:3000 and with
  the Flag set to 123456789012.

- Make sure you're using Twisted 11.1.0

- Connect using curl:

    curl 127.0.0.1:3000 -d '{"password": 123456789012, "webhooks": []}'
