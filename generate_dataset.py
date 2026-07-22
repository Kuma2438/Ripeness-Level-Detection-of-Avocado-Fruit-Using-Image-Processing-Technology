import os
import cv2
import numpy as np

def generate_sample_dataset(output_dir=r"d:\Project\program\dataset"):
    """
    Generates synthetic avocado sample images across 3 ripeness categories:
    - Unripe: Bright Green
    - Mid-ripe: Olive Green / Brownish
    - Ripe: Dark Purple / Blackish
    """
    categories = ["unripe", "mid_ripe", "ripe"]
    for cat in categories:
        os.makedirs(os.path.join(output_dir, cat), exist_ok=True)

    np.random.seed(42)

    for cat in categories:
        for i in range(15):
            img = np.ones((480, 640, 3), dtype=np.uint8) * 220 # Background
            
            center = (320 + np.random.randint(-15, 16), 240 + np.random.randint(-15, 16))
            axes = (90 + np.random.randint(-5, 6), 130 + np.random.randint(-8, 9))
            angle = np.random.randint(-15, 16)
            
            if cat == "unripe":
                base_bgr = [np.random.randint(30, 60), np.random.randint(130, 180), np.random.randint(40, 80)]
            elif cat == "mid_ripe":
                base_bgr = [np.random.randint(20, 45), np.random.randint(85, 115), np.random.randint(65, 95)]
            else: # ripe
                base_bgr = [np.random.randint(25, 45), np.random.randint(30, 55), np.random.randint(40, 65)]
                
            mask = np.zeros((480, 640), dtype=np.uint8)
            cv2.ellipse(mask, center, axes, angle, 0, 360, 255, -1)
            
            for c in range(3):
                noise = np.random.normal(0, 15, (480, 640)).astype(np.int16)
                channel = base_bgr[c] + noise
                channel = np.clip(channel, 0, 255).astype(np.uint8)
                img[:, :, c] = np.where(mask == 255, channel, img[:, :, c])
                
            # Texture spots
            spots_mask = (np.random.rand(480, 640) > 0.95) & (mask == 255)
            img[spots_mask] = np.clip(img[spots_mask].astype(int) - 35, 0, 255).astype(np.uint8)

            filepath = os.path.join(output_dir, cat, f"{cat}_{i+1:02d}.jpg")
            cv2.imwrite(filepath, img)
            
    print(f"Sample Dataset generated successfully in '{output_dir}'")
    return output_dir

if __name__ == "__main__":
    generate_sample_dataset()
