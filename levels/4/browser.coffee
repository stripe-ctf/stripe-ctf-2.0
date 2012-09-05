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
  @fill "form", {username: 'karma_fountain', password: password}, true

casper.then ->
  # Log the page title.
  console.log "On the main page"

  page_title = @getTitle()
  page_url = @getCurrentUrl()
  console.log "Page title is: #{page_title} (url: #{page_url})"

  credits = @evaluate ->
    return document.querySelectorAll('p')[1].innerHTML

  credits_left = credits.match /-?\d+/
  console.log "Guard Llama has #{credits_left} credits left"

casper.run ->
  console.log "Running!"
  casper.exit 0
