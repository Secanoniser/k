import os
import zipfile
import shutil
import sys

def create_highly_compressible_file(output_path, size_mb=10):
    """Creates a file filled with repeating data (optimal for compression)."""
    chunk = b"0" * 1024 * 1024  # 1MB of zeros (compresses to almost nothing)
    with open(output_path, "wb") as f:
        for _ in range(size_mb):
            f.write(chunk)

def compress_to_smallest_zip(input_zip, output_zip, max_mb=25):
    """Takes an input ZIP, extracts, and repacks it into the smallest possible ZIP."""
    temp_dir = "temp_zip_contents"
    os.makedirs(temp_dir, exist_ok=True)

    # 1. Extract original ZIP
    with zipfile.ZipFile(input_zip, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    # 2. Create a highly compressible dummy file (optional, for bomb effect)
    dummy_file = os.path.join(temp_dir, "dummy_data.bin")
    create_highly_compressible_file(dummy_file, 10)  # 10MB of zeros (compresses to ~1KB)

    # 3. Recompress with maximum settings
    with zipfile.ZipFile(output_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)

    # 4. Verify output size
    output_size = os.path.getsize(output_zip) / (1024 * 1024)  # in MB
    if output_size > max_mb:
        print(f"Warning: Output ZIP is {output_size:.2f} MB (target was ≤{max_mb} MB).")
    else:
        print(f"Success! Output ZIP: {output_size:.2f} MB")

    # 5. Cleanup
    shutil.rmtree(temp_dir)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python make_small_zip_bomb.py <input_zip> <output_zip> [max_mb]")
        sys.exit(1)

    input_zip = sys.argv[1]
    output_zip = sys.argv[2]
    max_mb = int(sys.argv[3]) if len(sys.argv) > 3 else 25

    if not os.path.exists(input_zip):
        print(f"Error: Input file '{input_zip}' not found!")
        sys.exit(1)

    compress_to_smallest_zip(input_zip, output_zip, max_mb)