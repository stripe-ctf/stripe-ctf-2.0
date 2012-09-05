# Level 5

Many attempts have been made at creating a federated identity system for the
web (see [OpenID](http://openid.net/), for example). However, none of them have
been successful. Until today.

The DomainAuthenticator is based off a novel protocol for establishing
identities. To authenticate to a site, you simply provide it username,
password, and pingback URL. The site posts your credentials to the pingback
URL, which returns either "AUTHENTICATED" or "DENIED". If "AUTHENTICATED", the
site considers you signed in as a user for the pingback domain.

We've been using the Stripe CTF DomainAuthenticator instance it to distribute
the password to access Level 6. If you could only somehow authenticate as a
user of a level05 machine...

To avoid nefarious exploits, the machine hosting the DomainAuthenticator has
very locked down network access. It can only make outbound requests to other
`stripe-ctf.com` servers. Though, you've heard that someone forgot to
internally firewall off the high ports from the Level 2 server.

*NB: During the actual Stripe CTF, we allowed full network access from the
Level 5 server to the Level 2 server.*

# To run

- Install bundler: `gem install bundler`
- Run srv.rb: `./srv.rb`
- Point your browser to [http://localhost:4567](http://localhost:4567)
