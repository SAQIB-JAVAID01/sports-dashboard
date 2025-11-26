"""
Diagnose PyQt6 DLL load issue on Windows
Shows installed PyQt6 location, Qt DLL paths, and attempts direct load
"""

import sys
import os
import ctypes
from pathlib import Path

print("\n" + "=" * 70)
print("PyQt6 DLL DIAGNOSTIC TOOL")
print("=" * 70)

# 1. Check if PyQt6 is installed
print("\n[1] Checking PyQt6 installation...")
try:
    import PyQt6
    pyqt6_path = Path(PyQt6.__file__).parent
    print(f"    PyQt6 found at: {pyqt6_path}")
    try:
        print(f"    Version: {PyQt6.__version__}")
    except:
        print(f"    Version: (not available)")
except ImportError as e:
    print(f"    ERROR: PyQt6 not installed: {e}")
    sys.exit(1)

# 2. Check PyQt6.QtCore location
print("\n[2] Checking PyQt6.QtCore package...")
try:
    import PyQt6.QtCore as QtCore
    qtcore_path = Path(QtCore.__file__).parent
    print(f"    QtCore path: {qtcore_path}")
except ImportError as e:
    print(f"    ERROR loading QtCore: {e}")

# 3. List Qt DLL files
print("\n[3] Checking for Qt DLL files...")
qt_dll_locations = [
    pyqt6_path / "Qt6Core.dll",
    pyqt6_path / "Qt6Gui.dll",
    pyqt6_path / "Qt6Widgets.dll",
]
for dll_path in qt_dll_locations:
    if dll_path.exists():
        size = dll_path.stat().st_size / 1024 / 1024  # MB
        print(f"    FOUND: {dll_path.name} ({size:.2f} MB)")
    else:
        print(f"    MISSING: {dll_path.name}")

# 4. Check system PATH for Qt DLLs
print("\n[4] Checking system PATH...")
path_dirs = os.environ.get("PATH", "").split(";")
qt_in_path = []
for path_dir in path_dirs:
    if "Qt" in path_dir or "PyQt" in path_dir:
        qt_in_path.append(path_dir)
        if Path(path_dir).exists():
            print(f"    FOUND: {path_dir}")
        else:
            print(f"    MISSING: {path_dir}")

if not qt_in_path:
    print("    (No Qt/PyQt entries in PATH)")

# 5. Check Visual C++ redistributables
print("\n[5] Checking for Microsoft Visual C++ DLLs...")
vc_dlls = ["vcruntime140.dll", "msvcp140.dll", "vccorlib140.dll"]
for dll_name in vc_dlls:
    # Try to load from system
    try:
        ctypes.CDLL(dll_name)
        print(f"    FOUND: {dll_name}")
    except OSError:
        print(f"    MISSING: {dll_name}")

# 6. Attempt to load Qt6Core.dll directly
print("\n[6] Attempting direct DLL load (ctypes)...")
try:
    qt6core_dll = ctypes.CDLL(str(pyqt6_path / "Qt6Core.dll"))
    print(f"    SUCCESS: Qt6Core.dll loaded")
except OSError as e:
    print(f"    FAILED: {e}")
    print(f"    Error code: {e.winerror if hasattr(e, 'winerror') else 'unknown'}")
except Exception as e:
    print(f"    ERROR: {e}")

# 7. Try importing QtWidgets step by step
print("\n[7] Attempting PyQt6 imports...")
try:
    print("    Importing PyQt6...")
    import PyQt6
    print("    OK: PyQt6")
    
    print("    Importing PyQt6.QtCore...")
    from PyQt6 import QtCore
    print("    OK: PyQt6.QtCore")
    
    print("    Importing PyQt6.QtGui...")
    from PyQt6 import QtGui
    print("    OK: PyQt6.QtGui")
    
    print("    Importing PyQt6.QtWidgets...")
    from PyQt6 import QtWidgets
    print("    OK: PyQt6.QtWidgets")
    
    print("\n    SUCCESS: All PyQt6 imports successful!")
    
except ImportError as e:
    print(f"    FAILED at: {e}")
    import traceback
    print("\n    Full traceback:")
    traceback.print_exc()

print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)
print("\nIf Qt6Core.dll failed to load, you likely need:")
print("  - Microsoft Visual C++ Redistributable (2015-2022)")
print("  - Download from: https://support.microsoft.com/en-us/help/2977003")
print("=" * 70 + "\n")
