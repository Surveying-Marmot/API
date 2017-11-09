import os
from app import app, db

db.create_all()

app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT')))