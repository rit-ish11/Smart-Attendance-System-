import cv2
import os
def capture_images(roll_no):
    # Create folder for this student's roll_no
    save_path = os.path.join("dataset", roll_no)
    os.makedirs(save_path, exist_ok=True)
    # Start webcam
    cap = cv2.VideoCapture(0)
    count = 0
    print(f"[INFO] Capturing images for Roll No: {roll_no}")
    print("[INFO] Press SPACE to capture an image, 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to grab frame")
            break
        # Show video feed
        cv2.imshow("Capture - Press SPACE to save, q to quit", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord(" "):  # SPACE pressed
            count += 1
            img_name = os.path.join(save_path, f"{count}.jpg")
            cv2.imwrite(img_name, frame)
            print(f"[INFO] Saved {img_name}")
        elif key == ord("q"):  # quit
            break
    cap.release()
    cv2.destroyAllWindows()
    print(f"[INFO] Finished capturing {count} images for {roll_no}")

if __name__ == "__main__":
    roll_no = input("Enter Roll No: ").strip()  # e.g., EE101
    capture_images(roll_no)
