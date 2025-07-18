#!/usr/bin/env python3
"""
Debug Configuration
Centralized configuration for debug features across all scrapers
"""

# Debug Configuration - Modify these settings as needed
DEBUG_CONFIG = {
    # Screenshot and HTML generation
    "save_screenshots": False,  # Set to True to save screenshots
    "save_html": False,         # Set to True to save HTML files
    
    # Auto-cleanup settings
    "cleanup_old_files": True,  # Set to True to auto-cleanup old debug files
    "auto_cleanup_on_start": True,  # Clean up files when scraper starts
    
    # Debug folder settings
    "use_debug_folder": False,  # Set to True to save files in debug_files/ folder
    "debug_folder": "debug_files",
    
    # Logging settings
    "verbose_logging": True,    # Set to False to reduce console output
    "show_progress": True,      # Show progress indicators
    
    # Performance settings
    "reduced_timeouts": False,  # Set to True for faster scraping (may fail more)
    "headless_mode": True,      # Set to False to see browser (for debugging)
}

def get_debug_config():
    """Get the current debug configuration"""
    return DEBUG_CONFIG.copy()

def update_debug_config(**kwargs):
    """Update debug configuration with new values"""
    global DEBUG_CONFIG
    DEBUG_CONFIG.update(kwargs)
    return DEBUG_CONFIG

def enable_debug_mode():
    """Enable full debug mode"""
    return update_debug_config(
        save_screenshots=True,
        save_html=True,
        cleanup_old_files=False,
        verbose_logging=True,
        show_progress=True
    )

def disable_debug_mode():
    """Disable debug mode for production"""
    return update_debug_config(
        save_screenshots=False,
        save_html=False,
        cleanup_old_files=True,
        verbose_logging=False,
        show_progress=True
    )

def enable_minimal_debug():
    """Enable minimal debug (screenshots only)"""
    return update_debug_config(
        save_screenshots=True,
        save_html=False,
        cleanup_old_files=True,
        verbose_logging=True
    )

# Production-ready configuration
PRODUCTION_CONFIG = {
    "save_screenshots": False,
    "save_html": False,
    "cleanup_old_files": True,
    "auto_cleanup_on_start": True,
    "use_debug_folder": False,
    "verbose_logging": False,
    "show_progress": True,
    "reduced_timeouts": False,
    "headless_mode": True,
}

# Development configuration
DEVELOPMENT_CONFIG = {
    "save_screenshots": True,
    "save_html": True,
    "cleanup_old_files": False,
    "auto_cleanup_on_start": False,
    "use_debug_folder": True,
    "verbose_logging": True,
    "show_progress": True,
    "reduced_timeouts": False,
    "headless_mode": False,
}

def set_production_mode():
    """Set configuration for production use"""
    global DEBUG_CONFIG
    DEBUG_CONFIG = PRODUCTION_CONFIG.copy()
    return DEBUG_CONFIG

def set_development_mode():
    """Set configuration for development use"""
    global DEBUG_CONFIG
    DEBUG_CONFIG = DEVELOPMENT_CONFIG.copy()
    return DEBUG_CONFIG

if __name__ == "__main__":
    print("🔧 DEBUG CONFIGURATION UTILITY")
    print("=" * 40)
    
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "production":
            set_production_mode()
            print("✅ Set to PRODUCTION mode (no debug files)")
        elif command == "development":
            set_development_mode()
            print("✅ Set to DEVELOPMENT mode (debug files enabled)")
        elif command == "enable":
            enable_debug_mode()
            print("✅ Enabled FULL DEBUG mode")
        elif command == "disable":
            disable_debug_mode()
            print("✅ Disabled debug mode")
        elif command == "minimal":
            enable_minimal_debug()
            print("✅ Enabled MINIMAL DEBUG mode (screenshots only)")
        elif command == "show":
            print("📊 Current Configuration:")
            for key, value in DEBUG_CONFIG.items():
                print(f"  {key}: {value}")
        else:
            print("❌ Unknown command. Available commands:")
            print("  python debug_config.py production  - Set production mode")
            print("  python debug_config.py development - Set development mode")
            print("  python debug_config.py enable      - Enable full debug")
            print("  python debug_config.py disable     - Disable debug")
            print("  python debug_config.py minimal     - Enable minimal debug")
            print("  python debug_config.py show        - Show current config")
    else:
        print("📊 Current Configuration:")
        for key, value in DEBUG_CONFIG.items():
            print(f"  {key}: {value}")
        
        print("\n💡 Usage:")
        print("  python debug_config.py production  - No debug files")
        print("  python debug_config.py development - Debug files enabled")
        print("  python debug_config.py show        - Show current settings") 