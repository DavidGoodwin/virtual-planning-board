#!/usr/bin/ruby
# This script attempts to import all previous tickets from a given 
# Trac repository into the Virtual Planner.
#
# Enrico Rubboli <rubboli@gmail.com>

require 'sqlite3'
require 'net/https'
require 'uri'

#configs
trac_base = "/home/trac"
trac_project = "test"
trac_http_base = "https://myhost/trac/#{trac_project}/"

#ping
ping_hostname = "myhostname"
ping_url = "/virtual-planner/ping/update.php"
ping_username="virtual"
ping_password="planner"


#execution
db_filename = "#{trac_base}/#{trac_project}/db/trac.db"
url = URI.parse("https://#{ping_username}:#{ping_password}@#{ping_hostname}#{ping_url}")
conn = Net::HTTP.new(url.hostname, (url.scheme=='https')  ? 443 : 80)
conn.use_ssl = (url.scheme=='https') ?true:false
conn.start

begin
 db=SQLite3::Database.new(db_filename)
 db.results_as_hash = true
 db.execute("SELECT id,component as project,owner,status,summary as title, description as desc FROM ticket") do | s |
        req = Net::HTTP::Post.new  ping_url
        req.set_form_data ({ "project"  => s["projet"],
                  "owner"       => s['owner'],
                  "status"      => s['status'],
                  "title"       => s['title'],
                  "trac_id"     => s['id'],
                  "ticket_url"  => "#{trac_http_base}/ticket/#{s['id']}",
                  "total_hours" => "0",
                  "estimated_hours" => "0",
                  "action"      => "created",
                  "desc"        => s['desc']
                })
        req.basic_auth ping_username, ping_password
        resp = conn.request req
 end
 db.close
 conn.close
rescue SQLite3::Exception => e
 puts "An error occurred: #{e}"
 puts "Uri: #{uri}"
end

