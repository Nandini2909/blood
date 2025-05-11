from flask import Flask, render_template, request
from blood_utils import save_entry, find_match, is_valid_blood_group

app = Flask(__name__)

# Blood group compatibility map for recipients
BLOOD_COMPATIBILITY = {
    "O-": ["O-"],
    "O+": ["O-", "O+"],
    "A-": ["O-", "A-"],
    "A+": ["O-", "O+", "A-", "A+"],
    "B-": ["O-", "B-"],
    "B+": ["O-", "O+", "B-", "B+"],
    "AB-": ["O-", "A-", "B-", "AB-"],
    "AB+": ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"],
}

def get_compatible_donors(recipient_group):
    return BLOOD_COMPATIBILITY.get(recipient_group, [recipient_group])

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/donor", methods=["GET", "POST"])
def donor():
    if request.method == "POST":
        data = {
            "type": "offer",
            "name": request.form["name"],
            "contact": request.form["contact"],
            "blood_group": request.form["blood_group"].upper(),
            "location": request.form["location"]
        }
        if not is_valid_blood_group(data["blood_group"]):
            return render_template("result.html", message="Invalid blood group.", matches=[])

        if save_entry(data):
            matches = find_match(data)
            return render_template("result.html", message="Your entry has been saved!", matches=matches)
        else:
            return render_template("result.html", message="Failed to get location coordinates.", matches=[])
    return render_template("donor.html")

@app.route("/requester", methods=["GET", "POST"])
def requester():
    if request.method == "POST":
        data = {
            "type": "request",
            "name": request.form["name"],
            "contact": request.form["contact"],
            "blood_group": request.form["blood_group"].upper(),
            "location": request.form["location"]
        }
        if not is_valid_blood_group(data["blood_group"]):
            return render_template("result.html", message="Invalid blood group.", matches=[])

        compatible_groups = get_compatible_donors(data["blood_group"])
        if save_entry(data):
            matches = find_match(data, compatible_groups)
            return render_template("result.html", message="Your request has been saved!", matches=matches)
        else:
            return render_template("result.html", message="Failed to get location coordinates.", matches=[])
    return render_template("requester.html")

if __name__ == "__main__":
    app.run(debug=True)