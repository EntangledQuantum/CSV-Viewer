import os
import sys
import platform
import subprocess

def build_exe():
    """Build a single executable using PyInstaller with custom icon"""
    
    print("Starting build process...")
    
    # Build command for PyInstaller using Python module
    cmd = [
        sys.executable,             # Use the current Python executable
        '-m', 'PyInstaller',        # Run PyInstaller as a module
        '--onefile',                # Create a single executable file
        '--windowed',               # Don't show the console window when running
        '--name=LandmarkCSVViewer', # Name of the output executable
        '--icon=image.png',         # Use the image.png as an icon
        '--clean',                  # Clean PyInstaller cache
        '--noupx',                  # Don't use UPX compression (reduces false positives)
        '--disable-windowed-traceback',  # Disable traceback for windowed app
        '--version-file=version_info.txt',  # Add version information
    ]
    
    # Add data file with the correct separator for the platform
    if platform.system() == 'Windows':
        cmd.append('--add-data=image.png;.')
    else:
        cmd.append('--add-data=image.png:.')
    
    # Add the script to package
    cmd.append('run.py')
    
    print("Running command:", ' '.join(cmd))
    
    # Run PyInstaller
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\nBuild completed successfully!")
        print("Executable can be found in the ./dist directory")
        
        # Create information about the application
        print("\nCreating additional identification files...")
        create_identification_files()
    else:
        print("\nBuild failed with error code:", result.returncode)

def create_identification_files():
    """Create files that help identify the application as legitimate"""
    dist_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist')
    
    # Create a README.txt file in the dist directory
    readme_path = os.path.join(dist_dir, 'README.txt')
    with open(readme_path, 'w') as f:
        f.write("LandmarkCSV Viewer Application\n")
        f.write("==============================\n\n")
        f.write("This application was built using PyInstaller and is completely safe to use.\n")
        f.write("Some anti-virus software may incorrectly flag this executable as suspicious.\n")
        f.write("This is a known false positive with PyInstaller-packaged applications.\n\n")
        f.write("If you encounter any security warnings, you can safely add this application\n")
        f.write("to your anti-virus exclusions or whitelist.\n\n")
        f.write("For more information about the application, see the documentation.\n")
    
    print(f"Created {readme_path}")

if __name__ == "__main__":
    build_exe()