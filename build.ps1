$ErrorActionPreference = "Stop"

py process_asset.py
py -c "import PyInstaller" 2>$null
if ($LASTEXITCODE -ne 0) {
    py -m pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller installation failed."
    }
}
py -m PyInstaller --noconfirm --clean --onefile --windowed --name naiwa_desktop_pet --add-data "assets\naiwa.png;assets" naiwa_pet.py
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller build failed."
}
Write-Host "Built dist\naiwa_desktop_pet.exe"
