#!/usr/bin/env bash
# Builds dist/recallquest_v<version>_<arch>.deb (needs python3-venv and dpkg-deb)
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$PWD"
VENV="$ROOT/build/venv-linux"

[ -x "$VENV/bin/python" ] || python3 -m venv "$VENV"
"$VENV/bin/pip" install --quiet -r requirements-build.txt

VERSION="$("$VENV/bin/python" -c 'import recallquest; print(recallquest.__version__)')"
ARCH="$(dpkg --print-architecture)"
PACKAGE="recallquest_v${VERSION}_${ARCH}"
STAGE="$ROOT/build/deb/$PACKAGE"

"$VENV/bin/python" -m PyInstaller --noconfirm --clean --log-level WARN \
  --distpath build/pyi-linux/dist --workpath build/pyi-linux/work packaging/recallquest.spec

rm -rf "$STAGE"
mkdir -p "$STAGE/DEBIAN" "$STAGE/opt" "$STAGE/usr/bin" "$STAGE/usr/share/applications" \
         "$STAGE/usr/share/doc/recallquest" "$STAGE/usr/share/pixmaps"
cp -a build/pyi-linux/dist/recallquest "$STAGE/opt/recallquest"
find "$STAGE/opt/recallquest" -type d -exec chmod 755 {} +
find "$STAGE/opt/recallquest" -type f -exec chmod 644 {} +
find "$STAGE/opt/recallquest" -type f \( -name '*.so*' -o -name 'recallquest' \) -exec chmod 755 {} +

printf '#!/bin/sh\nexec /opt/recallquest/recallquest "$@"\n' > "$STAGE/usr/bin/recallquest"
chmod 755 "$STAGE/usr/bin/recallquest"
install -m 644 packaging/recallquest.desktop "$STAGE/usr/share/applications/recallquest.desktop"
install -m 644 assets/icon.png "$STAGE/usr/share/pixmaps/recallquest.png"
install -m 644 README.md BUGREPORT.md "$STAGE/usr/share/doc/recallquest/"
install -m 644 LICENSE "$STAGE/usr/share/doc/recallquest/copyright"

# The standard icon sizes, scaled from the master
SDL_VIDEODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1 "$VENV/bin/python" - "$STAGE" <<'PY'
import os, sys
import pygame
stage = sys.argv[1]
master = pygame.image.load("assets/icon.png")
for size in (16, 24, 32, 48, 64, 128, 256, 512):
    folder = f"{stage}/usr/share/icons/hicolor/{size}x{size}/apps"
    os.makedirs(folder, exist_ok=True)
    pygame.image.save(pygame.transform.smoothscale(master, (size, size)), f"{folder}/recallquest.png")
PY

SIZE="$(du -sk "$STAGE" | cut -f1)"
cat > "$STAGE/DEBIAN/control" <<CONTROL
Package: recallquest
Version: $VERSION
Section: games
Priority: optional
Architecture: $ARCH
Depends: libc6 (>= 2.36)
Recommends: libgl1, libasound2
Installed-Size: $SIZE
Maintainer: Shouku Games <info@shoukugames.org>
Homepage: https://shoukugames.org/
Description: Bilingual reading comprehension game for ages 10+ (English/Japanese)
 Read a randomly generated silly story before the 120-second timer runs out,
 then answer three questions by pointing at the right character, animal,
 object or place. Ten levels on three difficulties, with stories that grow
 longer and trickier. Every unused second scores 100 points. Includes a
 top 10 scoreboard, ambient music and a For Parents progress record.
CONTROL
cat > "$STAGE/DEBIAN/postinst" <<'SCRIPT'
#!/bin/sh
set -e
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -f /usr/share/icons/hicolor || true
fi
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications || true
fi
SCRIPT
cp "$STAGE/DEBIAN/postinst" "$STAGE/DEBIAN/postrm"
chmod 755 "$STAGE/DEBIAN/postinst" "$STAGE/DEBIAN/postrm"

mkdir -p dist
dpkg-deb --root-owner-group -Zxz --build "$STAGE" "dist/$PACKAGE.deb" >/dev/null

# Prove the packaged game really runs: unpack it and play a few seconds
CHECK="$ROOT/build/deb/check"
rm -rf "$CHECK"
dpkg-deb -x "dist/$PACKAGE.deb" "$CHECK"
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy RECALLQUEST_DATA="$CHECK/data" \
  "$CHECK/opt/recallquest/recallquest" --smoke-test "$CHECK/smoke.txt"
echo "Smoke test: $(cat "$CHECK/smoke.txt")"
echo "Built dist/$PACKAGE.deb ($(du -h "dist/$PACKAGE.deb" | cut -f1))"
