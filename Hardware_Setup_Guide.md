# Hardware Setup Guide: Smart Pothole Detection

Don't worry if you haven't worked with hardware before! Follow these simple steps to connect everything and get it running.

## 1. Wiring the Ultrasonic Sensor (HC-SR04) to the ESP32
You will need your ESP32 board, the HC-SR04 sensor, and 4 jumper wires (female-to-female usually, depending on your ESP32 pins).

The HC-SR04 has 4 pins: `VCC`, `TRIG`, `ECHO`, and `GND`.
Connect them to the ESP32 like this:

| HC-SR04 Pin | Wire Goes To | ESP32 Pin | Note |
| :---: | :---: | :---: | :--- |
| **VCC** | ➡️ | **VIN** or **5V** | The sensor needs 5 Volts to work properly. Connect it to the 5V output on your ESP32 (sometimes labeled VIN). |
| **GND** | ➡️ | **GND** | Connect to any Ground pin on the ESP32. |
| **TRIG** | ➡️ | **D5** (GPIO 5) | This pin sends the sound wave. |
| **ECHO** | ➡️ | **D18** (GPIO 18) | This pin listens for the echo. *(Note: The ECHO pin outputs 5V. While the ESP32 is technically a 3.3V device, it can usually handle this, but for long-term use a simple voltage divider is recommended. For quick testing, direct connection is usually fine).* |

## 2. Setting Up the Arduino Code (`pathhole.ino`)
1. Open up the Arduino IDE.
2. Open the `pathhole.ino` file inside the `c:\projects\pathhole` folder.
3. At the very top of the code, find these two lines:
   ```cpp
   const char* ssid = "YOUR_WIFI_SSID";
   const char* password = "YOUR_WIFI_PASSWORD";
   ```
4. Change `"YOUR_WIFI_SSID"` to your actual Wi-Fi network name (keep the quotes).
5. Change `"YOUR_WIFI_PASSWORD"` to your actual Wi-Fi password (keep the quotes).
   *(Note: The ESP32 only connects to 2.4GHz Wi-Fi networks, not 5GHz ones!)*
6. Ensure your ESP32 is plugged into your computer via USB.
7. In the Arduino IDE, select your ESP32 board and the correct COM port.
8. Click **Upload** (the right-arrow button) to flash the code to the ESP32.

## 3. Testing the System
1. Keep the ESP32 plugged into the computer. Open the **Serial Monitor** in the Arduino IDE (the magnifying glass icon in the top right).
2. Set the baud rate in the bottom right corner of the Serial Monitor to **115200**.
3. You should see it reporting distances! 
   *(e.g., "Distance: 20.00 cm")*
4. Open your web browser and go to: **[http://127.0.0.1:5000](http://127.0.0.1:5000)** to see your dashboard!
5. **Simulate a Pothole:** The code expects a "normal" road distance of 20cm. Place your hand or an object about 20cm in front of the sensor. Then, quickly pull your hand away so the distance jumps to 30cm or more.
6. The Serial Monitor will say `>>> POTHOLE CONFIRMED <<<` and the dashboard on your screen will update within 5 seconds!
