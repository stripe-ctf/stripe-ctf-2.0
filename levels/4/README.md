# Level 4

The Karma Trader is the world's best way to reward people for good deeds. You
can sign up for an account, and start transferring karma to people who you
think are doing good in the world. In order to ensure you're transferring karma
only to good people, transferring karma to a user will also reveal your
password to him or her.

The very active user **karma_fountain** has infinite karma, making it a ripe
account to obtain (no one will notice a few extra karma trades here and there).
The password for **karma_fountain**'s account will give you access to Level 5.

# To run

- Install bundler: `gem install bundler`
- Run srv.rb: `./srv.rb`
- Point your browser to [http://localhost:4567](http://localhost:4567)

## Karma Fountain

We used [CapserJS](http://casperjs.org/) on top of
[PhantomJS](http://phantomjs.org/) to power the **karma_fountain** user. Run
`capserjs browser.coffee http://localhost:4567` to start it up. It expects to
find the password from the filesystem `public_html/password.txt`.
