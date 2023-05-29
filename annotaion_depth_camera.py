import cv2
import pyrealsense2 as rs
import numpy as np
import cv2
import os
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

pipeline.start(config)

refPt = []
cropping = False
pause = False

def change_xy(x,z):
    X = np.max(np.array([(x-(15-((z/2500)*15)),0)]))
    return X

zoom_factor = 1.45

def click_and_crop(event, x, y, flags, param):

    global refPt, cropping

    if event == cv2.EVENT_LBUTTONDOWN:
        refPt = [(x, y)]
        cropping = True

    elif event == cv2.EVENT_LBUTTONUP:
        refPt.append((x, y))
        cropping = False

        cv2.rectangle(color_image, refPt[0], refPt[1], (0, 255, 0), 2)
        cv2.imshow("Video", color_image)

frame_counter = 0

while True:
    if not pause:

        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        if not depth_frame or not color_frame:
            continue

        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        height, width = depth_image.shape[:2]
        center_x = width // 2
        center_y = height // 2
        M = np.float32([[zoom_factor, 0, (1 - zoom_factor) * center_x],
                [0, zoom_factor, (1 - zoom_factor) * center_y]])
        zoomed_image = cv2.warpAffine(depth_image, M, (width, height))
        zoomed_image_colormap = cv2.warpAffine(depth_colormap, M, (width, height))

        cv2.imshow("Video", color_image)
        if len(refPt) == 2:
            (x_start, y_start) = refPt[0]
            (x_end, y_end) = refPt[1]
            if x_start > x_end:
                x_min_temp = x_start
                x_start = x_end
                x_end = x_min_temp
            if y_start > y_end:
                y_min_temp = y_start
                y_start = y_end
                y_end = y_min_temp
            cv2.rectangle(zoomed_image_colormap, (int(change_xy(x_start,zoomed_image[int((y_start+y_end)/2),int((x_start+x_end)/2)])),y_start), (int(change_xy(x_end,zoomed_image[int((y_start+y_end)/2),int((x_start+x_end)/2)])),y_end), (0, 255, 0), 2)
        cv2.imshow("Video Depth", zoomed_image_colormap)
    cv2.setMouseCallback("Video", click_and_crop)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break

    elif key == ord('p'):
        pause = not pause

    elif key == ord('s') and len(refPt) == 2 and pause:
        (x_start, y_start) = refPt[0]
        (x_end, y_end) = refPt[1]
        if x_start > x_end:
            x_min_temp = x_start
            x_start = x_end
            x_end = x_min_temp
        if y_start > y_end:
            y_min_temp = y_start
            y_start = y_end
            y_end = y_min_temp
        cv2.imshow("Crop", zoomed_image_colormap[int(y_start):int(y_end),int(change_xy(x_start,zoomed_image[int((y_start+y_end)/2),int((x_start+x_end)/2)])):int(change_xy(x_end,zoomed_image[int((y_start+y_end)/2),int((x_start+x_end)/2)]))])
        cv2.imwrite(os.path.join('depth_folder/', f"cropped_image_{frame_counter}.png"), zoomed_image[int(y_start):int(y_end),int(change_xy(x_start,zoomed_image[int((y_start+y_end)/2),int((x_start+x_end)/2)])):int(change_xy(x_end,zoomed_image[int((y_start+y_end)/2),int((x_start+x_end)/2)]))])

    frame_counter += 1

cv2.destroyAllWindows()
