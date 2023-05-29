import cv2
import numpy as np
import cv2
import os
import re

refPt = []
cropping = False

def change_x(x, z):
    X = np.max(np.array([(x - (15 - ((z / 2500) * 15)), 0)]))
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

        cv2.rectangle(frame, refPt[0], refPt[1], (0, 255, 0), 2)
        cv2.rectangle(zoomed_image_colormap, refPt[0], refPt[1], (0, 255, 0), 2)
        cv2.imshow("Video", frame)
        cv2.imshow("Video Depth", zoomed_image_colormap)

folder_path = 'image/'
png_files = []

for file_name in os.listdir(folder_path):
    if file_name.endswith('.png'):
        png_files.append(file_name)

video_path = 'color_video.avi'
depth_image_path = 'image/'
video = cv2.VideoCapture(video_path)

frame_counter = 0
current_png_index = 0

depth_image = cv2.imread(depth_image_path + png_files[current_png_index], cv2.IMREAD_ANYDEPTH)
frame_num = re.search(r'\d+', png_files[current_png_index])
video.set(cv2.CAP_PROP_POS_FRAMES, int(frame_num.group()))

while True:
    ret, frame = video.read()

    if not ret:
        break

    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

    height, width = depth_image.shape[:2]
    center_x = width // 2
    center_y = height // 2
    M = np.float32([[zoom_factor, 0, (1 - zoom_factor) * center_x],
                    [0, zoom_factor, (1 - zoom_factor) * center_y]])
    zoomed_image = cv2.warpAffine(depth_image, M, (width, height))
    zoomed_image_colormap = cv2.warpAffine(depth_colormap, M, (width, height))

    cv2.imshow("Video", frame)
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
        
    cv2.imshow("Video Depth", zoomed_image_colormap)
    cv2.setMouseCallback("Video", click_and_crop)
    key = cv2.waitKey(0) & 0xFF

    if key == ord('q'):
        break

    elif key == ord('s') and len(refPt) == 2:
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

        cv2.imwrite(
            os.path.join('crop_image/', f"cropped_image_{frame_counter}.png"),
            zoomed_image[int(y_start):int(y_end),
            int(change_x(x_start, zoomed_image[int((y_start + y_end) / 2), int((x_start + x_end) / 2)])):
            int(change_x(x_end, zoomed_image[int((y_start + y_end) / 2), int((x_start + x_end) / 2)]))]
        )

        current_png_index += 1
        if current_png_index >= len(png_files):
            break 
        depth_image = cv2.imread(depth_image_path + png_files[current_png_index], cv2.IMREAD_ANYDEPTH)
        frame_num = re.search(r'\d+', png_files[current_png_index])
        video.set(cv2.CAP_PROP_POS_FRAMES, int(frame_num.group()))
    elif key == ord('c'):
        refPt = []
    frame_counter += 1

video.release()
cv2.destroyAllWindows()
