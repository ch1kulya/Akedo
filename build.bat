:: Pyinstaller build script
cd C:\Users\ch1ka\Desktop\Akedo
nuitka --standalone --output-dir=build --windows-console-mode=disable --noinclude-default-mode=error --deployment --nofollow-import-to=unittest --windows-icon-from-ico=logo.ico --include-data-dir=audio=audio Akedo.py
