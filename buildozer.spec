[app]
title = IRL Stream
package.name = irlstream
package.domain = com.emragehc

source.dir = .
source.include_exts = py

version = 1.0.0

requirements = python3,kivy,pillow,requests,pyjnius,android

permissions = CAMERA,RECORD_AUDIO,INTERNET,WAKE_LOCK

orientation = portrait

[buildozer]
log_level = 2
warn_on_root = 0

android.api = 31
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.arch = armeabi-v7a