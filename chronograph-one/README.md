# Chronograph One for OnePlus Watch 4
- Wear OS Watch Face Format v1 APK built with Android Gradle Plugin 8.10.1.
- 9 configurable color palettes, analog hands, digital time, date, daily step count, battery %, heart-rate value.
- Weather and active calories require selecting a suitable Wear OS complication data provider. Do not assume OHealth provides one.
- Power saving: bitmap graphics hidden in ambient (AOD) mode, no second hand.
- The watch face must be installed on the WATCH through ADB debugging, not just downloaded to the phone. No Play Store distribution.
- Builds are unsigned for publication but debug APK is debug-signed by Android build tools (good for sideload).
- No guarantee of battery-life parity with stock OnePlus watch face, because OnePlus power optimizations may be proprietary.
