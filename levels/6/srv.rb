#!/usr/bin/env ruby
require 'rubygems'
require 'bundler/setup'

require 'rack/utils'
require 'rack/csrf'
require 'json'
require 'sequel'
require 'sinatra'

module Streamer
  PASSWORD = File.read('password.txt').strip

  # Only needed in production
  URL_ROOT = File.read('url_root.txt').strip rescue ''

  module DB
    def self.db_file
      'streamer.db'
    end

    def self.conn
      @conn ||= Sequel.sqlite(db_file)
    end

    def self.safe_insert(table, key_values)
      key_values.each do |key, value|
        # Just in case people try to exfiltrate
        # level07-password-holder's password
        if value.kind_of?(String) &&
            (value.include?('"') || value.include?("'"))
          raise "Value has unsafe characters"
        end
      end

      conn[table].insert(key_values)
    end

    def self.init
      return if File.exists?(db_file)
      File.umask(0066)

      conn.create_table(:users) do
        primary_key :id
        String :username
        String :password
        Time :last_active
      end

      conn.create_table(:posts) do
        primary_id :id
        String :user
        String :title
        String :body
        Time :time
      end

      conn[:users].insert(:username => 'level07-password-holder',
        :password => Streamer::PASSWORD,
        :last_active => Time.now.utc)

      conn[:posts].insert(:user => 'level07-password-holder',
        :title => 'Hello World',
        :body => "Welcome to Streamer, the most streamlined way of sharing
updates with your friends!

One great feature of Streamer is that no password resets are needed. I, for
example, have a very complicated password (including apostrophes, quotes, you
name it!). But I remember it by clicking my name on the right-hand side and
seeing what my password is.

Note also that Streamer can run entirely within your corporate firewall. My
machine, for example, can only talk directly to the Streamer server itself!",
        :time => Time.now.utc)
    end
  end

  class StreamerSrv < Sinatra::Base
    set :environment, :production
    enable :sessions

    # Use persistent entropy file
    entropy_file = 'entropy.dat'
    unless File.exists?(entropy_file)
      File.open(entropy_file, 'w') do |f|
        f.write(OpenSSL::Random.random_bytes(24))
      end
    end
    set :session_secret, File.read(entropy_file)

    use Rack::Csrf, :raise => true

    helpers do
      def absolute_url(path)
        Streamer::URL_ROOT + path
      end

      # Insert an hidden tag with the anti-CSRF token into your forms.
      def csrf_tag
        Rack::Csrf.csrf_tag(env)
      end

      # Return the anti-CSRF token
      def csrf_token
        Rack::Csrf.csrf_token(env)
      end

      # Return the field name which will be looked for in the requests.
      def csrf_field
        Rack::Csrf.csrf_field
      end

      include Rack::Utils
      alias_method :h, :escape_html
    end

    def redirect(url)
      super(absolute_url(url))
    end

    before do
      @user = logged_in_user
      update_last_active
    end

    def logged_in_user
      if session[:user]
        @username = session[:user]
        @user = DB.conn[:users][:username => @username]
      end
    end

    def update_last_active
      return unless @user
      DB.conn[:users].where(:username => @user[:username]).
        update(:last_active => Time.now.utc)
    end

    def recent_posts
      # Grab the 5 most recent posts
      DB.conn[:posts].reverse_order(:time).limit(5).to_a.reverse
    end

    def registered_users
      DB.conn[:users].reverse_order(:id)
    end

    def die(msg, view)
      @error = msg
      halt(erb(view))
    end

    get '/' do
      if @user
        @registered_users = registered_users
        @posts = recent_posts

        erb :home
      else
        erb :login
      end
    end

    get '/register' do
      erb :register
    end

    post '/register' do
      username = params[:username]
      password = params[:password]
      unless username && password
        die("Please specify both a username and a password.", :register)
      end

      unless DB.conn[:users].where(:username => username).count == 0
        die("This username is already registered. Try another one.",
            :register)
      end

      DB.safe_insert(:users,
        :username => username,
        :password => password,
        :last_active => Time.now.utc
        )
      session[:user] = username
      redirect '/'
    end

    get '/login' do
      redirect '/'
    end

    post '/login' do
      username = params[:username]
      password = params[:password]
      user = DB.conn[:users][:username => username, :password => password]
      unless user
        die('Could not authenticate. Perhaps you meant to register a new' \
            ' account? (See link below.)', :login)
      end

      session[:user] = user[:username]
      redirect '/'
    end

    get '/logout' do
      session.clear
      redirect '/'
    end

    get '/user_info' do
      @password = @user[:password]

      erb :user_info
    end

    before '/ajax/*' do
      halt(403, 'Must be logged in!') unless @user
    end

    get '/ajax/posts' do
      recent_posts.to_json
    end

    post '/ajax/posts' do
      msg = create_post
      resp = {:response => msg}
      resp.to_json
    end

    # Fallback if JS breaks
    get '/posts' do
      redirect '/'
    end

    post '/posts' do
      create_post if @user
      redirect '/'
    end

    def create_post
      post_body = params[:body]
      title = params[:title] || 'untitled'
      if post_body
        DB.safe_insert(:posts,
          :user => @user[:username],
          :title => title,
          :body => post_body,
          :time => Time.now.utc
          )
        'Successfully added the post!'
      else
        'No post body given!'
      end
    end
  end
end

def main
  Streamer::DB.init
  Streamer::StreamerSrv.run!
end

if $0 == __FILE__
  main
  exit(0)
end
