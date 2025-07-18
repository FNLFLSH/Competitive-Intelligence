# Debug File Management System

This system manages screenshot and HTML debug files generated during web scraping to keep your workspace clean.

## 🎯 Overview

The scraper generates debug files (screenshots and HTML) during development to help troubleshoot scraping issues. In production, these files are not needed and can clutter your workspace.

## 🛠️ Quick Commands

### Clean up all debug files:
```bash
python cleanup_debug_files.py clean
```

### Move debug files to organized folder:
```bash
python cleanup_debug_files.py move
```

### Check current debug file status:
```bash
python cleanup_debug_files.py status
```

### Configure debug settings:
```bash
# Set production mode (no debug files)
python backend/debug_config.py production

# Set development mode (debug files enabled)
python backend/debug_config.py development

# Show current configuration
python backend/debug_config.py show
```

## 🔧 Configuration

### Production Mode (Default)
- ✅ No screenshot generation
- ✅ No HTML file saving
- ✅ Auto-cleanup of old files
- ✅ Clean workspace

### Development Mode
- 📸 Screenshots enabled
- 📄 HTML files enabled
- 📁 Files saved to `debug_files/` folder
- 🔍 Full debugging capabilities

## 📁 File Types Cleaned

The system automatically detects and cleans:
- `capterra_debug_*.png` - Screenshots from Capterra scraping
- `capterra_debug_*.html` - HTML files from Capterra scraping
- `g2_debug_*.png` - Screenshots from G2 scraping
- `g2_debug_*.html` - HTML files from G2 scraping
- `glassdoor_debug_*.png` - Screenshots from Glassdoor scraping
- `glassdoor_debug_*.html` - HTML files from Glassdoor scraping

## 🚀 Integration with Your Frontend

The debug system is **completely separate** from your frontend functionality:

✅ **No impact on scraping results**
✅ **No impact on sentiment analysis**
✅ **No impact on API responses**
✅ **No impact on frontend display**

Your multi-product sentiment analysis continues to work exactly as before, just without the debug file clutter.

## 🔄 Automatic Cleanup

The system automatically cleans up old debug files when:
- The scraper starts (if `auto_cleanup_on_start` is enabled)
- You run the cleanup utility manually
- You switch to production mode

## 💡 Best Practices

1. **Development**: Use development mode when debugging scraping issues
2. **Production**: Use production mode for clean, fast scraping
3. **Regular cleanup**: Run cleanup periodically to keep workspace tidy
4. **Organized storage**: Use the move command to organize debug files if needed

## 🎯 Your Multi-Product Sentiment System

Your sentiment analysis system works perfectly with this debug management:

- **Company-level sentiment**: ✅ Working
- **Product-level sentiment**: ✅ Working  
- **Multi-platform support**: ✅ Ready for G2/Glassdoor
- **Frontend integration**: ✅ Compatible
- **Clean workspace**: ✅ No debug file clutter

The debug system is purely for development convenience and doesn't affect your core functionality at all! 