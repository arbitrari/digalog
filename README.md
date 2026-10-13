# Digalog — Wear OS watch face (Watch Face Format)

An analog face with the digital hour and minute printed on the hands, three complication
slots, and a choice of ten second-hand colors. Package: `com.arbitrary.digalog`.

This project was recovered from the published Play bundle (Watch Face Studio 1.5.7, v1.0.2,
versionCode 10010002). It is a **resource-only** Watch Face Format (WFF v1) app, with no Kotlin or Java code.

## Layout
- `app/src/main/res/raw/watchface.xml`: the whole face (WFF XML)
- `app/src/main/res/xml/watch_face_info.xml`: preview / editable flags
- `app/src/main/res/drawable-nodpi/`: hands, indices, previews
- `app/src/main/AndroidManifest.xml`: `hasCode=false`, `com.google.wear.watchface.format.version=1`

## Build
Requires JDK 17 and the Android SDK (API 35). Open the folder in Android Studio, or:

    ./gradlew assembleDebug        # app/build/outputs/apk/debug/app-debug.apk
    ./gradlew bundleRelease        # AAB for Play (sign with your upload key)

## Install
On a Wear OS 4+ emulator (Device Manager > Wear OS Large/Small Round, API 33+) or a watch with ADB debugging on:

    adb install -r app/build/outputs/apk/debug/app-debug.apk

Then long-press the current watch face, swipe to the end, tap **+**, and pick *Digalog*.
A debug build can't replace the Play-installed copy, because the signatures differ. Uninstall the Play version first.

## Validate
Use the validator from https://github.com/google/watchface (`third_party/wff`):

    ./gradlew :specification:validator:executable-jar
    java -jar wff-validator.jar 1 app/src/main/res/raw/watchface.xml

## Releasing
Bump `versionCode` (must stay above 10010002) and `versionName` in `app/build.gradle.kts`.
