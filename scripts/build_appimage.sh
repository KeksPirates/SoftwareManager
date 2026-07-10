#!/usr/bin/env bash

echo "Cleaning up"
rm -rf dist build

echo "Installing Dependencies"
mkdir build
cd build

curl -L -o appimagetool-x86_64.AppImage https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage

curl -L -o python.AppImage https://github.com/niess/python-appimage/releases/download/python3.13/python3.13.9-cp313-cp313-manylinux2014_x86_64.AppImage
chmod +x python.AppImage

./python.AppImage --appimage-extract
mv squashfs-root SoftwareManager.AppDir

echo "Build SoftwareManager.whl"
cd ..
build/SoftwareManager.AppDir/AppRun -m build

echo "Prepare SoftwareManager AppImage"
cd build/SoftwareManager.AppDir
./AppRun -m pip install -r ../../requirements.txt
./AppRun -m pip install ../../dist/main-0.0.0-py3-none-any.whl

rm AppRun .DirIcon python.png python*.desktop usr/share/applications/python*.desktop

cp -t . ../../src/interface/assets/logo.png ../../SoftwareManager.desktop
cp ../../SoftwareManager.desktop usr/share/applications/

echo '#! /bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH=$HERE/usr/bin:$PATH;
export APPIMAGE_COMMAND=$(command -v -- "$ARGV0")
"$HERE/opt/python3.13/bin/python3.13" "-m" "main" "$@"' > AppRun

chmod -R 0755 ../SoftwareManager.AppDir
chmod +x AppRun

cp /usr/lib/x86_64-linux-gnu/libxcb-cursor.so* ../SoftwareManager.AppDir/usr/lib/
cp /usr/lib/x86_64-linux-gnu/libxcb-xinerama.so* ../SoftwareManager.AppDir/usr/lib/
cp /usr/lib/x86_64-linux-gnu/libxcb.so* ../SoftwareManager.AppDir/usr/lib/
cp /usr/lib/x86_64-linux-gnu/libgssapi_krb5.so* ../SoftwareManager.AppDir/usr/lib

echo " => Build SoftwareManager AppImage"
cd ..
./appimagetool-x86_64.AppImage --appimage-extract
squashfs-root/AppRun SoftwareManager.AppDir

echo " => Done "
