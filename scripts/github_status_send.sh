curl "https://api.github.com/repos/threefoldtech/jumpscaleX/statuses/$1?access_token=$2" \
-H "Content-Type: application/json" \
-X POST \
-d "{\"state\": \"$3\", \"description\": \"JSX-machine for testing\", \"target_url\": \"$4\"}"
