import cv2
import pandas as pd
from pathlib import Path
import os

LANGUAGES = ['English', 'Portuguese']
IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg']
MAX_BLOBS = 5

def count_blobs(path):
    """Count green blobs in an image"""
    template_img = cv2.imread(path)
    if template_img is None:
        return 0
    mask_green = cv2.inRange(template_img, (0, 210, 0), (40, 255, 40))
    contours_green, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return len(contours_green)

def get_rects(contours_green):
    """Get rects for each blob"""
    rects = []
    for contour in contours_green:
        x, y, w, h = cv2.boundingRect(contour)
        rects.append((x, y, w, h))
    return rects

def get_blob_rects_from_path(path):
    """Get blob rects directly from image path"""
    template_img = cv2.imread(path)
    if template_img is None:
        return []
    mask_green = cv2.inRange(template_img, (0, 210, 0), (40, 255, 40))
    contours_green, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return get_rects(contours_green)

def create_meme_metadata_table():
    """Create a comprehensive table of all meme images with their metadata"""
    base_dir = Path(__file__).parent
    data = []
    for language in LANGUAGES:
        lang_dir = base_dir / language
        if not lang_dir.exists():
            continue
        for ext in IMAGE_EXTENSIONS:
            for image_path in lang_dir.glob(f'*{ext}'):
                try:
                    blob_count = count_blobs(str(image_path))
                    blob_rects = get_blob_rects_from_path(str(image_path))
                    if blob_count > MAX_BLOBS:
                        os.remove(image_path)
                        continue
                    data.append({
                        'filename': image_path.name,
                        'language': language,
                        'blob_count': blob_count,
                        'blob_rects': blob_rects,
                        'full_path': f"Static/Meme/{language}/{image_path.name}"
                    })
                except Exception as e:
                    print(f"Error processing {image_path}: {e}")
                    continue
    df = pd.DataFrame(data)
    df = df.sort_values(['language', 'blob_count'])
    return df

if __name__ == "__main__":
    print("Processing meme images...")
    metadata_df = create_meme_metadata_table()
    output_file = Path(__file__).parent / "meme_metadata.csv"
    metadata_df.to_csv(output_file, index=False)
    print(f"\nMetadata saved to: {output_file}")
    print("\n=== SAMPLE DATA ===")
    print(metadata_df.head(10).to_string(index=False))
    print(f"\nComplete metadata table available as DataFrame with {len(metadata_df)} rows")
    print("Columns: filename, language, blob_count, blob_rects, full_path")
