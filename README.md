# mini-gplus

An 8-hour worth of mini Google+ clone

## Run without Docker

Python 3.7.0

Node.js && Yarn

Have a MongoDB running locally at `mongodb://localhost:27017`

```bash
# Run server
pip install -r requirements.txt
FLASK_ENVIRONMENT=development python app.py

# Run web frontend
cd web
yarn start
```

View web frontend at [`http://localhost:3000`](http://localhost:3000/)
View server at [`http://localhost:5000`](http://localhost:5000/)