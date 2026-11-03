Step 1: Start the Local Web Server

Save your HTML file as index.html in a folder, open a terminal there, and run:

Bash
python -m http.server 3009

Step 2: Establish ADB Port Forwarding

Connect your Quest 3 via USB, ensure USB Debugging is allowed, and forward both ports in your PC terminal:

Bash
adb reverse tcp:8089 tcp:8089
adb reverse tcp:3009 tcp:3009

Step 3: Run SteamVR & The Python Bridge

Turn on SteamVR and your Vive trackers.

Run your tracker bridge script:

Bash
python trackers_steamvr_bridge.py

Step 4: Play in Quest 3 AR

Open the Meta Quest Browser in your headset.

Go to: http://localhost:3009

Click "Enter AR", stand in a T-Pose, and press 'C' (or click the UI button) to calibrate.