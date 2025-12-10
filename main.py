import threading
from multiprocessing import Manager
from app.modules.utils import play_sound, save_regisstered_vehicles_to_file
from app.modules import tracking_car, detect_license, connect_bgm220, connect_xg26, globals, turn_light_barier
from app.modules.cloud_api import get_registered_vehicles

def main():
    # Khởi tạo shared memory cho give_way TRƯỚC KHI chạy bất kỳ thread nào
    manager = Manager()
    shared_give_way = manager.Value('b', False)
    globals.give_way_shared = shared_give_way
    
    threading.Thread(target=play_sound, args=("start-program.mp3",)).start()
    threading.Thread(target=save_regisstered_vehicles_to_file, args=(get_registered_vehicles(),)).start()
    threading.Thread(target=tracking_car.start_tracking_car, daemon=True).start()
    threading.Thread(target=detect_license.start_detect_license, daemon=True).start()
    threading.Thread(target=connect_bgm220.start_connect_bgm220, daemon=True).start()
    threading.Thread(target=connect_xg26.start_connect_xg26, daemon=True).start()
    threading.Thread(target=turn_light_barier.start_turn_light_barier, daemon=True).start()
if __name__ == '__main__':
    main()
    while True:
        try:
            # Keep the main thread alive
            threading.Event().wait(1)
        except KeyboardInterrupt:
            print("Exiting...")
            break   