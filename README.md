# Autonomous Computer Vision Navigation AI for diep.io

## Description

This project is an autonomous computer vision navigation AI designed for the game [diep.io](https://diep.io). The AI has several functionalities that enhance gameplay by automating various tasks:

- **Target Detection**: The AI searches for targets within the game environment using computer vision techniques.
- **Charging and Fleeing**: It intelligently charges at targets to engage in combat and flees when necessary to avoid damage.
- **Collision Avoidance**: The AI navigates the game environment while avoiding obstacles and targets to prevent crashes.
- **Shooting**: When a target is detected within a certain range, the AI automatically shoots at them.

### AI Vision

The AI's vision includes two concentric radii around it, which assist with movement and decision-making:
- **Outer Radius**: Helps the AI determine when to charge.
- **Inner Radius**: Aids in avoiding obstacles and fleeing from targets.

### User Interface

- **Basic Properties Menu**: Located on the left side of the screen, this menu displays:
  - Current framerate
  - Active buttons pressed by the AI
  - Current AI state (searching, charging, fleeing)
  - Status of the aimbot and movement toggles

## Demo

Check out the AI in action in the demo video below:

[![Autonomous Computer Vision Navigation AI Demo](http://img.youtube.com/vi/b5HUMx49OpQ/0.jpg)](https://www.youtube.com/watch?v=b5HUMx49OpQ)


## How to Run

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/doquendo0/Autonomous-Navigation-AI.git
2. **Download YOLOv5**:
   Go to the [YOLOv5 GitHub Repository](https://github.com/ultralytics/yolov5)
   Download the ZIP file of the repository.
   Extract the folder and move it to the same directory as your cloned repository files.
   Modify the variable `folder_path` in `main.py` to the name of the extracted folder.
3. **Set the Chrome Window Name**:
   Modify the variable `window_name` in `main.py` to the name of the window when running the game in Chrome.
4. **Install the Required Dependencies**:
   pip install -r requirements.txt
5. **Run the Program**:
   python main.py
6. **Activate the Program Features**:
   Press `p` to turn on the aimbot.
   Press `m` to turn on the movement.
