# Level 6

After Karma Trader from Level 4 was hit with massive karma inflation
(purportedly due to someone flooding the market with massive quantities of
karma), the site had to close its doors. All hope was not lost, however, since
the technology was acquired by a real up-and-comer, Streamer. Streamer is the
self-proclaimed most steamlined way of sharing updates with your friends.

The Streamer engineers, realizing that security holes had led to the demise of
Karma Trader, have greatly beefed up the security of their application. Which
is really too bad, because you've learned that the holder of the password to
access Level 7, **level07-password-holder**, is the first Streamer user.

In addition, **level07-password-holder** is taking a lot of precautions: his or
her computer has no network access besides the Streamer server itself, and his
or her password is a complicated mess, including quotes and apostrophes and the
like.

Fortunately for you, the Streamer engineers have decided to open-source their
application so that other people can run their own Streamer instances.

# To run

- Install bundler: `gem install bundler`
- Run srv.rb: `./srv.rb`
- Point your browser to [http://localhost:4567](http://localhost:4567)

## level07-password-holder

We used [CapserJS](http://casperjs.org/) on top of
[PhantomJS](http://phantomjs.org/) to power the **level07-password-holder**
user. Run `capserjs browser.coffee http://localhost:4567` to start it up. It
expects to find the password from the filesystem `public_html/password.txt`.
