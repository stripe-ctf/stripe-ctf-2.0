#!/usr/bin/env ruby
require 'rubygems'
require 'bundler/setup'

require 'logger'
require 'uri'

require 'restclient'
require 'sinatra'

$log = Logger.new(STDERR)
$log.level = Logger::INFO

module DomainAuthenticator
  class DomainAuthenticatorSrv < Sinatra::Base
    set :environment, :production

    # Run with the production file on the server
    if File.exists?('production')
      PASSWORD_HOSTS = /^level05-\d+\.stripe-ctf\.com$/
      ALLOWED_HOSTS = /\.stripe-ctf\.com$/
    else
      PASSWORD_HOSTS = /^localhost$/
      ALLOWED_HOSTS = //
    end
    PASSWORD = File.read('password.txt').strip
    enable :sessions

    # Use persistent entropy file
    entropy_file = 'entropy.dat'
    unless File.exists?(entropy_file)
      File.open(entropy_file, 'w') do |f|
        f.write(OpenSSL::Random.random_bytes(24))
      end
    end
    set :session_secret, File.read(entropy_file)

    get '/*' do
      output = <<EOF
<p>
  Welcome to the Domain Authenticator. Please authenticate as a user from
  your domain of choice.
</p>

<form action="" method="POST">
<p>Pingback URL: <input type="text" name="pingback" /></p>
<p>Username: <input type="text" name="username" /></p>
<p>Password: <input type="password" name="password" /></p>
<p><input type="submit" value="Submit"></p>
</form>
EOF

      user = session[:auth_user]
      host = session[:auth_host]
      if user && host
        output += "<p> You are authenticated as #{user}@#{host}. </p>"
        if host =~ PASSWORD_HOSTS
          output += "<p> Since you're a user of a password host and all,"
          output += " you deserve to know this password: #{PASSWORD} </p>"
        end
      end

      output
    end

    post '/*' do
      pingback = params[:pingback]
      username = params[:username]
      password = params[:password]

      pingback = "http://#{pingback}" unless pingback.include?('://')

      host = URI.parse(pingback).host
      unless host =~ ALLOWED_HOSTS
        return "Host not allowed: #{host}" \
               " (allowed authentication hosts are #{ALLOWED_HOSTS.inspect})"
      end

      begin
        body = perform_authenticate(pingback, username, password)
      rescue StandardError => e
        return "An unknown error occurred while requesting #{pingback}: #{e}"
      end

      if authenticated?(body)
        session[:auth_user] = username
        session[:auth_host] = host
        return "Remote server responded with: #{body}." \
               " Authenticated as #{username}@#{host}!"
      else
        session[:auth_user] = nil
        session[:auth_host] = nil
        sleep(1) # prevent abuse
        return "Remote server responded with: #{body}." \
               " Unable to authenticate as #{username}@#{host}."
      end
    end

    def perform_authenticate(url, username, password)
      $log.info("Sending request to #{url}")
      response = RestClient.post(url, {:password => password,
                                       :username => username})
      body = response.body

      $log.info("Server responded with: #{body}")
      body
    end

    def authenticated?(body)
      body =~ /[^\w]AUTHENTICATED[^\w]*$/
    end
  end
end

def main
  DomainAuthenticator::DomainAuthenticatorSrv.run!
end

if $0 == __FILE__
  main
  exit(0)
end
