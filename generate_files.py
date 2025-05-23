import os

def create_test_file(size_mb, filename):
    size_bytes = size_mb * 1024 * 1024
    
    with open(filename, 'wb') as f:
        f.write(os.urandom(size_bytes))
    
    print(f"Created test file: {filename} ({size_mb} MB)")

volumes = [10, 50, 100]
for vol in volumes:
    create_test_file(vol, "file_"+str(vol)+"mb.dat")