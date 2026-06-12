from flask import Flask, render_template, request, session, redirect, url_for
import pickle

app = Flask(__name__)
app.secret_key = "secret123"

# Load model & scaler
model = pickle.load(open("model/model.pkl", "rb"))
scaler = pickle.load(open("model/scaler.pkl", "rb"))

# 🔐 LOGIN PAGE
@app.route("/", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "123":
            session["user"] = username
            return redirect(url_for("home"))   # ✅ FIXED
        else:
            error = "❌ Invalid Username or Password"

    return render_template("login.html", error=error)

# 🏠 HOME PAGE
@app.route("/home")
def home():
    if "user" not in session:
        return redirect(url_for("login"))   # ✅ FIXED
    return render_template("index.html")

# 🔓 LOGOUT (NEW)
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# ✈️ PREDICTION (UNCHANGED LOGIC)
@app.route("/predict", methods=["POST"])
def predict():
    try:
        form_data = request.form.to_dict()

        visibility = float(form_data.get("Visibility_Km", 0) or 0)
        wind = float(form_data.get("Wind_Speed_Kmph", 0) or 0)
        turbulence = int(float(form_data.get("Turbulence", 0) or 0))
        weather = int(float(form_data.get("Weather_Condition", 0) or 0))
        pilot = float(form_data.get("Pilot_Experience_Hrs", 0) or 0)

        risk_score = 0
        reasons = []

        if visibility < 3:
            risk_score += 2
            reasons.append("Low Visibility")

        if wind > 50:
            risk_score += 2
            reasons.append("High Wind")

        if turbulence >= 2:
            risk_score += 2
            reasons.append("Turbulence")

        if weather >= 2:
            risk_score += 2
            reasons.append("Bad Weather")

        if pilot < 2000:
            risk_score += 1
            reasons.append("Low Pilot Experience")

        risk_percent = min(int((risk_score / 9) * 100), 100)

        if risk_score >= 5:
            result = f"⚠️ High Risk ({risk_percent}%)"
        else:
            result = f"✅ Low Risk ({risk_percent}%)"

        reason_text = ", ".join(reasons) if reasons else "All conditions normal"

        return render_template(
            "result.html",
            prediction_text=result,
            score=risk_score,
            percent=risk_percent,
            reason=reason_text
        )

    except Exception as e:
        return str(e)

if __name__ == "__main__":
    app.run(debug=True)