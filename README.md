<p align="center">
  <img width="600" alt="UI" src="https://github.com/KnOX-07/SmallArmsFiring/blob/4ae0306ef210ab2e204f7b065b297c5167731192/latest/output/UI.png">
</p>

# Padinale Small Arms Firing Score Evaluator

This is an AI-based application designed for shooting analysis using object detection. The application captures images from a camera feed, processes them using the YOLO (You Only Look Once) model, and evaluates shooting performance based on various metrics.

## Features

- Upload and process images and videos.
- Capture photos from a live camera feed.
- Store and manage shooting data in a MySQL database.
- Calculate and display scores based on distances to targets.
- Grading system to evaluate shooting performance.
- User-friendly dashboard for data input and results display.

## Technologies Used

- **Flask**: For web framework and routing.
- **OpenCV**: For video capture and image processing.
- **YOLO**: For object detection and recognition.
- **MySQL**: For database management.
- **HTML/CSS**: For frontend rendering.

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/KnOX-07/SmallArmsFiring.git
   cd SmallArmsFiring
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
3. **Set up the MySQL database**:
   - Create a database named sa_firing.
   - Update the DATABASE_CONFIG in the app.py file with your MySQL credentials.
4. **Run the application**:
   - Navigate to the directory `extra`
   - Open terminal and type:


      ```bash
      python app.py
      ```
      By default, the application will run on `http://127.0.0.1:5000/`.

## Usage

- Open your web browser and go to `http://127.0.0.1:5000/` to access the dashboard.
- Use the dashboard to upload images/videos, capture photos, and manage shooting data.
- Results and performance metrics will be displayed after processing the uploaded media.

## Configuration

- The path to the YOLO model is set in the `app.py` file. Make sure to update it to point to your model file:
  
  ```bash
  model = YOLO(r"D:\latest\smallarmfiring\extra\best.pt")  # Change this path
  ```
- The allowed file extensions for uploads are defined in the configuration. You can modify these as needed.
