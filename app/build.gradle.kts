plugins {
    alias(libs.plugins.android.application)
}

android {
    namespace = "com.arbitrary.digalog"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.arbitrary.digalog"
        // WFF v1 requires Wear OS 4 (API 33). The original WFS build declared minSdk 30
        // but relied on a bundled runtime; a pure WFF package needs 33+.
        minSdk = 33
        targetSdk = 34
        // Published build was 10010002 / 1.0.2. Must stay higher to ship as an update.
        versionCode = 10010003
        versionName = "1.1.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }
}
