import sys, os, traceback, importlib
print('Python executable:', sys.executable)
print('Python version:', sys.version)
print('\nAttempting to import PyQt6...')
try:
    import PyQt6
    print('PyQt6 module found:', getattr(PyQt6, '__version__', 'unknown'))
    try:
        import PyQt6.QtWidgets as qw
        print('QtWidgets file:', qw.__file__)
    except Exception as e:
        print('Failed importing QtWidgets:', e)
        traceback.print_exc()
    try:
        import PyQt6.QtCore as qc
        print('QtCore file:', qc.__file__)
    except Exception as e:
        print('Failed importing QtCore:', e)
        traceback.print_exc()
except Exception as e:
    print('PyQt6 import failed:', e)
    traceback.print_exc()

print('\nChecking site-packages paths:')
import site
for p in site.getsitepackages():
    print(' -', p)

print('\nChecking PATH for Qt-related entries:')
for p in os.environ.get('PATH','').split(os.pathsep):
    if 'Qt' in p or 'PyQt' in p or 'Qt6' in p:
        print(' -', p)

print('\nListing PyQt6 package directory (if exists):')
try:
    import PyQt6
    import inspect
    pkg = os.path.dirname(inspect.getfile(PyQt6))
    print('PyQt6 package path:', pkg)
    for root, dirs, files in os.walk(pkg):
        level = root.replace(pkg, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f"{indent}{os.path.basename(root)}/")
        if level >= 2:
            # limit depth
            continue
except Exception:
    print('PyQt6 package directory not available')
