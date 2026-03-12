# Hardware Guide: Adding a Buzzer

I have updated the Arduino code to remove the MPU6050 and replace it with a simple buzzer!

Now, whenever the ultrasonic sensor detects a pothole, the dashboard will still update, but the ESP32 will also immediately trigger a loud "BEEP" for half a second.

### Wiring the Buzzer
Most standard active buzzers have two pins: a longer pin (Positive/VCC) and a shorter pin (Negative/GND).

| Buzzer Pin | Wire Goes To | ESP32-S3 Mini Pin |
| :---: | :---: | :---: |
| **Long Pin / + / Red Wire** | ➡️ | **GPIO 4** |
| **Short Pin / - / Black Wire** | ➡️ | **GND** |

*(Note: Active buzzers will usually honk loudly when directly connected to 3.3V power, which is exactly why GPIO 4 will be able to turn it on and off directly!)*

1. Plug your ESP32-S3 Mini back into your computer and click **Upload** in the Arduino IDE to flash this new buzzer code.
2. Once flashed, unplug it and plug it back into your Power Bank.
3. Everything will connect exactly as before!
