from flask import Flask, render_template, request, session, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change this for production
app.config["SESSION_TYPE"] = "filesystem"

def get_auth_headers(pat):
    """Return headers for Jira authentication."""
    return {
        "Authorization": f"Bearer {pat}",
        "Content-Type": "application/json"
    }

def test_jira_connection(jira_url, pat):
    """Test the connection by hitting the server info endpoint."""
    test_url = f"{jira_url}/rest/api/2/serverInfo"
    try:
        response = requests.get(test_url, headers=get_auth_headers(pat), timeout=10)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def fetch_all_projects(jira_url, pat):
    """Fetch all Jira projects."""
    projects_url = f"{jira_url}/rest/api/2/project"
    try:
        response = requests.get(projects_url, headers=get_auth_headers(pat), timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            flash(f"Error fetching projects: {response.status_code}", "danger")
            return []
    except Exception as e:
        flash(f"Exception fetching projects: {e}", "danger")
        return []

@app.route("/", methods=["GET", "POST"])
def login():
    """Login page for Jira authentication."""
    if request.method == "POST":
        jira_url = request.form["jira_url"].strip()
        pat = request.form["pat"].strip()
        
        if test_jira_connection(jira_url, pat):
            session["jira_url"] = jira_url
            session["pat"] = pat
            flash("✅ Connected to Jira successfully!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("❌ Connection failed! Check your Jira details.", "danger")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    """Dashboard that fetches and displays all Jira projects."""
    if "jira_url" not in session or "pat" not in session:
        flash("⚠️ Please log in first.", "warning")
        return redirect(url_for("login"))
    
    jira_url = session["jira_url"]
    pat = session["pat"]
    projects = fetch_all_projects(jira_url, pat)
    
    return render_template("dashboard.html", projects=projects, jira_url=jira_url)

@app.route("/logout")
def logout():
    """Log out and clear the session."""
    session.clear()
    flash("🔒 Logged out successfully!", "info")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
