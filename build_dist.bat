REM --log-level=WARN
REM --onefile

pyinstaller ^
  --noconfirm  ^
  --noconsole ^
  --onefile ^
  --add-data="avif-logo-rgb.svg.ico;." ^
  --add-data="avifenc.exe;." ^
  --icon="avif-logo-rgb.svg.ico" ^
  avifhelper.py