[app]
title = Riqueza Babilônica
package.name = riqueza_babilonica
package.domain = org.seunome

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0
requirements = python3,kivy==2.2.1,sqlite3

[buildozer]
log_level = 2

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.arch = arm64-v8a