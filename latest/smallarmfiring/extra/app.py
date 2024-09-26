from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
import cv2
import base64
import os
from ultralytics import YOLO
import mysql.connector

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'webm', 'avi', 'mov'}
DATABASE_CONFIG = {
    'host': 'localhost',    
    'user': 'root',    
    'password': 'Rupal@db123', 
    'database': 'sa_firing'
}

def get_db_connection():
    conn = mysql.connector.connect(**DATABASE_CONFIG)
    return conn

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

model = YOLO(r"D:\latest\smallarmfiring\extra\best.pt") # change path

@app.route('/')
def dashboard():
    return render_template("dashboard.html")

@app.route('/process-score', methods=['POST'])
def process_score():
    score = request.form.get('score')
    score2 = request.form.get('score2')
    score3 = request.form.get('score3')

    radius = 'less than 32'
    radius2 = 'between 32 and 48'
    radius3 = 'more than 48'

    conn = get_db_connection()
    cursor = conn.cursor()

    #cursor.executemany("""
    #    INSERT INTO settings (radius, score)
    #    VALUES (%s, %s)
    #""", [
    #    (radius, score),
    #    (radius2, score2),
    #    (radius3, score3)
    #])

    cursor.execute("""
        UPDATE settings
        SET radius = %s, score = %s
        WHERE id = %s
    """, (radius, score, 1))

    cursor.execute("""
        UPDATE settings
        SET radius = %s, score = %s
        WHERE id = %s
    """, (radius2, score2, 2))

    cursor.execute("""
        UPDATE settings
        SET radius = %s, score = %s
        WHERE id = %s
    """, (radius3, score3, 3))
    
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('dashboard'))

class GetImage:
    image_counter = 1

    def capture_photo(self, camera_url):
        cap = cv2.VideoCapture(camera_url)
        
        if not cap.isOpened():
            print(f"Failed to open camera URL: {camera_url}")
            return None, None
        
        ret, frame = cap.read()
        
        if not ret:
            print("Failed to capture a frame from the camera.")
            return None, None

        frame = cv2.resize(frame, (0, 0), fx=0.50, fy=0.50)
        ret, buffer = cv2.imencode('.jpg', frame)
        
        if not ret:
            print("Failed to encode frame to image.")
            return None, None
        
        # Convert the buffer to a base64 string
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        cap.release()

        filename = f"image_{GetImage.image_counter}.jpg"
        GetImage.image_counter += 1
        
        return image_base64, filename

@app.route('/capture-photo', methods=['POST'])
def capture_photo():
    cam = GetImage()
    image_base64, filename = cam.capture_photo("http://192.168.133.78:8080/video")
    
    if image_base64:
        return jsonify({'success': True, 'imageBase64': image_base64, 'filename': filename})
    else:
        return jsonify({'success': False, 'message': 'Failed to capture photo!'})

@app.route('/store-shooters', methods=['POST'])
def store_shooters():
    try:
        data = request.json
        num_shooters = data.get('numShooters')
        armid1 = data.get('armid1')
        armid2 = data.get('armid2')
        
        try:
            num_shooters = int(num_shooters)
        except ValueError:
            return jsonify({'error': 'numShooters must be a valid integer!'}), 400

        if num_shooters is None:
            return jsonify({'error': 'numShooters is required'}), 400

        # Allow armid2 to be None if numShooters is 1
        if num_shooters >= 1 and not armid1:
            return jsonify({'error': 'armid1 is required when numShooters is 1 or more'}), 400
        if num_shooters == 2 and not armid2:
            return jsonify({'error': 'armid2 is required when numShooters is 2'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO shooters (num_shooters, armid1, armid2)
            VALUES (%s, %s, %s)
        ''', (num_shooters, armid1 if armid1 else None, armid2 if armid2 else None))
        
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Data stored successfully!!'}), 200
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/new-settings', methods=['POST'])
def new_settings():
    butt_no = request.form.get('noOfBullet')
    army_id = request.form.get('sid_input')
    name = request.form.get('name')
    rank = request.form.get('range')

    # Save the data into the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO new_settings (butt_no, army_id, name, `rank`)
        VALUES (%s, %s, %s, %s)
    ''', (butt_no, army_id, name, rank))
    
    conn.commit()
    cursor.close()
    conn.close()

    return '', 200

@app.route('/save-round-distance', methods=['POST'])
def save_round_distance():
    rounds = request.form.get('rounds')
    distance = request.form.get('distance')

    # Save the data into the database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO rounds_distance (rounds, distance)
        VALUES (%s, %s)
    ''', (rounds, distance))
    
    conn.commit()
    cursor.close()
    conn.close()

    return '', 200

@app.route('/save-performance', methods=['POST'])
def save_performance():
    sid = request.form.get('sid_input')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO performance (sid, start_date, end_date)
        VALUES (%s, %s, %s)
    """, (sid, start_date, end_date))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('dashboard'))

@app.route('/save-photo', methods=['POST'])
def save_photo():
    if 'photo' in request.files:
        photo = request.files['photo']
        photo.save(os.path.join('photos', photo.filename))
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route("/upload-file", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files.get('file_input')
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            return redirect(url_for('display_image', filename=file.filename))
    return render_template("dashboard.html")

@app.route("/upload-video", methods=["GET", "POST"])
def upload_video():
    file = request.files.get('video_input')
    if file and allowed_file(file.filename):
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return redirect(url_for('display_video', filename=filename))
    return render_template('dashboard.html')

@app.route('/display-video/<filename>')
def display_video(filename):
    video_path = url_for('static', filename=f'uploads/{filename}')
    return render_template('display_video.html', video_path=video_path)

@app.route('/display/<filename>', methods=["GET"])
def display_image(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT army_id, name FROM new_settings
        ORDER BY id DESC LIMIT 1
    ''')
    result = cursor.fetchone()

    army_id = result[0] if result else 'Unknown'
    name = result[1] if result else 'Unknown'

    cursor.close()
    conn.close()
    
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
    m=0
    for i in t1:
        if i<r:
            score=3
            st="Inside 12 cm"
        elif i > c6:
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
            st="More than 48cm"
        m = m+1
        
        s += score        
        scores.append(score)
        distances.append(st)
    score_distance_pairs = list(zip(scores, distances))  
    
      
         

    # Calculate average score
    average_score = round(s / len(t1), 2) if t1 else 0
    
    #total_no_of_bullets_detected = c
    z=3*m
    
    acc=(s/z)*100
    gr=""
    if acc>=86:
      gr="HPS"
    elif acc>=66 and acc<86:  
      gr="MM"
    elif acc>=60 and acc<66:  
      gr="FC" 
    elif acc>=50 and acc<=60:
      gr="SS"  
    else:
      gr="FAIL"    
      
      
    return render_template("display.html", file_path=url_for('static', filename=f'uploads/{filename}'), scores=scores, average_score=average_score, score_distance_pairs=score_distance_pairs,
                           total_score=s,tot_sco=z,accuracy=round((s/z*100),2),grade=gr, army_id=army_id, name=name)
                           

if __name__ == '__main__':
    app.run(debug=True)
