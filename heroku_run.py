from app import app
from db_toolkit import create_db

create_db()

app.run(debug=True)