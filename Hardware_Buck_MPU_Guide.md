# Hardware Guide: Buck Converter & MPU6050

This guide explains how to power your system safely using a Buck Converter and how to wire the MPU6050 accelerometer.

## 1. Setting up the Buck Converter (Power Supply)
A buck converter takes a higher voltage battery (like a 9V battery or a 12V pack) and safely steps it down to exactly 5V.

**⚠️ CRITICAL STEP: TUNE IT BEFORE CONNECTING! ⚠️**
Before you connect the buck converter to your ESP32 or sensors, you MUST tune it, or it could output 12V and instantly burn out your boards.

1. Connect your battery (e.g., 9V) to the **IN+** (Red/Positive) and **IN-** (Black/Negative) on the buck converter.
2. Get a multimeter, set it to measure DC Voltage.
3. Touch the multimeter probes to the **OUT+** and **OUT-** pads on the buck converter.
4. Take a tiny flathead screwdriver and slowly turn the small golden screw on the blue box (potentiometer) on the buck converter.
5. Watch the multimeter. Turn the screw until the screen reads exactly **5.0V** (or between 4.9V and 5.1V).
6. Once it says 5.0V, you are safe! Unhook the battery for now.

**Wiring the Power:**
*   Connect **OUT+** from the buck converter to the **5V / VBUS** pin on the ESP32.
*   Connect **OUT-** from the buck converter to the **GND** pin on the ESP32.
*   *Both your HC-SR04 and MPU6050 will also take their power from these 5V and GND pins.*

## 2. Wiring the MPU6050 Accelerometer
The MPU6050 detects motion and jolts (like hitting a pothole). It uses I2C communication, which requires two wires: SDA (Data) and SCL (Clock).

On the ESP32-S3 Mini, we will use **GPIO 8 for SDA** and **GPIO 9 for SCL**.

| MPU6050 Pin | Wire Goes To | ESP32-S3 Mini Pin |
| :---: | :---: | :---: |
| **VCC** | ➡️ | **5V / VBUS** (Same power as everything else) |
| **GND** | ➡️ | **GND** |
| **SDA** | ➡️ | **GPIO 8** |
| **SCL** | ➡️ | **GPIO 9** |

*(Leave the XDA, XCL, AD0, and INT pins disconnected, you don't need them).*

Once wired up, the code will automatically read the downward G-force (Z-axis) to detect if the car physically bounced in the pothole!
