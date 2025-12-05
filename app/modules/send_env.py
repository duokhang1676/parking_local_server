def send_env():
    global parking_id
    while True:
        if globals.get_humidity() is not None and globals.get_temperature() is not None and globals.get_light() is not None:
            data = {
                'parking_id': parking_id,
                'temperature': globals.get_temperature(),
                'humidity': globals.get_humidity(),
                'light': int(globals.get_light() / 50)  
            }
            print("update env")
            update_environment(data)
        time.sleep(5)