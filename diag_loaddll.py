import ctypes, os, sys
from pathlib import Path

qt_dll = Path(sys.prefix) / 'Lib' / 'site-packages' / 'PyQt6' / 'Qt6' / 'bin' / 'Qt6Core.dll'
print('Looking for Qt6Core at:', qt_dll)
if not qt_dll.exists():
    # try alternate location
    alt = Path(os.environ.get('PATH','')).parts if hasattr(Path, 'parts') else None
    print('Qt6Core.dll not found at expected location')
else:
    try:
        h = ctypes.WinDLL(str(qt_dll))
        print('Loaded Qt6Core.dll ok (handle)', h._handle)
    except Exception as e:
        import traceback
        print('WinDLL load failed:', e)
        traceback.print_exc()

# Also try to load via name (allowing system search)
try:
    h2 = ctypes.WinDLL('Qt6Core.dll')
    print('Loaded Qt6Core.dll by name OK', h2._handle)
except Exception as e:
    import traceback
    print('WinDLL load by name failed:', e)
    traceback.print_exc()
