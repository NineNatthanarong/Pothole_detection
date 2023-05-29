import cv2
import pyrealsense2 as rs
import numpy as np

# Initialize the RealSense pipeline
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
pipeline.start(config)

# Create a VideoWriter object to save the color video
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('color_video.avi', fourcc, 30.0, (640, 480))

# Initialize the frame counter
frame_counter = 0

# Main loop
paused = False
while True:
    if not paused:
        # Wait for the next set of frames from the RealSense camera
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()

        # Convert the color frame to a numpy array
        color_image = np.asanyarray(color_frame.get_data())

        # Write the color frame to the video
        out.write(color_image)

        # Show the color frame
        cv2.imshow('Color', color_image)
        
        frame_counter += 1

    # Wait for key press
    key = cv2.waitKey(1)
    if key == ord('p'):
        # Toggle pause/unpause
        paused = not paused
    elif key == ord('s'):
        # Save the depth frame as a PNG image with the frame counter in the filename
        depth_image = np.asanyarray(depth_frame.get_data())
        filename = f'image/depth_image_{frame_counter}.png'
        cv2.imwrite(filename, depth_image)

    # Break the loop if 'q' is pressed
    if key == ord('q'):
        break

# Release resources
pipeline.stop()
out.release()
cv2.destroyAllWindows()
