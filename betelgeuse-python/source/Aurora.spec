# Build with: python -m PyInstaller --noconfirm Aurora.spec
import os
from pathlib import Path

root = Path(SPECPATH)
# Resolve Windows ICU from Windows, never an unrelated copy on PATH.
icu = Path(os.environ['WINDIR']) / 'System32' / 'icuuc.dll'
a = Analysis(
    [str(root / 'aurora.py')],
    pathex=[], binaries=[(str(icu), '.')], datas=[], hiddenimports=[],
    hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[],
    noarchive=False, optimize=0,
)
# ICU is an operating-system component on supported Windows versions.
# Use the target computer's copy instead of redistributing our Windows DLLs.
a.binaries = [entry for entry in a.binaries
              if not Path(entry[0].replace('\\', '/')).name.lower().startswith('icu')]
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [], name='BetelgeuseAI',
    debug=False, bootloader_ignore_signals=False, strip=False, upx=False,
    runtime_tmpdir=None, console=False, disable_windowed_traceback=False,
    icon=[str(root / 'aurora.ico')],
)
