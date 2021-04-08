#! /usr/bin/env sh
set -e

migrate () {
  echo "Migrating database"
  echo "..."
  alembic upgrade head
  status=$?
  if [ $status -ne 0 ]; then
    echo "Failed to migrate database: $status"
    exit $status
  fi
  python tool/seed_data/seed_data_for_review.py
}

start_api () {
  migrate
  # Start Supervisor, with Nginx and uWSGI
  exec /usr/bin/supervisord
}

start_worker () {
  python run_worker.py --worker $1
}

case $1 in
  "api")
    start_api
    ;;

  "worker")
    if [[ ! -z "$2" ]]
    then
      start_worker $2
    else
      echo "Usage: ./start.sh worker <worker-name>"
    fi
    ;;

  *)
    echo "Usage: ./start.sh api|worker"
    ;;
esac
