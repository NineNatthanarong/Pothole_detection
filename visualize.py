import open3d as o3d
import numpy as np

# Load the depth image
depth_image = o3d.io.read_image("image\depth_image_476.png")
# Convert depth image to a numpy array
depth_array = np.array(depth_image)

# Rescale the depth values to the desired range
depth_scale = (1.0/255.0)*1000
depth_array = depth_array

# Get the dimensions of the depth array
height, width = depth_array.shape[:2]

# Create the intrinsic matrix for the depth image
intrinsic = o3d.camera.PinholeCameraIntrinsic(width, height, fx=1.0, fy=1.0, cx=width // 2, cy=height // 2)

# Create the point cloud by converting the depth array to 3D coordinates
y, x = np.mgrid[0:height, 0:width]
x = x.reshape(-1)
y = y.reshape(-1)
depth = depth_array[:,:].reshape(-1)  # take the first channel and reshape

# Create the PointCloud
points = np.column_stack((x, y, depth))
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)

# Visualize the PointCloud
o3d.visualization.draw_geometries([pcd])
