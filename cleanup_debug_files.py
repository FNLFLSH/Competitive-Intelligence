#!/usr/bin/env python3
"""
Debug File Cleanup Utility
Manages screenshot and HTML debug files generated during scraping
"""

import os
import glob
import shutil
from datetime import datetime

def cleanup_debug_files():
    """Clean up all debug files generated during scraping"""
    print("🧹 CLEANING UP DEBUG FILES")
    print("=" * 40)
    
    # Patterns for debug files
    debug_patterns = [
        "capterra_debug_*.png",
        "capterra_debug_*.html",
        "g2_debug_*.png", 
        "g2_debug_*.html",
        "glassdoor_debug_*.png",
        "glassdoor_debug_*.html",
        "*_debug_*.png",
        "*_debug_*.html"
    ]
    
    total_removed = 0
    
    for pattern in debug_patterns:
        files = glob.glob(pattern)
        if files:
            print(f"📁 Found {len(files)} files matching: {pattern}")
            for file in files:
                try:
                    os.remove(file)
                    print(f"  ✅ Removed: {file}")
                    total_removed += 1
                except Exception as e:
                    print(f"  ❌ Could not remove {file}: {e}")
        else:
            print(f"📁 No files found matching: {pattern}")
    
    print(f"\n🎯 CLEANUP SUMMARY")
    print(f"Total files removed: {total_removed}")
    
    if total_removed == 0:
        print("✨ No debug files found to clean up!")
    else:
        print(f"🧹 Successfully cleaned up {total_removed} debug files")

def create_debug_folder():
    """Create a debug folder to organize debug files if needed"""
    debug_folder = "debug_files"
    if not os.path.exists(debug_folder):
        os.makedirs(debug_folder)
        print(f"📁 Created debug folder: {debug_folder}")
    else:
        print(f"📁 Debug folder already exists: {debug_folder}")
    return debug_folder

def move_debug_files_to_folder():
    """Move existing debug files to a debug folder instead of deleting"""
    debug_folder = create_debug_folder()
    
    print(f"\n📦 MOVING DEBUG FILES TO FOLDER")
    print("=" * 40)
    
    debug_patterns = [
        "capterra_debug_*.png",
        "capterra_debug_*.png",
        "g2_debug_*.png", 
        "g2_debug_*.html",
        "glassdoor_debug_*.png",
        "glassdoor_debug_*.html",
        "*_debug_*.png",
        "*_debug_*.html"
    ]
    
    total_moved = 0
    
    for pattern in debug_patterns:
        files = glob.glob(pattern)
        if files:
            print(f"📁 Found {len(files)} files matching: {pattern}")
            for file in files:
                try:
                    # Create subfolder based on file type
                    if file.endswith('.png'):
                        subfolder = os.path.join(debug_folder, "screenshots")
                    else:
                        subfolder = os.path.join(debug_folder, "html")
                    
                    if not os.path.exists(subfolder):
                        os.makedirs(subfolder)
                    
                    # Move file to subfolder
                    filename = os.path.basename(file)
                    destination = os.path.join(subfolder, filename)
                    shutil.move(file, destination)
                    print(f"  ✅ Moved: {file} → {destination}")
                    total_moved += 1
                except Exception as e:
                    print(f"  ❌ Could not move {file}: {e}")
    
    print(f"\n🎯 MOVE SUMMARY")
    print(f"Total files moved: {total_moved}")
    
    if total_moved == 0:
        print("✨ No debug files found to move!")
    else:
        print(f"📦 Successfully moved {total_moved} debug files to {debug_folder}/")

def enable_debug_mode():
    """Enable debug mode (screenshots and HTML saving)"""
    print("🔧 ENABLING DEBUG MODE")
    print("=" * 30)
    
    # Update the scraper configuration
    scraper_config = """
# Configuration for debug output
DEBUG_CONFIG = {
    "save_screenshots": True,   # Enable screenshot generation
    "save_html": True,          # Enable HTML saving
    "cleanup_old_files": False  # Don't auto-cleanup
}
"""
    
    print("To enable debug mode, update the DEBUG_CONFIG in capterra_scraper.py:")
    print(scraper_config)
    print("This will enable screenshot and HTML generation for debugging purposes.")

def disable_debug_mode():
    """Disable debug mode (no screenshots or HTML saving)"""
    print("🔧 DISABLING DEBUG MODE")
    print("=" * 30)
    
    # Update the scraper configuration
    scraper_config = """
# Configuration for debug output
DEBUG_CONFIG = {
    "save_screenshots": False,  # Disable screenshot generation
    "save_html": False,         # Disable HTML saving
    "cleanup_old_files": True   # Auto-cleanup old files
}
"""
    
    print("To disable debug mode, update the DEBUG_CONFIG in capterra_scraper.py:")
    print(scraper_config)
    print("This will disable screenshot and HTML generation for production use.")

def show_current_status():
    """Show current debug file status"""
    print("📊 CURRENT DEBUG FILE STATUS")
    print("=" * 40)
    
    debug_patterns = [
        "capterra_debug_*.png",
        "capterra_debug_*.html",
        "g2_debug_*.png", 
        "g2_debug_*.html",
        "glassdoor_debug_*.png",
        "glassdoor_debug_*.html",
        "*_debug_*.png",
        "*_debug_*.html"
    ]
    
    total_files = 0
    
    for pattern in debug_patterns:
        files = glob.glob(pattern)
        if files:
            print(f"📁 {pattern}: {len(files)} files")
            total_files += len(files)
            for file in files[:3]:  # Show first 3 files
                file_size = os.path.getsize(file)
                print(f"    - {file} ({file_size} bytes)")
            if len(files) > 3:
                print(f"    ... and {len(files) - 3} more files")
    
    if total_files == 0:
        print("✨ No debug files found!")
    else:
        print(f"\n📊 Total debug files: {total_files}")
        
        # Calculate total size
        total_size = 0
        for pattern in debug_patterns:
            for file in glob.glob(pattern):
                total_size += os.path.getsize(file)
        
        print(f"📏 Total size: {total_size / 1024:.1f} KB")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "clean" or command == "cleanup":
            cleanup_debug_files()
        elif command == "move":
            move_debug_files_to_folder()
        elif command == "enable":
            enable_debug_mode()
        elif command == "disable":
            disable_debug_mode()
        elif command == "status":
            show_current_status()
        else:
            print("❌ Unknown command. Available commands:")
            print("  python cleanup_debug_files.py clean    - Remove all debug files")
            print("  python cleanup_debug_files.py move     - Move debug files to folder")
            print("  python cleanup_debug_files.py enable   - Show how to enable debug mode")
            print("  python cleanup_debug_files.py disable  - Show how to disable debug mode")
            print("  python cleanup_debug_files.py status   - Show current debug file status")
    else:
        # Default: show status and cleanup
        show_current_status()
        print("\n" + "=" * 40)
        cleanup_debug_files() 