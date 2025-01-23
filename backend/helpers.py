import piexif
import fractions
import requests
import math

def get_sensor_size(camera_name):
    """
    Get the physical dimensions of a camera sensor in meters.

    Parameters:
    camera_name (str): The name of the camera.

    Returns:
    tuple: A tuple (sensor_width, sensor_height) in meters if the camera is found.
    str: An error message if the camera is not found.
    """
    camera_data = {
        "Sony Alpha 7 IV": (36, 24),
        "Canon EOS R5": (36, 24),
        "Nikon Z9": (36, 24),
        "Panasonic Lumix S5 II": (36, 24),
        "Fujifilm X-T5": (23.5, 15.6),
        "Sony Alpha 6400": (23.5, 15.6),
        "Canon EOS R10": (22.3, 14.9),
        "Canon EOS M100": (22.3, 14.9),
        "Olympus OM-D E-M1 Mark III": (17.3, 13),
        "Panasonic Lumix GH6": (17.3, 13),
        "Hasselblad X2D 100C": (44, 33),
        "Fujifilm GFX 100S": (43.8, 32.9),
        "Sony Xperia Pro-I": (12.8, 9.6),  # Approximate 1-inch dimensions
        "Xiaomi 13 Ultra": (12.8, 9.6),  # Approximate 1-inch dimensions
        "Xiaomi 11 Pro": (16, 12),
        "Apple iPhone 15 Pro Max": (9.6, 7.2),  # 1/1.28-inch
        "Google Pixel 8 Pro": (9.2, 7),  # 1/1.31-inch
        "Samsung Galaxy S23 Ultra": (9.6, 7.2),  # 1/1.3-inch
        "Huawei P60 Pro": (8.8, 6.6),  # 1/1.4-inch
        "iPhone SE (2022)": (4, 3),  # 1/3.6-inch
        "Samsung Galaxy A54": (8.9, 6.6),  # 1/1.56-inch
        "Apple iPhone 15 Pro Max": (9.6, 7.2),  # 1/1.28-inch
        "Apple iPhone 15 Pro": (9.6, 7.2),  # 1/1.28-inch
        "Apple iPhone 15": (7.6, 5.7),  # 1/1.65-inch
        "Apple iPhone 14 Pro Max": (9.6, 7.2),  # 1/1.28-inch
        "Apple iPhone 14 Pro": (9.6, 7.2),  # 1/1.28-inch
        "Apple iPhone 14": (7.6, 5.7),  # 1/1.65-inch
        "Apple iPhone 13 Pro Max": (7.6, 5.7),  # 1/1.65-inch
        "Apple iPhone 13 Pro": (7.6, 5.7),  # 1/1.65-inch
        "Apple iPhone 13": (7.6, 5.7),  # 1/1.65-inch
        "Apple iPhone 12 Pro Max": (8.4, 6.3),  # 1/1.7-inch
        "Apple iPhone 12 Pro": (8.4, 6.3),  # 1/1.7-inch
        "Apple iPhone 12": (7.6, 5.7),  # 1/1.65-inch
        "Apple iPhone 11 Pro Max": (7.6, 5.7),  # 1/2.55-inch
        "Apple iPhone 11 Pro": (7.6, 5.7),  # 1/2.55-inch
        "Apple iPhone 11": (6.4, 4.8),  # 1/3-inch
        "Apple iPhone XS Max": (7.6, 5.7),  # 1/2.55-inch
        "Apple iPhone XS": (7.6, 5.7),  # 1/2.55-inch
        "Apple iPhone XR": (6.4, 4.8),  # 1/3-inch
        "Apple iPhone X": (6.4, 4.8),  # 1/3-inch
        "Apple iPhone 8 Plus": (6.4, 4.8),  # 1/3-inch
        "Apple iPhone 8": (6.4, 4.8),  # 1/3-inch
        "Apple iPhone 7 Plus": (6.4, 4.8),  # 1/3-inch
        "Apple iPhone 7": (6.4, 4.8),  # 1/3-inch
        "Apple iPhone 6s Plus": (6.4, 4.8),  # 1/3-inch
        "Apple iPhone 6s": (6.4, 4.8),  # 1/3-inch
        "Apple iPhone 6 Plus": (6.4, 4.8),  # 1/3-inch
        "Apple iPhone 6": (6.4, 4.8),  # 1/3-inch
        "Apple iPhone SE (2022)": (4, 3),  # 1/3.6-inch
        "DJI Mini 3 Pro (Drone)": (9.6, 7.2),  # 1/1.3-inch
        "GoPro Hero 12 Black": (6.9, 5.2)  # 1/1.9-inch
    }

    if camera_name in camera_data:
        sensor_width, sensor_height = camera_data[camera_name]
        # Convert from mm to meters
        return (sensor_width / 1000, sensor_height / 1000)
    else:
        return "Camera not found."
    
def convert_to_degrees(value, ref):
    """Convert GPS coordinates to degrees."""
    d = float(value[0][0]) / float(value[0][1])
    m = float(value[1][0]) / float(value[1][1])
    s = float(value[2][0]) / float(value[2][1])

    if ref in ['S', 'W']:
        d = -d
        m = -m
        s = -s

    return d + (m / 60.0) + (s / 3600.0)

def get_exif_data(image_path):
    """Extract latitude, longitude, and focal length from a JPEG image."""
    exif_data = piexif.load(image_path)
    gps_info = exif_data.get("GPS", {})
    exif_info = exif_data.get("Exif", {})

    # Extract GPS Data
    latitude = None
    longitude = None
    if piexif.GPSIFD.GPSLatitude in gps_info and piexif.GPSIFD.GPSLatitudeRef in gps_info:
        print('Ciao')
        latitude = convert_to_degrees(
            gps_info[piexif.GPSIFD.GPSLatitude],
            gps_info[piexif.GPSIFD.GPSLatitudeRef].decode()
        )
    if piexif.GPSIFD.GPSLongitude in gps_info and piexif.GPSIFD.GPSLongitudeRef in gps_info:
        longitude = convert_to_degrees(
            gps_info[piexif.GPSIFD.GPSLongitude],
            gps_info[piexif.GPSIFD.GPSLongitudeRef].decode()
        )

    # Extract Focal Length
    focal_length = None
    if piexif.ExifIFD.FocalLength in exif_info:
        focal_length = exif_info[piexif.ExifIFD.FocalLength]
        focal_length = float(focal_length[0]) / float(focal_length[1])

    return latitude, longitude, focal_length/1000
def get_elevation(easting, northing, sr=None):
    """
    Retrieve the elevation of a point using the Swiss geo.admin.ch height service.

    Args:
        easting (float): The easting coordinate in LV03 (EPSG:21781) or LV95 (EPSG:2056).
        northing (float): The northing coordinate in LV03 (EPSG:21781) or LV95 (EPSG:2056).
        sr (int, optional): The spatial reference system (EPSG code). Defaults to None.

    Returns:
        float: Elevation in meters.
        str: Error message if the request fails.
    """
    url = "https://api3.geo.admin.ch/rest/services/height"
    params = {
        "easting": easting,
        "northing": northing
    }
    if sr:
        params["sr"] = sr

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        if "height" in data:
            return float(data["height"])
        else:
            return "Elevation data not found in the response."
    except requests.RequestException as e:
        return f"An error occurred while making the request: {e}"
    except ValueError:
        return "Invalid response format received from the API."
    
def compute_steepness_angles(easting, northing, delta=1, sr=None):
    """
    Compute the steepness angles in the east and north directions.

    Args:
        easting (float): The easting coordinate of the position.
        northing (float): The northing coordinate of the position.
        delta (float): The small offset for gradient approximation.
        sr (int, optional): The spatial reference system (EPSG code). Defaults to None.

    Returns:
        tuple: Steepness angles (in degrees) in the easting and northing directions.
        str: Error message if the calculation fails.
    """
    # Elevations at the central point and offsets
    z_center = get_elevation(easting, northing, sr)
    if z_center is None:
        return None, "Elevation data unavailable for the central point."

    z_east = get_elevation(easting + delta, northing, sr)
    if z_east is None:
        return None, "Elevation data unavailable for the east-offset point."

    z_north = get_elevation(easting, northing + delta, sr)
    if z_north is None:
        return None, "Elevation data unavailable for the north-offset point."

    # Compute the change in elevation (dZ) and change in position (dE and dN)
    delta_z_east = z_east - z_center
    delta_z_north = z_north - z_center

    # Compute the steepness angles in radians
    angle_east_rad = math.atan(delta_z_east / delta)
    angle_north_rad = math.atan(delta_z_north / delta)

    # Convert radians to degrees
    angle_east_deg = math.degrees(angle_east_rad)
    angle_north_deg = math.degrees(angle_north_rad)

    return angle_east_deg, angle_north_deg

def computeParallelSize(focal_length, sensor_size, distance):
    """
    Compute the physical size of the image on an avalanche parallel to the sensor at a distance.
    
    Parameters:
    focal_length (float): The focal length of the camera in mm.
    sensor_size (tuple): A tuple (sensor_width, sensor_height) in mm.
    distance (float): The distance from the camera to the wall in mm.
    
    Returns:
    tuple: (width, height) of the image captured on the wall in mm.
    """
    sensor_width, sensor_height = sensor_size
    
    # Compute the width and height of the wall captured by the camera
    wall_width = sensor_width * (distance / focal_length)
    wall_height = sensor_height * (distance / focal_length)
    
    return wall_width, wall_height

def computeTiltedRetroProjection(focal_length, sensor_size, distance, tilt_angles):
    """
    Compute the retro-projected size of a tilted avalanche on the parallel plane to the sensor.
    
    Parameters:
    focal_length (float): The focal length of the camera in mm.
    sensor_size (tuple): A tuple (sensor_width, sensor_height) in mm.
    distance (float): The distance from the camera to the wall in mm.
    tilt_angles (tuple): A tuple (theta, phi) representing the tilt angles in degrees.
    
    Returns:
    tuple: (projected_width, projected_height) of the image captured on the parallel wall in mm.
    """
    # Unpack tilt angles and convert to radians
    theta, phi = math.radians(tilt_angles[0]), math.radians(tilt_angles[1])
    
    # Use the existing computeParallelSize function to get the un-tilted dimensions
    wall_width, wall_height = computeParallelSize(focal_length, sensor_size, distance)
    
    # Compute the projected width and height considering tilts
    retro_projected_width = wall_width / math.cos(theta)
    retro_projected_height = wall_height / math.cos(phi)
    
    return retro_projected_width, retro_projected_height

def computeAvalancheSize(mask, distance, focal_length, sensor_size, tilt_angles):
    """
    Compute the physical size of the avalanche based on the segmentation mask.
    
    The function calculates the relative size of the avalanche from the segmentation mask
    and then computes the actual physical size of the avalanche on the ground, taking into
    account the camera's focal length, sensor size, the distance from the object, and any tilt
    in the image.

    Parameters:
    mask (Tensor): A binary segmentation mask (tensor) of the avalanche, where non-zero values
                   represent the avalanche pixels, and zero values represent the background.
                   The shape of the mask is typically a 2D or 3D tensor.
    distance (float): The distance from the camera to the avalanche (in mm).
    focal_length (float): The focal length of the camera (in mm).
    sensor_size (tuple): A tuple (sensor_width, sensor_height) representing the dimensions of
                          the camera's sensor in mm.
    tilt_angles (tuple): A tuple (theta, phi) representing the tilt angles of the camera in degrees
                          around the horizontal (theta) and vertical (phi) axes.

    Returns:
    tuple: The physical size of the avalanche on the ground (width, height) in mm, considering
           the tilt angles of the camera.
    """
    # Compute the relative avalanche size in the mask
    relativeAvalancheSize = mask #sum(mask) / mask.numel()

    # Compute the projected size of the tilted wall (or ground) based on camera properties
    projected_width, projected_height = computeTiltedRetroProjection(focal_length, sensor_size, distance, tilt_angles)
    
    # The physical size of the avalanche is proportional to the relative size in the mask
    absoluteAvalancheSize = relativeAvalancheSize * projected_width * projected_height
    
    return absoluteAvalancheSize

# Function to compute 3D Euclidean distance (including elevation)
def compute_3d_distance(easting1, northing1, elevation1, easting2, northing2, elevation2):
    """
    Compute the 3D Euclidean distance between two points in the easting/northing/elevation space.
    """
    return math.sqrt((easting2 - easting1) ** 2 + (northing2 - northing1) ** 2 + (elevation2 - elevation1) ** 2)