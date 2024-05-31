
export alias sf = python $"($env.PWD)/manage.py";
export alias db-pull-from-prod = sh $"($env.PWD)/scripts/local/pull-db-from-prod.sh";
export alias upgrade = sh $"($env.PWD)/scripts/server/upgrade.sh";
export alias db-backup = sh $"($env.PWD)/scripts/server/backup.sh";
export alias cache-warmup = sh $"($env.PWD)/scripts/server/cache_warmup.sh";
export alias enter-db = litecli $"($env.PWD)/db.sqlite";
export alias prod = ssh ubuntu@starfish-education.eu -A;
export alias h = display_help;
export def venv-upgrade [] {
  pip install -r $"($env.PWD)/requirements.txt"
}

export def serve [] {
  if ("/home/ubuntu/" | path exists) {
    sh $"($env.PWD)/scripts/server/serve.sh"
  } else {
    # task spawn {memcached -l localhost -p 11211} --label memcached
    sf runserver
  }
}

# export def memkill [] {
#   task log | where label == memcached | $in.id | each { |id| 
#     pueue kill $id
#     pueue remove $id
#   }
# }
  
export def display_help [] {
  mut dev = "  ---development--------------------------"

  if ("/home/ubuntu/" | path exists) {
    $dev = "  ---development--(you're-running-in-prod)"
  } 

  mut prod = "  ---production---------------------------"

  if ("/home/ubuntu/" | path exists) {
    $prod = "  ---production--(you're-running-in-prod)--"
  } 

  $"
You can use the following assist commands:
                                      
---django-------------------------------
sf                 short for python manage.py
sf check           check starfish configuration
sf makemigrations  create database migrations
sf migrate         run database migrations
                                      
---administrative-----------------------
serve              serve the application \(works on dev and prod)
enter-db           enter the database
venv-upgrade       install python requirements in venv
kill-process       kill a process by name

($dev)
                                            
prod               enter the production shell
db-pull-from-prod  overwrite local db with the one on prod

($prod)
upgrade            fetches the latest source code and restarts
db-backup          create a local backup of the database
cache-warmup       warms up the cache
                                        
---misc---------------------------------
h                  display this message again
                                        
  "
}
