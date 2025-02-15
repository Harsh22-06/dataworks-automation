from pathlib import Path
import shutil
import zipfile

DATA_DIR = Path("/data")

@secure_file_operation
def secure_file_copy(src: Path, dest: Path):
    shutil.copy2(src, dest)

@secure_file_operation  
def secure_file_move(src: Path, dest: Path):
    shutil.move(src, dest)

@secure_file_operation
def secure_zip_operation(input_path: Path, output_path: Path):
    with zipfile.ZipFile(output_path, 'w') as zipf:
        for file in input_path.rglob('*'):
            zipf.write(file, arcname=file.relative_to(input_path))

@secure_file_operation
def validate_file_signature(file_path: Path):
    signatures = {
        '.png': b'\x89PNG',
        '.jpg': b'\xFF\xD8\xFF',
        '.sqlite': b'SQLite format 3'
    }
    with open(file_path, 'rb') as f:
        header = f.read(16)
        for ext, sig in signatures.items():
            if file_path.suffix == ext and not header.startswith(sig):
                raise HTTPException(400, f"Invalid {ext} file signature")
