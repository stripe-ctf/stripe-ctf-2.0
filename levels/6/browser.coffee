# Install instructions:
#   - Install phantomjs 1.5+
#     - wget http://phantomjs.googlecode.com/files/phantomjs-1.6.1-linux-x86_64-dynamic.tar.bz2
#     - tar -xjvf phantomjs-1.6.1-linux-x86_64-dynamic.tar.bz2
#     - ln -s phantomjs-1.6.1-linux-x86_64-dynamic/bin/phantomjs /usr/bin/local
#   - Install casperjs
#     - git clone git://github.com/n1k0/casperjs.git
#     - cd casperjs
#     - git checkout tags/1.0.0-RC1
#     - ln -sf `pwd`/bin/casperjs /usr/local/bin/casperjs
#   - Run it!
#     - casperjs browser.coffee http://level04.stripe-ctf.com/
#     - (change above path to match the actual CTF path)
#
# Will exit(0) if success, exit(other) if failure
# Profit!

casper = require('casper').create()
system = require 'system'
utils = require 'utils'
fs = require 'fs'


if not casper.cli.has(0)
    console.log 'Usage: browser.coffee <url to visit>'
    casper.exit 1

password = fs.open('public_html/password.txt', 'r').read().trim()

page_address = casper.cli.get(0)
console.log "Page address is: #{page_address}"

casper.start page_address, ->
  # Fill and submit the login form
  console.log 'Filling the login form...'
  @fill "form", {username: 'level07-password-holder', password: password}, true

casper.then ->
  # Log the page title.
  console.log "On the main page"

  page_title = @getTitle()
  page_url = @getCurrentUrl()
  console.log "Before posting title is: #{page_title} (url: #{page_url})"

  # TODO: maybe make a post sometimes?
  h3 = @evaluate ->
    return document.querySelectorAll('h3')[0].innerHTML

  console.log "First h3 has contents #{h3}"

  titles = ['Important update', 'Very important update', 'An update', 'An FYI',
            'FYI', 'Did you know...', 'Possibly of interest', 'Definitely of interest',
            "You probably don't care but...", 'Because I feel like posting', 'Note',
            "You probably don't know", 'Guess what?', 'Might want to take note', 'A really cool update']
  bodies = ['I am hungry', 'Anyone want to play tennis?', 'Up for some racquetball?',
            'Hey!', "I'm bored. Anyone want to play a game?", 'Ooh, I think I found something',
            'Why is it so hard to find good juice restaurants?', 'You should all invite your friends to join Streamer!',
            'Why is everyone trying to exploit Streamer?', 'Streamer is *soo* secure',
            'Welcome!', 'Glad to have you here!', "I know what you're doing right now. You are reading this message."]

  # Post infrequently
  if Math.random() < 0.05
    console.log "Decided to post"
    title = titles[Math.floor(Math.random() * titles.length)]
    body = bodies[Math.floor(Math.random() * bodies.length)]
    @fill "form#new_post", {title: title, body: body}, true
  else
    console.log "Decided not to post"

casper.then ->
  page_title = @getTitle()
  page_url = @getCurrentUrl()
  console.log "After posting title is: #{page_title} (url: #{page_url})"

casper.run ->
  console.log "Running!"
  casper.exit 0
