from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from ultralytics import YOLO
import cv2

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

model = YOLO(r"/home/akash/Downloads/smallarmfiring/best.pt")

@app.route('/')
def dashboard():
    return render_template("dashboard.html")

@app.route('/process-score', methods=['POST'])
def process_score():
    # Retrieve the score from the form data
    scored = request.form.get('score')    
    sco1 = request.form.get('score2')
    sco2 = request.form.get('score3')

@app.route('/save-photo', methods=['POST'])
def save_photo():
    if 'photo' in request.files:
        photo = request.files['photo']
        # Save the file in the "photos" directory with a unique name
        photo.save(os.path.join('photos', photo.filename))
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        sid = request.form.get('sid_input')
        file = request.files.get('file_input')
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            return redirect(url_for('display_image', filename=file.filename, sid=sid))
    return render_template("dashboard.html")

@app.route('/display/<filename>', methods=["GET"])
def display_image(filename):
    sid = request.args.get('sid')
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # Process the image through the model
    results = model(file_path)

    # Initialize list to store the center coordinates
    l = []

    # Extract bounding box predictions and additional calculations
    c = 0
    for det in results[0].boxes:
        x1, y1, x2, y2 = det.xyxy[0].int().tolist()  # Bounding box coordinates
        
        n1 = int(f"{x1}")
        n2 = int(f"{y1}")
        n3 = int(f"{x2}")
        n4 = int(f"{y2}")
        
        m1 = (n1 + n3) / 2
        m2 = (n2 + n4) / 2
        
        l.append((m1, m2))
        
        cls = det.cls[0].int().tolist()  # Class of the detected object
        conf = det.conf[0].float().tolist()  # Confidence score of the detection
        
        if cls == 1:
            z = ((n1 - n3) ** 2 + (n2 - n4) ** 2) ** 0.5
            r = z / 2
        elif cls == 0:
            c = c + 1
        else:
            continue

    # Calculate the radius
    c2 = 1.33 * r
    c3 = (9 / 8) * c2
    c4 = (4 / 3) * c3
    c5 = (4 / 3) * c4
    c6 = (3 / 2) * c5

    # Calculate scores based on distances
    t = l[0]
    t1 = []
    scores = []
    distances=[]
    snum=[]
    for i in l[1:]:
        k = ((t[0] - i[0]) ** 2 + (t[1] - i[1]) ** 2) ** 0.5
        t1.append(k)
        
    invalid = 0
    s = 0
    st=""
    for i in t1:
        if i > c6:
            invalid += 1
            continue
        elif i>c4 and i < c5:
            score = 3
            st="24cm-32cm"
        elif i>c3 and i < c4:
            score = 3
            st="18cm-24cm"    
        elif i>c2 and i < c3:
            score = 3
            st="16cm-18cm"  
        elif i>r and i < c2:
            score = 3
            st="12cm-16cm"          
        elif i >= c5 and i <= c6:
            score = 2
            st="32cm-48cm"
        else:
            score = 1 
            st="more than 48cm"
        
        s += score
        scores.append(score)
        distances.append(st)
    score_distance_pairs = list(zip(scores, distances))  
    m=1  
    for i in scores:
     snum.append(m)
     m=m+1
      
         

    # Calculate average score
    average_score = round(s / len(t1), 2) if t1 else 0
    
    total_no_of_bullets_detected = c
    Number_of_valid_bullet_hits = total_no_of_bullets_detected - invalid
    
    percentage_of_valid_target_hits = (Number_of_valid_bullet_hits / total_no_of_bullets_detected) * 100
    return render_template("display.html", file_path=url_for('static', filename=f'uploads/{filename}'), sid=sid, scores=scores, average_score=average_score, score_distance_pairs=score_distance_pairs,
                           total_no_of_bullets_detected=total_no_of_bullets_detected, Number_of_valid_bullet_hits=Number_of_valid_bullet_hits,snum=snum,
                           percentage_of_valid_target_hits=percentage_of_valid_target_hits)

if __name__ == '__main__':
    app.run(debug=True)
