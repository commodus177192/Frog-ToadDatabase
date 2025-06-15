import os
import shutil

# Copy a file to the specified directory and return the destination path
def copy_file_to_dir(src_path, dest_dir):
    # Ensure the destination directory exists
    os.makedirs(dest_dir, exist_ok=True)
    # Generate a unique destination path by appending a number if needed
    base_name = os.path.basename(src_path)
    dest_path = os.path.join(dest_dir, base_name)
    counter = 1
    while os.path.exists(dest_path):
        name, ext = os.path.splitext(base_name)
        dest_path = os.path.join(dest_dir, f"{name}_{counter}{ext}")
        counter += 1
    # Copy the file
    shutil.copy(src_path, dest_path)
    return dest_path
