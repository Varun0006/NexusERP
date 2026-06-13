# Import the main application factory from the app package
from app import create_app

# Instantiate the Flask application object
app = create_app()

if __name__ == "__main__":
    # Start the local development web server on port 5000
    app.run(debug=True, host="0.0.0.0", port=5000)
