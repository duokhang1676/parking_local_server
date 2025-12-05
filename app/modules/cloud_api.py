from dotenv import load_dotenv
import os
import requests
load_dotenv()

CLOUD_SERVER_URL = os.getenv("CLOUD_SERVER_URL")    

# coordinates APIs
def get_coordinates(parking_id, camera_id):
    url = f'{CLOUD_SERVER_URL+"coordinates/"}{parking_id}/{camera_id}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()[0]
    else:
        return None

def update_coordinates(parking_id, camera_id, data):
    url = f'{CLOUD_SERVER_URL+"coordinates/"}update/{parking_id}/{camera_id}'
    response = requests.put(url, json=data)
    return response.status_code == 200

def insert_coordinates(data):
    url = f'{CLOUD_SERVER_URL+"coordinates/"}add'
    response = requests.post(url, json=data)
    return response.status_code == 201

# parked vehicle APIs
def insert_parked_vehicle(data):
    url = f'{CLOUD_SERVER_URL+"parked_vehicles/"}add_vehicle'
    response = requests.post(url, json=data)
    return response.status_code == 200

def remove_parked_vehicle(data):
    url = f'{CLOUD_SERVER_URL+"parked_vehicles/"}remove_vehicle'
    response = requests.delete(url, json=data)
    if response != 200:
        print(response)
    return response.status_code == 200

def update_parked_vehicle(data):
    url = f'{CLOUD_SERVER_URL+"parked_vehicles/"}update_vehicle'
    response = requests.put(url, json=data)
    return response.status_code == 200

def update_parked_vehicle_list(data):
    url = f'{CLOUD_SERVER_URL+"parked_vehicles/"}update_vehicle_list'
    response = requests.put(url, json=data)
    if response.status_code == 200:
        print(f"[CLOUD] Đã cập nhật danh sách xe đậu lên Cloud Server")
        return True
    else:
        print(f"[CLOUD] Lỗi khi cập nhật danh sách xe đậu lên Cloud Server")
        print(response.json())
        return False

# parking lot, environment, history APIs
def update_parking_lot(data):
    url = f'{CLOUD_SERVER_URL+"parking_slots/"}update_parking_slots'
    response = requests.post(url, json=data)
    if response.status_code == 200:
        print(f"[CLOUD] Đã cập nhật trạng thái bãi xe lên Cloud Server")
        return True
    else:
        print(f"[CLOUD] Lỗi khi cập nhật trạng thái bãi xe lên Cloud Server")
        return False

def update_environment(data):
    url = f'{CLOUD_SERVER_URL+"environments/"}update_environment'
    response = requests.post(url, json=data)
    return response.status_code == 200

def insert_history(data):
    url = f'{CLOUD_SERVER_URL+"histories/"}'
    response = requests.post(url, json=data)
    return response.status_code == 201

# def get_registered_vehicles():