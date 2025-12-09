from flask import Flask, render_template, redirect, url_for
import requests

app = Flask(__name__)

API_BASE_URL = "http://localhost:3000"  # Adjust the base URL as needed

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/docs")
def docs():
    response = requests.get(f"{API_BASE_URL}/books-api.yaml")
    if response.status_code == 200:
        return render_template("docs.html", api_spec=response.text)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)