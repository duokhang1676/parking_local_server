import yaml
import cv2 
import os
import vlc
from gtts import gTTS
import numpy as np
import json
from app.modules import globals

def tracking_objects2(tracker, image, detections):
    if len(detections) == 0:
        return [], []

    # Kiểm tra cấu trúc của `detections`
    for det in detections:
        if len(det) != 5:
            print(f"Dữ liệu không hợp lệ: {det}")
            return [], []
##        
    tracked_objects = tracker.update(np.array(detections))
    detected_boxes = []
    track_ids = []
    for x1, y1, x2, y2, track_id in tracked_objects:
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
        detected_boxes.append([x1, y1, x2, y2])
        track_ids.append(int(track_id))
    return detected_boxes[::-1], track_ids[::-1] # Trả về  danh sách bounding boxes và track id 

def tracking_objects(tracker, model, image, confidence_threshold=0.5, device='cuda'):
    results = model(image,  device=device)[0]
    detections = []
    for r in results.boxes.data.tolist():
        x1, y1, x2, y2, conf, cls = r
        if int(cls) == 0 and conf >= confidence_threshold: 
            detections.append([x1, y1, x2, y2, conf])
##
    if len(detections) == 0:
        return [], []

    # Kiểm tra cấu trúc của `detections`
    for det in detections:
        if len(det) != 5:
            print(f"Dữ liệu không hợp lệ: {det}")
            return [], []
##        
    tracked_objects = tracker.update(np.array(detections))
    detected_boxes = []
    track_ids = []
    for x1, y1, x2, y2, track_id in tracked_objects:
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
        detected_boxes.append([x1, y1, x2, y2])
        track_ids.append(int(track_id))
    return detected_boxes[::-1], track_ids[::-1] # Trả về  danh sách bounding boxes và track id 


def read_yaml(file_path):
    # Kiểm tra xem file có tồn tại không
    if not os.path.exists(file_path):
        # Tạo file mới nếu không tồn tại
        with open(file_path, 'w') as file:
            yaml.dump({}, file)  # Lưu một dictionary rỗng vào file YAML

    # Đọc dữ liệu từ file
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file) or {}  # Nếu file rỗng, trả về dict rỗng
    return data

def write_yaml_file(file_path, data):
    # Ghi đè dữ liệu vào file YAML
    with open(file_path, 'w') as file:
        yaml.dump(data, file)
    print(f'YAML file {file_path} written successfully.')
    
# Kiểm tra xem điểm (x, y) có nằm trong bounding box không
def is_point_in_box(x, y, box):
    x_min, y_min, x_max, y_max = box
    return x_min <= x <= x_max and y_min <= y <= y_max

# Hàm vẽ dấu chấm và ID tại tọa độ
def draw_points_and_ids(frame, coordinates_data, hidden_ids, track_ids, detected_boxes, track_licenses, fps, hidden_ids_map_track_licenses):
    cv2.putText(frame, f"FPS: {fps:.0f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    for item in coordinates_data:
        coord = item['coordinate']
        x, y = coord
        license = ""
        # Kiểm tra xem điểm có bị che khuất hay không
        if item['id'] in hidden_ids:
            position = hidden_ids.index(item['id'])
            license = str(hidden_ids_map_track_licenses[position])
            # Vẽ dấu chấm màu đỏ nếu tọa độ bị che khuất
            cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)  # Dấu chấm màu đỏ
        else:
            # Vẽ dấu chấm màu xanh lá nếu không bị che khuất
            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)  # Dấu chấm màu xanh lá
        # # Vẽ ID gần dấu chấm
        # if license == "":
        cv2.putText(frame, str(item['id']), (x - 5, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)  # ID màu đỏ
        # else:
        #     cv2.putText(frame, str(item['id'])+" - " + license, (x - 5, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)  # ID màu đỏ
        #     license = ""

    for i, track_id in enumerate(track_ids):
            x1, y1, x2, y2 = detected_boxes[i]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
            if len(track_licenses) == len(track_ids):
                cv2.putText(frame, f"ID: {track_licenses[i]}", (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            else:
                cv2.putText(frame, f"ID: {int(track_id)}", (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            

# Hàm kiểm tra các điểm bị che khuất
def check_occlusion(coordinates_data, detected_boxes, track_licenses):
    hidden_ids = []  # Danh sách chứa các ID bị che khuất
    visible_ids = []  # Danh sách chứa các ID không bị che khuất
    hidden_ids_map_track_licenses = [] # Danh sách chứa các id được tracking tương ứng với các vị trí bị che khuất
    for item in coordinates_data:
        coord = item['coordinate']
        x, y = coord
        is_hidden = False
        
        # Kiểm tra xem điểm có nằm trong bất kỳ bounding box nào không
        for i, box in enumerate(detected_boxes):
            if is_point_in_box(x, y, box):
                is_hidden = True
                hidden_ids_map_track_licenses.append(track_licenses[i])
                break
        
        if is_hidden:
            hidden_ids.append(item['id'])

        else:
            visible_ids.append(item['id'])
    
    return hidden_ids, visible_ids, hidden_ids_map_track_licenses

def speech_text(text):
    # Tạo tts
    tts = gTTS(text=text, lang='vi', slow=False)
    path = "app/resources/mp3/temp.mp3"
    tts.save(path)
    player = vlc.MediaPlayer(path)
    player.play()

def play_sound(file_name):
    player = vlc.MediaPlayer("app/resources/mp3/" + file_name)
    player.play()

def get_parked_vehicles_from_file():
    with open("app/resources/database/parked_vehicles.json", "r", encoding="utf-8") as f:
        parked_vehicles = json.load(f)
    return parked_vehicles

def save_parked_vehicles_to_file(parked_vehicles):
    with open("app/resources/database/parked_vehicles.json", "w", encoding="utf-8") as f:
        json.dump(parked_vehicles, f, ensure_ascii=False, indent=4)

def get_new_license_plate_from_file():
    with open("app/resources/database/new_license.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["new_license"]

def save_new_license_plate_to_file(new_license_plate):
    with open("app/resources/database/new_license.json", "w", encoding="utf-8") as f:
        json.dump({"new_license": new_license_plate}, f, ensure_ascii=False, indent=4)

def update_screen_display(occupied_list, available_list):
    globals.slot_direction = []
    globals.parking_num_slot = []