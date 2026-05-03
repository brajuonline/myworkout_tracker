[app]
# Title of your application
title = My Workout Tracker

# Package name
package.name = myworkouttracker

# Package domain
package.domain = org.basavaraju

# Source code directory
source.dir = .

# File types to include
source.include_exts = py,kv,json,png,jpg

# Application version
version = 0.1

# Application requirements (add any extra modules you use)
requirements = python3,kivy,requests,sqlite3,openssl

# Orientation
orientation = portrait

# Permissions (uncomment if needed)
android.permissions = INTERNET

# Entry point (default is main.py)
# entrypoint = main.py

# Supported Android architectures (plural form!)
android.archs = arm64-v8a, armeabi-v7a

# Target Android API
android.api = 33

# Minimum supported API
android.minapi = 21

android.bootstrap = sdl2


# NDK version (recommended by p4a)
android.ndk = 25b

# Icons and presplash
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/presplash.png

[buildozer]
# Log level
log_level = 2

# Build output directory
# build_dir = .buildozer
