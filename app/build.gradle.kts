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
        targetSdk = 35
        // Published build was 10010002 / 1.0.2. Must stay higher to ship as an update.
        versionCode = 20000002
        versionName = "2.0.0"
    }

    // Upload key for Play. Set these in ~/.gradle/gradle.properties (never in the repo):
    // digalogUploadStoreFile, digalogUploadStorePassword, digalogUploadKeyAlias, digalogUploadKeyPassword
    val uploadStoreFile = providers.gradleProperty("digalogUploadStoreFile").orNull
    signingConfigs {
        if (uploadStoreFile != null) {
            create("upload") {
                storeFile = file(uploadStoreFile)
                storePassword = providers.gradleProperty("digalogUploadStorePassword").get()
                keyAlias = providers.gradleProperty("digalogUploadKeyAlias").get()
                keyPassword = providers.gradleProperty("digalogUploadKeyPassword").get()
            }
        }
    }

    buildTypes {
        release {
            // R8 strips the generated R classes so the bundle has no dex (Play rejects dex in watch faces).
            isMinifyEnabled = true
            if (uploadStoreFile != null) {
                signingConfig = signingConfigs.getByName("upload")
            }
        }
    }
}
