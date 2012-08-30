#!/usr/bin/env ruby
require 'yaml'
require 'set'

require 'rubygems'
require 'bundler/setup'

require 'sequel'
require 'sinatra'

module KarmaTrader
  PASSWORD = File.read('password.txt').strip
  STARTING_KARMA = 500
  KARMA_FOUNTAIN = 'karma_fountain'

  # Only needed in production
  URL_ROOT = File.read('url_root.txt').strip rescue ''

  module DB
    def self.db_file
      'karma.db'
    end

    def self.conn
      @conn ||= Sequel.sqlite(db_file)
    end

    def self.init
      return if File.exists?(db_file)
      File.umask(0066)

      conn.create_table(:users) do
        primary_key :id
        String :username
        String :password
        Integer :karma
        Time :last_active
      end

      conn.create_table(:transfers) do
        primary_id :id
        String :from
        String :to
        Integer :amount
      end

      # Karma Fountain has infinite karma, so just set it to -1
      conn[:users].insert(
        :username => KarmaTrader::KARMA_FOUNTAIN,
        :password => KarmaTrader::PASSWORD,
        :karma => -1,
        :last_active => Time.now.utc
        )
    end
  end

  class KarmaSrv < Sinatra::Base
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

    helpers do
      def absolute_url(path)
        KarmaTrader::URL_ROOT + path
      end
    end

    # Hack to make this work with a URL root
    def redirect(url)
      super(absolute_url(url))
    end

    def die(msg, view)
      @error = msg
      halt(erb(view))
    end

    before do
      refresh_state
      update_last_active
    end

    def refresh_state
      @user = logged_in_user
      @transfers = transfers_for_user
      @trusts_me = trusts_me
      @registered_users = registered_users
    end

    def update_last_active
      return unless @user
      DB.conn[:users].where(:username => @user[:username]).
        update(:last_active => Time.now.utc)
    end

    def logged_in_user
      return unless username = session[:user]
      DB.conn[:users][:username => username]
    end

    def transfers_for_user
      return [] unless @user

      DB.conn[:transfers].where(
        Sequel.or(:from => @user[:username], :to => @user[:username])
        )
    end

    def trusts_me
      trusts_me = Set.new
      return trusts_me unless @user

      # Get all the users who have transferred credits to me
      DB.conn[:transfers].where(:to => @user[:username]).
        join(:users, :username => :from).each do |result|
        trusts_me.add(result[:username])
      end

      trusts_me
    end

    def registered_users
      KarmaTrader::DB.conn[:users].reverse_order(:id)
    end

    # KARMA_FOUNTAIN gets all the karma it wants. (Part of why getting
    # its password would be so great...)
    def user_has_infinite_karma?
      @user[:username] == KARMA_FOUNTAIN
    end

    get '/' do
      if @user
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

      unless username =~ /^\w+$/
        die("Invalid username. Usernames must match /^\w+$/", :register)
      end

      unless DB.conn[:users].where(:username => username).count == 0
        die("This username is already registered. Try another one.",
            :register)
      end

      DB.conn[:users].insert(
        :username => username,
        :password => password,
        :karma => STARTING_KARMA,
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

    get '/transfer' do
      redirect '/'
    end

    post '/transfer' do
      redirect '/' unless @user

      from = @user[:username]
      to = params[:to]
      amount = params[:amount]

      die("Please fill out all the fields.", :home) unless amount && to
      amount = amount.to_i
      die("Invalid amount specified.", :home) if amount <= 0
      die("You cannot send yourself karma!", :home) if to == from
      unless DB.conn[:users][:username => to]
        die("No user with username #{to.inspect} found.", :home)
      end

      unless user_has_infinite_karma?
        if @user[:karma] < amount
          die("You only have #{@user[:karma]} karma left.", :home)
        end
      end

      DB.conn[:transfers].insert(:from => from, :to => to, :amount => amount)
      DB.conn[:users].where(:username=>from).update(:karma => :karma - amount)
      DB.conn[:users].where(:username=>to).update(:karma => :karma + amount)

      refresh_state
      @success = "You successfully transfered #{amount} karma to" +
                 " #{to.inspect}."
      erb :home
    end

    get '/logout' do
      session.clear
      redirect '/'
    end
  end
end

def main
  KarmaTrader::DB.init
  KarmaTrader::KarmaSrv.run!
end

if $0 == __FILE__
  main
  exit(0)
end
