# 🚀 Building Standalone Finance Tracker

This guide will help you create standalone executable files (.exe) of your Finance Tracker application that can run on any Windows computer without requiring Python to be installed.

## 📋 Prerequisites

- Python 3.8+ installed
- All project dependencies installed (`pip install -r requirements.txt`)
- Your Google Sheets credentials configured (`credentials.json`)

## 🛠️ Method 1: Automated Build Script (Recommended)

### Step 1: Install Build Dependencies
```bash
pip install -r build-requirements.txt
```

### Step 2: Run the Build Script
```bash
python scripts/build_standalone.py
```

This script will:
- ✅ Install PyInstaller if not already installed
- 🧹 Clean previous build artifacts
- 🔨 Build both CLI and GUI versions
- 📋 Copy essential files to the distribution folder
- 🚀 Create a convenient launcher script

### Step 3: Find Your Executables
After successful build, you'll find in the `dist/` folder:
- **FinanceTracker.exe** - CLI version (command-line interface)
- **FinanceTrackerGUI.exe** - GUI version (graphical interface)
- **launch.bat** - Easy launcher to choose between CLI and GUI
- All necessary configuration files and data folders

## 🛠️ Method 2: Manual PyInstaller Commands

### For CLI Version:
```bash
pyinstaller --onefile --console --name FinanceTracker main.py
```

### For GUI Version:
```bash
pyinstaller --onefile --windowed --name FinanceTrackerGUI gui_finance_tracker.py
```

### Using Spec Files (Advanced):
```bash
pyinstaller finance_tracker.spec
pyinstaller finance_tracker_gui.spec
```

## 🛠️ Method 3: Auto-py-to-exe (GUI Tool)

If you prefer a graphical interface for building:

### Step 1: Install auto-py-to-exe
```bash
pip install auto-py-to-exe
```

### Step 2: Launch the GUI
```bash
auto-py-to-exe
```

### Step 3: Configure Settings
- **Script Location**: Choose `main.py` (CLI) or `gui_finance_tracker.py` (GUI)
- **Onefile**: Select "One File"
- **Console Window**: 
  - CLI version: "Console Based"
  - GUI version: "Window Based (hide the console)"
- **Additional Files**: Add your `credentials.json`, `config/`, `data/` folders
- Click "Convert .py to .exe"

## 📦 Distribution Package

After building, your `dist/` folder will contain everything needed to run the application:

```
dist/
├── FinanceTracker.exe          # CLI executable
├── FinanceTrackerGUI.exe       # GUI executable
├── launch.bat                  # Launcher script
├── credentials.json            # Google Sheets credentials
├── user_settings.json          # User settings
├── config/                     # Configuration files
├── data/                       # Data files
└── README.md                   # Documentation
```

## 🚚 How to Distribute

1. **Zip the entire `dist/` folder**
2. **Share the zip file** with anyone who wants to use your Finance Tracker
3. **Recipients just need to**:
   - Extract the zip file
   - Double-click `launch.bat` OR
   - Run `FinanceTrackerGUI.exe` directly

## 🔧 Troubleshooting

### Common Issues and Solutions:

#### 1. "Module not found" errors
**Solution**: Add missing modules to the `hiddenimports` list in the `.spec` files

#### 2. "Credentials.json not found"
**Solution**: Ensure `credentials.json` is in the same directory as the executable

#### 3. Large executable size
**Solution**: Use `--exclude-module` to remove unused modules:
```bash
pyinstaller --onefile --exclude-module matplotlib --exclude-module numpy main.py
```

#### 4. Slow startup time
**Solution**: Use `--onedir` instead of `--onefile` for faster startup:
```bash
pyinstaller --onedir --console main.py
```

#### 5. Antivirus false positives
**Solution**: 
- Add the `dist/` folder to antivirus exclusions
- Use `--debug=imports` to see what's being bundled
- Consider code signing for professional distribution

### Build Optimization Tips:

#### Reduce File Size:
```bash
# Exclude unnecessary modules
pyinstaller --onefile --exclude-module matplotlib --exclude-module scipy main.py

# Use UPX compression (requires UPX to be installed)
pyinstaller --onefile --upx-dir=/path/to/upx main.py
```

#### Debug Build Issues:
```bash
# Build with debug info
pyinstaller --onefile --debug=all main.py

# Test imports
pyinstaller --onefile --debug=imports main.py
```

## 🎯 Testing Your Standalone Build

1. **Test on the build machine**:
   ```bash
   cd dist
   FinanceTrackerGUI.exe
   ```

2. **Test on a clean machine** (without Python installed):
   - Copy the `dist/` folder to another computer
   - Run the executable to ensure all dependencies are included

3. **Test both interfaces**:
   - GUI: `FinanceTrackerGUI.exe`
   - CLI: `FinanceTracker.exe`

## 📊 Build Statistics

After building, you can check the size and contents:
- **Typical size**: 50-100 MB (includes Python interpreter and all dependencies)
- **Startup time**: 3-5 seconds (first run may be slower)
- **Memory usage**: 50-200 MB depending on operations

## 🔄 Updating Your Standalone Build

When you make changes to your code:
1. Run the build script again: `python scripts/build_standalone.py`
2. The script will clean old builds and create fresh executables
3. Test the new build before distributing

## 💡 Pro Tips

1. **Always test your build** on a machine without Python installed
2. **Include a README** in your distribution package
3. **Version your builds** by adding version numbers to executable names
4. **Consider code signing** for professional distribution
5. **Keep build logs** for troubleshooting future builds

## 🆘 Need Help?

If you encounter issues:
1. Check the build logs for error messages
2. Ensure all dependencies are listed in `requirements.txt`
3. Test the application in development mode first
4. Consider using the spec files for more control over the build process

Happy building! 🎉 