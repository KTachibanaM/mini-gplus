# mini-gplus

An 8-hour worth of mini Google+ clone

## Dependencies

* Database: MongoDB
    * Production
        * Set `MONGODB_URI` env var
    * Local dev
        * `MONGODB_URI=mongodb://localhost:27017/minigplus`
    
* Storage: configurable via [flask-cloudy](https://github.com/mardix/flask-cloudy)
    * Production
        * Read [flask-cloudy README](https://github.com/mardix/flask-cloudy/blob/master/README.md)
        * Set `STORAGE_PROVIDER`, `STORAGE_KEY`, `STORAGE_SECRET`, `STORAGE_CONTAINER` env vars
    * Local dev
        * `STORAGE_PROVIDER=LOCAL`
        * `STORAGE_CONTAINER=./uploads`
        * `STORAGE_SERVER=False`