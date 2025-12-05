
# Giao tiếp serial với micro controller
def start_connect_bgm220():
   # Thiết lập cổng Serial (kiểm tra cổng COM trong Device Manager)
    port = "/dev/ttyUSB0"  
    baudrate = 9600
    global car_in, car_out, id_code_in, id_code_out, license_car_in, license_car_out, new_car, customer_type, parked_vehicles, parking_id, registered_vehicles, update_coordinate_arduino, direction, slot_table, qr_thread, license_thread, start_detect_qr, start_detect_license, qr_first
    # Thiết lập cổng Serial (kiểm tra cổng COM trong Device Manager)
    try:
        # Kết nối Serial
        ser = serial.Serial(port, baudrate, timeout=1)
        print(f"Kết nối thành công với {port}")
        threading.Thread(target=play_sound, args=('resources/mp3/arduino_connection.mp3',)).start()
        # API arduino
        # 0: barie_in:0 (đóng barie vào)
        # 1: barie_in:1 (mở barie vào)
        # 2: barie_out:0 (đóng barie ra)
        # 3: barie_out:1 (mở barie ra)
        # 4: update_slot (cập nhật lại số chỗ trống và hướng đi)
        while True:
            time.sleep(1)
            if update_coordinate_arduino:
                print("Cập nhật direction")
                update_coordinate_arduino = False
                # ser.write(("4" + '\n').encode('utf-8'))
                text = f" {str(direction[3])}-{str(direction[2])}    {str(direction[1])}-{str(direction[0])}   "
                ser.write((text + '\n').encode('utf-8'))
                time.sleep(2)
                sum_slot = sum(slot_table)
                text = str(slot_table[0])+","+str(slot_table[1])+","+str(slot_table[2])+","+str(slot_table[3])+","+str(sum_slot)
                ser.write((text + '\n').encode('utf-8'))
            # Xe đi vào
            if car_in and id_code_in != "" and license_car_in != "":
                # Kiểm tra customer_type
                if customer_type == "customer":
                    # Kiểm tra biển số xe đã được đăng ký chưa
                    user_valid = False
                    license_valid = False
                    for vehicle in registered_vehicles:
                        if vehicle['user_id'] == id_code_in:
                            user_valid = True
                            if vehicle['license_plate'] == license_car_in:
                                license_valid = True
                                # mở barie
                                new_car = license_car_in
                                print("new car: ", new_car)
                                print("Xe vào bãi đỗ")
                                ser.write(("1" + '\n').encode('utf-8'))
                                threading.Thread(target=play_sound, args=('resources/mp3/xin-moi-vao.mp3',)).start()
                                qr_first = False
                                # Tạo mới parked_vehicle
                                time_in = datetime.datetime.utcnow()+ datetime.timedelta(hours=7) 
                                parked_vehicle = {
                                    'user_id': id_code_in,
                                    'customer_type': customer_type,
                                    'time_in': time_in.isoformat(),
                                    'license_plate': license_car_in,
                                    'slot_name': '',
                                    'num_slot': 0
                                }
                                # Thêm parked_vehicle vào danh sách
                                parked_vehicles.append(parked_vehicle)
                                # Gửi dữ liệu lên server
                                # data = {
                                #     'parking_id': parking_id,
                                #     'vehicle': parked_vehicle
                                # }
                                # if insert_parked_vehicle(data):
                                #     print("Gửi parked_vehicle thành công!")
                                # else:
                                #     print("Gửi parked_vehicle không thành công!")
                                break
                    car_in = False
                    if not user_valid:
                        print("Khách hàng không hợp lệ")
                        threading.Thread(target=play_sound, args=('resources/mp3/khach-hang-khong-hop-le.mp3',)).start()
                    elif not license_valid:
                        print("Biển số không hợp lệ")
                        threading.Thread(target=play_sound, args=('resources/mp3/bien-so-khong-hop-le.mp3',)).start()

            # Xe đi ra
            if car_out and id_code_out != "" and license_car_out != "":
                # Kiểm tra id_code_out và license có trong danh sách parked_vehicles không
                user_valid = False
                license_valid = False
                for vehicle in parked_vehicles:
                    if vehicle['user_id'] == id_code_out:
                        user_valid = True
                        if vehicle['license_plate'] == license_car_out:
                            license_valid = True
                            # Nếu có, thì xe đã được đỗ và có thể ra
                            print("Xe ra khỏi bãi đỗ")
                            threading.Thread(target=play_sound, args=('resources/mp3/tam-biet-quy-khach.mp3',)).start()
                            # Mở barie ra
                            ser.write(("3" + '\n').encode('utf-8'))
                            # Tạo history
                            user_id = ""
                            total_price = 0
                            time_in = vehicle['time_in']
                            time_out = datetime.datetime.utcnow()+ datetime.timedelta(hours=7)
                            
                            # start_time_parsed = datetime.fromisoformat(time_in)

                            # # Hiệu thời gian
                            # elapsed = time_out - start_time_parsed

                            # # Đổi thành số giờ (dưới dạng float)
                            # parking_time = elapsed.total_seconds() / 3600
                            parking_time = 0.1
                            if vehicle['customer_type'] == "customer":
                                user_id = vehicle['user_id']
                                total_price = 0
                            else:
                                user_id = "guest"
                                # Tính toán giá tiền dựa trên thời gian đỗ xe
                                # 5 giời đầu tiên là 50k, từ giờ thứ 6 là 10k
                                total_price = 50000 + (int(parking_time.split(':')[0]) - 5) * 10000  
                            history = {
                                'parking_id': parking_id,
                                'user_id': user_id,
                                'license_plate': vehicle['license_plate'],
                                'time_in': time_in,
                                'time_out': time_out.isoformat(),
                                'parking_time': parking_time,
                                'total_price': total_price,
                            }
                            # Gửi dữ liệu lên server
                            if insert_history(history):
                                print("Gửi history thành công!")
                            else:
                                print("Gửi history không thành công!")

                            # Xóa parked_vehicle khỏi danh sách
                            parked_vehicles.remove(vehicle)
                            # Xóa trên server
                            if remove_parked_vehicle(vehicle):
                                print("Xóa parked-vehicle thành công")
                            else:
                                print("Xóa parked-vehicle không thành công")

                            break
                car_out = False
                if not user_valid:
                    print("Khách hàng không hợp lệ")
                    threading.Thread(target=play_sound, args=('resources/mp3/khach-hang-khong-hop-le.mp3',)).start()
                elif not license_valid:
                    print("Biển số không hợp lệ")
                    threading.Thread(target=play_sound, args=('resources/mp3/bien-so-khong-hop-le.mp3',)).start()

            # Danh sách dữ liệu từ Arduino
            if ser.in_waiting > 0:
                for _ in range(ser.in_waiting):
                    # Đọc dữ liệu từ Arduino
                    data = ser.readline().decode('utf-8').strip()
                    # Kiểm tra định dạng và tách key, value
                    if ":" in data:
                        key, value = data.split(":", 1)
                        print(f"Key: {key}, Value: {value}")
                        # Xe vào
                        if key == "car_in":
                            if value == "1":
                                car_in = True
                                #if license_thread:
                                #license_thread = False
                                start_detect_license = True
                                if qr_thread:
                                    qr_thread = False
                                    start_detect_qr = True
                            else:
                                car_in = False
                                id_code_in = ""
                                license_car_in = ""
                                # đóng barie vào
                                ser.write(("0" + '\n').encode('utf-8'))
                        # Xe ra
                        elif key == "car_out":
                            if value == "1":
                                car_out = True  
                                if license_thread:
                                    license_thread = False
                                    start_detect_license = True
                                if qr_thread:
                                    qr_thread = False
                                    start_detect_qr = True
                            else:
                                car_out = False
                                id_code_out = ""
                                license_car_out = ""
                                # đóng barie ra
                                ser.write(("2" + '\n').encode('utf-8'))
                                
    

    except serial.SerialException:
        print(f"Không thể kết nối tới {port}")
    except KeyboardInterrupt:
        print("\nĐã thoát chương trình.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Đã đóng cổng Serial.")