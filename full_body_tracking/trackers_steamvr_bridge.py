import asyncio
import json
import openvr
import websockets
import math

# Server. Run alongside SteamVR.

def matrix_to_pose(m):
    x, y, z = m[0][3], m[1][3], m[2][3]
    tr = m[0][0] + m[1][1] + m[2][2]
    if tr > 0:
        s = math.sqrt(tr + 1.0) * 2
        w = 0.25 * s
        x_q = (m[2][1] - m[1][2]) / s
        y_q = (m[0][2] - m[2][0]) / s
        z_q = (m[1][0] - m[0][1]) / s
    elif (m[0][0] > m[1][1]) and (m[0][0] > m[2][2]):
        s = math.sqrt(1.0 + m[0][0] - m[1][1] - m[2][2]) * 2
        w = (m[2][1] - m[1][2]) / s
        x_q = 0.25 * s
        y_q = (m[0][1] + m[1][0]) / s
        z_q = (m[0][2] + m[2][0]) / s
    elif m[1][1] > m[2][2]:
        s = math.sqrt(1.0 + m[1][1] - m[0][0] - m[2][2]) * 2
        w = (m[0][2] - m[2][0]) / s
        x_q = (m[0][1] + m[1][0]) / s
        y_q = 0.25 * s
        z_q = (m[1][2] + m[2][1]) / s
    else:
        s = math.sqrt(1.0 + m[2][2] - m[0][0] - m[1][1]) * 2
        w = (m[1][0] - m[0][1]) / s
        x_q = (m[0][2] + m[2][0]) / s
        y_q = (m[1][2] + m[2][1]) / s
        z_q = 0.25 * s
    return {"pos": {"x": x, "y": y, "z": z}, "rot": {"x": x_q, "y": y_q, "z": z_q, "w": w}}

async def tracker_server(websocket):
    print("Quest 3 Connected to Bridge.")
    try:
        while True:
            poses = openvr.VRSystem().getDeviceToAbsoluteTrackingPose(
                openvr.TrackingUniverseStanding, 0, openvr.k_unMaxTrackedDeviceCount
            )
            
            trackers_data = {}
            for i in range(openvr.k_unMaxTrackedDeviceCount):
                pose = poses[i]
                if pose.bPoseIsValid:
                    device_class = openvr.VRSystem().getTrackedDeviceClass(i)
                    if device_class == openvr.TrackedDeviceClass_GenericTracker:
                        serial = openvr.VRSystem().getStringTrackedDeviceProperty(i, openvr.Prop_SerialNumber_String)
                        trackers_data[serial] = matrix_to_pose(pose.mDeviceToAbsoluteTracking)

            if trackers_data:
                await websocket.send(json.dumps(trackers_data))
            
            await asyncio.sleep(0.016) # 60 fps
    except websockets.exceptions.ConnectionClosed:
        print("Quest 3 disconnected.")

async def main():
    print("Initializing OpenVR...")
    while True:
        try:
            openvr.init(openvr.VRApplication_Background)
            break
        except Exception:
            await asyncio.sleep(2.0)
            
    print("Bridge ready on ws://0.0.0.0:8089")
    try:
        async with websockets.serve(tracker_server, "0.0.0.0", 8089):
            await asyncio.Future()
    finally:
        openvr.shutdown()

if __name__ == "__main__":
    asyncio.run(main())