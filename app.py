from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Predefined symptoms for each disease
DISEASE_SYMPTOMS = {
    "heart": ["Chest Pain", "Shortness of Breath", "Fatigue", "Dizziness", "Swelling in Legs"],
    "diabetes": ["Frequent Urination", "Excessive Thirst", "Unexplained Weight Loss", "Blurred Vision", "Fatigue"],
    "thyroid": ["Weight Changes", "Hair Loss", "Mood Swings", "Fatigue", "Irregular Heartbeat"]
}

# Health Advice for conditions
HEALTH_ADVICE = {
    "Hypothyroidism": "Eat iodine-rich foods like fish, dairy, and eggs. Exercise regularly and take thyroid medication as prescribed.",
    "Hyperthyroidism": "Limit iodine intake, manage stress, and avoid excessive caffeine. Follow doctor's medication plan.",
    "Hypertension (High BP)": "Reduce salt intake, exercise regularly, and manage stress. Avoid smoking and alcohol.",
    "Hypotension (Low BP)": "Increase salt intake slightly, stay hydrated, and avoid standing up too quickly.",
    "Hyperglycemia (High Blood Sugar)": "Limit sugar intake, exercise daily, and monitor blood sugar levels. Follow diabetes medication if prescribed.",
    "Hypoglycemia (Low Blood Sugar)": "Eat small frequent meals, carry a glucose source, and monitor sugar levels regularly.",
    "Normal": "Your levels are in a healthy range! Maintain a balanced diet and stay active."
}

# Dummy user storage
users = {}

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users:
            return "User already exists!"
        users[username] = password
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users and users[username] == password:
            session["user"] = username
            return redirect(url_for("select_disease"))
        return "Invalid credentials!"
    return render_template("login.html")

@app.route("/select_disease", methods=["GET", "POST"])
def select_disease():
    if "user" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        disease = request.form["disease"]
        return redirect(url_for("symptoms", disease=disease))
    return render_template("select_disease.html")

@app.route("/symptoms", methods=["GET", "POST"])
def symptoms():
    if "user" not in session:
        return redirect(url_for("login"))
    
    disease = request.args.get("disease")
    if disease not in DISEASE_SYMPTOMS:
        return "Invalid disease selected!"
    
    symptoms_list = DISEASE_SYMPTOMS[disease]

    if request.method == "POST":
        selected_symptoms = request.form.getlist("symptoms")
        return redirect(url_for("additional_input", disease=disease, symptoms=",".join(selected_symptoms)))

    return render_template("symptoms.html", disease=disease, symptoms_list=symptoms_list)

@app.route("/additional_input", methods=["GET", "POST"])
def additional_input():
    if "user" not in session:
        return redirect(url_for("login"))

    disease = request.args.get("disease")
    symptoms = request.args.get("symptoms", "").split(",")

    if request.method == "POST":
        if disease == "thyroid":
            tsh = float(request.form["tsh"])
            thyroid_type = "Hypothyroidism" if tsh > 4.0 else "Hyperthyroidism" if tsh < 0.4 else "Normal"
            return redirect(url_for("result", disease=disease, symptoms=",".join(symptoms), condition=thyroid_type, advice=HEALTH_ADVICE[thyroid_type]))

        elif disease == "heart":
            systolic = int(request.form["systolic"])
            diastolic = int(request.form["diastolic"])
            if systolic >= 130 or diastolic >= 80:
                heart_condition = "Hypertension (High BP)"
            elif systolic <= 90 or diastolic <= 60:
                heart_condition = "Hypotension (Low BP)"
            else:
                heart_condition = "Normal"
            return redirect(url_for("result", disease=disease, symptoms=",".join(symptoms), condition=heart_condition, advice=HEALTH_ADVICE[heart_condition]))

        elif disease == "diabetes":
            sugar = int(request.form["sugar"])
            if sugar > 180:
                diabetes_type = "Hyperglycemia (High Blood Sugar)"
            elif sugar < 70:
                diabetes_type = "Hypoglycemia (Low Blood Sugar)"
            else:
                diabetes_type = "Normal"
            return redirect(url_for("result", disease=disease, symptoms=",".join(symptoms), condition=diabetes_type, advice=HEALTH_ADVICE[diabetes_type]))

    return render_template("additional_input.html", disease=disease)

@app.route("/result")
def result():
    if "user" not in session:
        return redirect(url_for("login"))
    
    disease = request.args.get("disease")
    symptoms = request.args.get("symptoms", "").split(",")
    condition = request.args.get("condition")
    advice = request.args.get("advice", "No advice available")

    return render_template("result.html", disease=disease, symptoms=symptoms, condition=condition, advice=advice)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
