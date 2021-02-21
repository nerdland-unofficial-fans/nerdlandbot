Space_launches command uses an api with limited allowed calls per time.
To run tests while developing: run this simple http server on your own machine when testing space_launches command. Set the URL to the test URL: Comment out the production one.

By default, the port used will be 8000.

python -m http.server
python -m http.server 8080