import threading
from app.modules.utils import play_sound
from app.modules import tracking_car, detect_qr, detect_license, connect_bgm220
def main():
    threading.Thread(target=play_sound, args=("start-program.mp3",)).start()
    threading.Thread(target=tracking_car.start_tracking_car, daemon=True).start()
    #threading.Thread(target=detect_qr.start_detect_qr, daemon=True).start()
    threading.Thread(target=detect_license.start_detect_license, daemon=True).start()
    threading.Thread(target=connect_bgm220.start_connect_bgm220, daemon=True).start()
if __name__ == '__main__':
    main()
    while True:
        try:
            # Keep the main thread alive
            threading.Event().wait(1)
        except KeyboardInterrupt:
            print("Exiting...")
            break   