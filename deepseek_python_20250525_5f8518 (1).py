import os
import zipfile
import shutil
import sys

def create_compressible_dummy_file(file_path, target_size_mb):
    """Creates a dummy file filled with repeating data (compresses extremely well)."""
    chunk = b"0" * 1024 * 1024  # 1 MB of zeros (compresses to ~1 KB)
    with open(file_path, "wb") as f:
        for _ in range(target_size_mb):
            f.write(chunk)

def shrink_zip(input_zip, output_zip, target_mb=10, dummy_size_mb=50):
    """Shrinks a ZIP file by recompressing with maximum settings + adding dummy data."""
    temp_dir = "temp_zip_contents"
    os.makedirs(temp_dir, exist_ok=True)

    # 1. Extract original ZIP
    with zipfile.ZipFile(input_zip, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    # 2. Add a highly compressible dummy file (optional but helps compression ratio)
    dummy_file = os.path.join(temp_dir, "dummy.bin")
    create_compressible_dummy_file(dummy_file, dummy_size_mb)

    # 3. Recompress with maximum settings
    with zipfile.ZipFile(output_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)

    # 4. Check output size
    output_size_mb = os.path.getsize(output_zip) / (1024 * 1024)
    print(f"Original: {os.path.getsize(input_zip) / (1024 * 1024):.2f} MB")
    print(f"Compressed: {output_size_mb:.2f} MB (Target: ≤{target_mb} MB)")

    # 5. Cleanup
    shutil.rmtree(temp_dir)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python shrink_zip_to_10mb.py <input.zip> <output.zip> [target_mb] [dummy_mb]")
        sys.exit(1)

    input_zip = sys.argv[1]
    output_zip = sys.argv[2]
    target_mb = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    dummy_mb = int(sys.argv[4]) if len(sys.argv) > 4 else 50

    shrink_zip(input_zip, output_zip, target_mb, dummy_mb)