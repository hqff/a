# Sơ Đồ Đấu Nối - Wiring Diagrams

## 🔌 TỔNG QUAN HỆ THỐNG ĐIỆN

```
┌─────────────────────────────────────────────────────────────────────┐
│                    POWER DISTRIBUTION SYSTEM                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────┐                                                    │
│  │  4S Li-ion   │  14.8V (16.8V fully charged)                      │
│  │  Battery     │  5000mAh+                                          │
│  │  (4x18650)   │                                                    │
│  └──────┬───────┘                                                    │
│         │                                                             │
│         ├──────────┬──────────┬──────────┬──────────┬──────────┐    │
│         │          │          │          │          │          │    │
│    ┌────▼────┐ ┌──▼───┐  ┌──▼───┐  ┌──▼───┐  ┌──▼───┐  ┌───▼───┐ │
│    │ 5V 5A   │ │ 12V  │  │ 12V  │  │ 5V   │  │ 3.3V │  │ Volt  │ │
│    │ Buck    │ │ Buck │  │ Buck │  │ Buck │  │ Buck │  │ Meter │ │
│    │ (Pi 5)  │ │(Gimb)│  │(LED) │  │(USB) │  │(Misc)│  │       │ │
│    └────┬────┘ └──┬───┘  └──┬───┘  └──┬───┘  └──┬───┘  └───────┘ │
│         │          │          │          │          │                │
│    ┌────▼────┐ ┌──▼───────┐ ┌▼────────┐┌▼──────┐ ┌▼──────┐        │
│    │   Pi 5  │ │ Gimbal   │ │ Zifon   ││ USB   │ │Sensor │        │
│    │  +NVMe  │ │ Motors   │ │ T6C LED ││ Hub   │ │Module │        │
│    └─────────┘ │ SimpleBGC│ │ 3x IR   │└───────┘ └───────┘        │
│                 └──────────┘ │ LED     │                            │
│                              └─────────┘                            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1️⃣ RASPBERRY PI 5 - MAIN CONNECTIONS

### 1.1 GPIO Pin Assignment

```
Raspberry Pi 5 GPIO (40-pin header)
┌─────┬──────┬──────────────────────────────────┬──────┬─────┐
│ 3V3 │  1   │  2  │ 5V (Power from Buck)         │      │     │
├─────┼──────┼─────┼──────────────────────────────┼──────┼─────┤
│ SDA │  3   │  4  │ 5V                           │ I2C  │     │
├─────┼──────┼─────┼──────────────────────────────┼──────┼─────┤
│ SCL │  5   │  6  │ GND                          │ I2C  │     │
├─────┼──────┼─────┼──────────────────────────────┼──────┼─────┤
│GPIO4│  7   │  8  │ GPIO14 (UART TX)             │      │     │
├─────┼──────┼─────┼──────────────────────────────┼──────┼─────┤
│ GND │  9   │ 10  │ GPIO15 (UART RX)             │      │     │
├─────┼──────┼─────┼──────────────────────────────┼──────┼─────┤
│GPIO17│ 11  │ 12  │ GPIO18 (PWM0)                │      │PWM  │
├─────┼──────┼─────┼──────────────────────────────┼──────┼─────┤
│GPIO27│ 13  │ 14  │ GND                          │      │     │
├─────┼──────┼─────┼──────────────────────────────┼──────┼─────┤
│GPIO22│ 15  │ 16  │ GPIO23                       │      │     │
├─────┼──────┼─────┼──────────────────────────────┼──────┼─────┤
│ 3V3 │ 17  │ 18  │ GPIO24                       │      │     │
├─────┼──────┼─────┼──────────────────────────────┼──────┼─────┤
│GPIO10│ 19  │ 20  │ GND                          │ SPI  │     │
├─────┼──────┼─────┼──────────────────────────────┼──────┼─────┤
│GPIO9 │ 21  │ 22  │ GPIO25                       │ SPI  │     │
├─────┼──────┼─────┼──────────────────────────────┼──────┼─────┤
│GPIO11│ 23  │ 24  │ GPIO8 (SPI CE0)              │ SPI  │     │
├─────┼──────┼─────┼──────────────────────────────┼──────┼─────┤
│ GND │ 25  │ 26  │ GPIO7 (SPI CE1)              │      │     │
└─────┴──────┴─────┴──────────────────────────────┴──────┴─────┘
... continues to pin 40
```

### 1.2 Pi 5 GPIO Allocation Table

| GPIO Pin | Function | Connected To | Purpose |
|----------|----------|--------------|---------|
| GPIO 2 (Pin 3) | I2C SDA | BH1750 Light Sensors | Light measurement |
| GPIO 3 (Pin 5) | I2C SCL | BH1750 Light Sensors | Light measurement |
| GPIO 14 (Pin 8) | UART TX | Arduino Mega | Motor control commands |
| GPIO 15 (Pin 10) | UART RX | Arduino Mega | Motor feedback |
| GPIO 17 (Pin 11) | Digital Out | Relay Module CH1 | Main LED control |
| GPIO 27 (Pin 13) | Digital Out | Relay Module CH2 | IR LED control |
| GPIO 22 (Pin 15) | Digital Out | Relay Module CH3 | Servo power |
| GPIO 23 (Pin 16) | Digital Out | SimpleBGC UART Enable | Gimbal enable |
| GPIO 24 (Pin 18) | Digital Out | Wiper Servo Signal | Rain wiper control |
| GPIO 10 (Pin 19) | SPI MOSI | NRF24L01 | RF transmission |
| GPIO 9 (Pin 21) | SPI MISO | NRF24L01 | RF transmission |
| GPIO 11 (Pin 23) | SPI SCLK | NRF24L01 | RF transmission |
| GPIO 8 (Pin 24) | SPI CE0 | NRF24L01 CE | RF chip enable |
| GPIO 7 (Pin 26) | SPI CE1 | NRF24L01 CSN | RF chip select |
| GPIO 25 (Pin 22) | Digital In | Emergency Stop Button | Safety |
| GPIO 4 (Pin 7) | Digital Out | Status LED | System status |

### 1.3 Pi 5 USB Connections

```
┌─────────────────────────────────────────┐
│         Raspberry Pi 5 USB Ports        │
├─────────────────────────────────────────┤
│                                         │
│  USB 3.0 Port 1 ──► 7-Port USB Hub     │
│                      │                   │
│                      ├─► Webcam 1 (Logitech Brio 100)
│                      ├─► Webcam 2 (Logitech Brio 100)
│                      ├─► Webcam 3 (Logitech Brio 100)
│                      ├─► 4G LTE Dongle
│                      └─► Arduino Mega (backup connection)
│                                         │
│  USB 3.0 Port 2 ──► Reserved for future│
│                                         │
│  USB-C Power ───► 5V 5A Power Supply   │
│                   (from Buck Converter) │
└─────────────────────────────────────────┘
```

### 1.4 Pi 5 CSI/DSI Connections

```
┌─────────────────────────────────────────┐
│    Raspberry Pi 5 Camera Interfaces     │
├─────────────────────────────────────────┤
│                                         │
│  CSI-0 (15-pin) ──► Pi HQ Camera Module│
│                     (via ribbon cable)  │
│                                         │
│  CSI-1 (15-pin) ──► Reserved/Unused    │
│                                         │
│  DSI (15-pin)   ──► 5" Touchscreen     │
│                     (800x480 HDMI alt.) │
└─────────────────────────────────────────┘
```

---

## 2️⃣ ARDUINO MEGA - MOTOR CONTROLLER HELPER

### 2.1 Arduino Mega Pin Assignment

```
┌────────────────────────────────────────────────────────────┐
│              ARDUINO MEGA 2560 CONNECTIONS                  │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  COMMUNICATION:                                             │
│  ├─ TX1 (Pin 18) ──► Pi 5 GPIO 15 (UART RX)               │
│  ├─ RX1 (Pin 19) ──► Pi 5 GPIO 14 (UART TX)               │
│  └─ GND ──────────► Pi 5 GND                               │
│                                                             │
│  STEPPER MOTORS (A4988 Drivers):                           │
│  ├─ Pin 22 ──► Stepper 1 STEP (Sony PJ670 Zoom)           │
│  ├─ Pin 23 ──► Stepper 1 DIR                              │
│  ├─ Pin 24 ──► Stepper 2 STEP (Sony PJ670 Focus)          │
│  ├─ Pin 25 ──► Stepper 2 DIR                              │
│  ├─ Pin 26 ──► Stepper 3 STEP (Pi Cam Zoom/Focus)         │
│  ├─ Pin 27 ──► Stepper 3 DIR                              │
│  ├─ Pin 28 ──► Stepper 4 STEP (Lens Aperture)             │
│  └─ Pin 29 ──► Stepper 4 DIR                              │
│                                                             │
│  SERVO MOTORS (via PCA9685 PWM Driver):                    │
│  ├─ SDA (Pin 20) ──► PCA9685 SDA (I2C)                    │
│  ├─ SCL (Pin 21) ──► PCA9685 SCL (I2C)                    │
│  └─ PCA9685 controls:                                       │
│      ├─ Channel 0: Sony PJ670 Pan Servo                   │
│      ├─ Channel 1: Pi HQ Cam Pan Servo                    │
│      ├─ Channel 2: Zifon LED Pan Servo                    │
│      ├─ Channel 3: Zifon LED Tilt Servo                   │
│      └─ Channel 4: Rain Wiper Servo                       │
│                                                             │
│  POWER:                                                     │
│  ├─ VIN ──► 12V from Buck Converter                       │
│  └─ GND ──► Common Ground                                  │
└────────────────────────────────────────────────────────────┘
```

### 2.2 A4988 Stepper Driver Wiring (x4)

```
┌─────────────────────────────────────────┐
│        A4988 Stepper Driver             │
├─────────────────────────────────────────┤
│                                         │
│  VMOT ──► 12V (from Buck Converter)    │
│  GND  ──► Common Ground                │
│  VDD  ──► 5V (from Arduino or LDO)     │
│  GND  ──► Common Ground                │
│                                         │
│  STEP ──► Arduino Pin (22,24,26,28)    │
│  DIR  ──► Arduino Pin (23,25,27,29)    │
│  EN   ──► GND (always enabled)         │
│                                         │
│  1A   ──► Stepper Motor Coil A+        │
│  1B   ──► Stepper Motor Coil A-        │
│  2A   ──► Stepper Motor Coil B+        │
│  2B   ──► Stepper Motor Coil B-        │
│                                         │
│  MS1  ──► 5V (1/16 microstepping)      │
│  MS2  ──► 5V                            │
│  MS3  ──► 5V                            │
│  RESET──► VDD (not used)               │
│  SLEEP──► VDD (not sleeping)           │
└─────────────────────────────────────────┘
```

### 2.3 PCA9685 PWM Servo Driver

```
┌─────────────────────────────────────────┐
│      PCA9685 16-Channel PWM Driver      │
├─────────────────────────────────────────┤
│                                         │
│  VCC ──► 5V (from Arduino)             │
│  GND ──► Common Ground                 │
│  SDA ──► Arduino SDA (Pin 20)          │
│  SCL ──► Arduino SCL (Pin 21)          │
│  OE  ──► GND (output always enabled)   │
│                                         │
│  V+  ──► 6V (separate servo power)     │
│                                         │
│  PWM Channels (0.5-2.5ms, 50Hz):       │
│  ├─ CH 0 ──► Sony Pan Servo            │
│  ├─ CH 1 ──► Pi Cam Pan Servo          │
│  ├─ CH 2 ──► LED Pan Servo             │
│  ├─ CH 3 ──► LED Tilt Servo            │
│  ├─ CH 4 ──► Wiper Servo               │
│  └─ CH 5-15 ──► Reserved               │
└─────────────────────────────────────────┘
```

---

## 3️⃣ SIMPLEBGC GIMBAL CONTROLLER

### 3.1 SimpleBGC 32-bit Connections

```
┌─────────────────────────────────────────────────────────┐
│          SimpleBGC 32-bit Gimbal Controller             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  POWER:                                                  │
│  ├─ BAT+ ──► 12V (from Buck Converter)                 │
│  └─ GND  ──► Common Ground                             │
│                                                          │
│  MOTORS (Brushless Gimbal Motors):                      │
│  ├─ PITCH Motor:                                        │
│  │   ├─ A ──► 2208 Motor Phase A                       │
│  │   ├─ B ──► 2208 Motor Phase B                       │
│  │   └─ C ──► 2208 Motor Phase C                       │
│  ├─ ROLL Motor:                                         │
│  │   ├─ A ──► 2208 Motor Phase A                       │
│  │   ├─ B ──► 2208 Motor Phase B                       │
│  │   └─ C ──► 2208 Motor Phase C                       │
│  └─ YAW Motor:                                          │
│      ├─ A ──► 2208 Motor Phase A                       │
│      ├─ B ──► 2208 Motor Phase B                       │
│      └─ C ──► 2208 Motor Phase C                       │
│                                                          │
│  IMU (MPU6050/MPU9250):                                 │
│  ├─ Built-in or external                               │
│  └─ Mounted on camera platform                         │
│                                                          │
│  SERIAL COMMUNICATION:                                   │
│  ├─ UART TX ──► Pi 5 GPIO (via level shifter)          │
│  ├─ UART RX ──► Pi 5 GPIO (via level shifter)          │
│  └─ GND ─────► Pi 5 GND                                │
│                                                          │
│  CONTROL:                                                │
│  ├─ RC_PITCH ──► PWM input (optional)                  │
│  ├─ RC_ROLL  ──► PWM input (optional)                  │
│  └─ RC_YAW   ──► PWM input (optional)                  │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Brushless Motor to SimpleBGC Wiring

```
Each 2208 Brushless Motor (80T):
┌──────────────┐
│   Motor      │
│   Phase A ───┼──► SimpleBGC Motor Port A
│   Phase B ───┼──► SimpleBGC Motor Port B
│   Phase C ───┼──► SimpleBGC Motor Port C
└──────────────┘

Mount Position:
- PITCH Motor: Controls camera tilt (up/down)
- ROLL Motor:  Controls camera roll (stabilization)
- YAW Motor:   Controls camera pan (left/right)
```

---

## 4️⃣ CAMERA CONNECTIONS

### 4.1 Sony PJ670 Camera

```
┌─────────────────────────────────────────┐
│         Sony PJ670 Handycam             │
├─────────────────────────────────────────┤
│                                         │
│  Power: Internal Battery (NP-FV70)     │
│                                         │
│  LANC/Remote Control:                  │
│  ├─ 2.5mm jack ──► Custom LANC adapter│
│  └─ LANC protocol via Arduino          │
│                                         │
│  Video Output:                          │
│  ├─ HDMI ──► HDMI Capture Card         │
│  └─ USB ──► Pi 5 USB Hub (control)     │
│                                         │
│  Mechanical Control:                    │
│  ├─ Zoom Rocker ──► Stepper Motor 1    │
│  ├─ Focus Ring ──► Stepper Motor 2     │
│  └─ Pan Mount  ──► Servo on PCA9685    │
└─────────────────────────────────────────┘
```

### 4.2 Raspberry Pi HQ Camera Module

```
┌─────────────────────────────────────────┐
│    Raspberry Pi HQ Camera Module        │
├─────────────────────────────────────────┤
│                                         │
│  CSI Ribbon Cable (15-pin):             │
│  └─► Pi 5 CSI-0 Port                   │
│                                         │
│  C/CS Mount Lens:                       │
│  ├─ 16mm Telephoto (C Mount), OR       │
│  ├─ 6mm Wide Angle (CS Mount), OR      │
│  ├─ 35mm Standard (C Mount), OR        │
│  └─ 8-50mm Zoom (C Mount)              │
│                                         │
│  Lens Control (for zoom lens):          │
│  ├─ Focus Ring ──► Stepper Motor 3     │
│  └─ Zoom Ring  ──► Stepper Motor 4     │
│                                         │
│  Pan Control:                           │
│  └─ Servo Motor on PCA9685 CH1         │
│                                         │
│  IR LEDs (3x 5V 3W):                   │
│  ├─ Connected in parallel              │
│  ├─ Power: 5V from relay-controlled    │
│  └─ Total: 9W @ 5V = 1.8A              │
└─────────────────────────────────────────┘
```

### 4.3 Logitech Brio 100 Webcams (x3)

```
┌─────────────────────────────────────────┐
│    Logitech Brio 100 Webcams (x3)       │
├─────────────────────────────────────────┤
│                                         │
│  Webcam 1 (Front):                      │
│  └─ USB 2.0 ──► Pi 5 USB Hub           │
│                                         │
│  Webcam 2 (Left):                       │
│  └─ USB 2.0 ──► Pi 5 USB Hub           │
│                                         │
│  Webcam 3 (Right):                      │
│  └─ USB 2.0 ──► Pi 5 USB Hub           │
│                                         │
│  Power: Bus-powered via USB             │
│  Resolution: 1080p @ 30fps              │
│  Fixed mounting (no pan/tilt)           │
└─────────────────────────────────────────┘
```

---

## 5️⃣ LIGHTING SYSTEM

### 5.1 Zifon T6C LED Videolight

```
┌─────────────────────────────────────────┐
│      Zifon T6C LED Videolight           │
├─────────────────────────────────────────┤
│                                         │
│  Power:                                 │
│  ├─ DC 12V input (from Buck)           │
│  └─ Relay controlled (Pi GPIO 17)      │
│                                         │
│  Brightness Control:                    │
│  ├─ PWM signal from Arduino            │
│  └─ 0-100% dimming                     │
│                                         │
│  Pan/Tilt Servos:                       │
│  ├─ Pan Servo  ──► PCA9685 CH2         │
│  └─ Tilt Servo ──► PCA9685 CH3         │
│                                         │
│  Mount: On top of camera cluster        │
└─────────────────────────────────────────┘
```

### 5.2 IR LED Array (3x 5V 3W)

```
┌─────────────────────────────────────────┐
│   IR LED Array for Pi HQ Camera         │
├─────────────────────────────────────────┤
│                                         │
│  3x IR LED (850nm/940nm):               │
│  ├─ Parallel connection                │
│  └─ Total: 9W @ 5V = 1.8A              │
│                                         │
│  Power Circuit:                         │
│  ┌──────────────────────────────┐      │
│  │ 5V ──► Relay CH2 ──► LED (+) │      │
│  │ GND ───────────────► LED (-) │      │
│  └──────────────────────────────┘      │
│                                         │
│  Relay Control: Pi GPIO 27              │
│  Mount: Around Pi HQ Camera lens        │
└─────────────────────────────────────────┘
```

---

## 6️⃣ SENSORS

### 6.1 BH1750 Light Sensors (x4-6)

```
┌─────────────────────────────────────────┐
│      BH1750 Light Sensors (I2C)         │
├─────────────────────────────────────────┤
│                                         │
│  All sensors on I2C bus (different addr)│
│                                         │
│  Sensor 1 (Front, addr 0x23):           │
│  ├─ VCC ──► 3.3V (Pi)                  │
│  ├─ GND ──► GND                        │
│  ├─ SDA ──► Pi GPIO 2 (I2C SDA)        │
│  ├─ SCL ──► Pi GPIO 3 (I2C SCL)        │
│  └─ ADDR ─► GND (addr 0x23)            │
│                                         │
│  Sensor 2 (Top, addr 0x5C):             │
│  ├─ ... (same as above)                │
│  └─ ADDR ─► VCC (addr 0x5C)            │
│                                         │
│  Sensor 3-4: Similar with addr select   │
│                                         │
│  Position: On camera cluster frame      │
│  Purpose: Measure ambient light         │
└─────────────────────────────────────────┘
```

---

## 7️⃣ DISPLAY & UI

### 7.1 5" Touchscreen Display

```
┌─────────────────────────────────────────┐
│    5" HDMI Touchscreen (800x480)        │
├─────────────────────────────────────────┤
│                                         │
│  Video:                                 │
│  └─ HDMI ──► Pi 5 HDMI Output          │
│                                         │
│  Touch:                                 │
│  └─ USB ──► Pi 5 USB Port              │
│                                         │
│  Power:                                 │
│  ├─ 5V ──► From Buck Converter         │
│  └─ ~500mA current draw                │
│                                         │
│  Mount: On gimbal handle                │
└─────────────────────────────────────────┘
```

---

## 8️⃣ WIRELESS TRANSMISSION

### 8.1 NRF24L01+ RF Module

```
┌─────────────────────────────────────────┐
│     NRF24L01+ PA LNA (2.4GHz)           │
├─────────────────────────────────────────┤
│                                         │
│  Transmitter (on Pi 5):                 │
│  ├─ VCC ──► 3.3V (with 10uF cap)       │
│  ├─ GND ──► GND                        │
│  ├─ CE  ──► GPIO 8  (SPI CE0)          │
│  ├─ CSN ──► GPIO 7  (SPI CE1)          │
│  ├─ SCK ──► GPIO 11 (SPI SCLK)         │
│  ├─ MOSI──► GPIO 10 (SPI MOSI)         │
│  └─ MISO──► GPIO 9  (SPI MISO)         │
│                                         │
│  Receiver (on remote display):          │
│  └─ Same pinout to separate MCU        │
│                                         │
│  Antenna: External 2.4GHz antenna       │
│  Range: Up to 1000m (line of sight)     │
└─────────────────────────────────────────┘
```

### 8.2 4G LTE USB Dongle

```
┌─────────────────────────────────────────┐
│        4G LTE USB Dongle                │
├─────────────────────────────────────────┤
│                                         │
│  Connection:                            │
│  └─ USB 3.0 ──► Pi 5 USB Hub           │
│                                         │
│  SIM Card: Data-only plan               │
│  Protocol: PPP / QMI                    │
│  Purpose: 4G/5G video streaming         │
│                                         │
│  Configuration via NetworkManager       │
└─────────────────────────────────────────┘
```

---

## 9️⃣ POWER SYSTEM DETAILED

### 9.1 Battery Pack Configuration

```
┌───────────────────────────────────────────────────────┐
│          4S Li-ion Battery Pack (14.8V Nominal)       │
├───────────────────────────────────────────────────────┤
│                                                        │
│  ┌────┐  ┌────┐  ┌────┐  ┌────┐                     │
│  │3.7V│──│3.7V│──│3.7V│──│3.7V│  Series Connection  │
│  │Cell│  │Cell│  │Cell│  │Cell│  Total: 14.8V       │
│  │ 1  │  │ 2  │  │ 3  │  │ 4  │  (16.8V fully chgd) │
│  └────┘  └────┘  └────┘  └────┘                     │
│     │      │      │      │                           │
│  ┌──┴──────┴──────┴──────┴───┐                       │
│  │   4S BMS Protection Board  │                       │
│  │  - Overcharge protection   │                       │
│  │  - Overdischarge protection│                       │
│  │  - Overcurrent protection  │                       │
│  │  - Cell balancing          │                       │
│  └────────────┬───────────────┘                       │
│               │                                        │
│            XT60 Connector ──► Main Power Distribution │
└───────────────────────────────────────────────────────┘

Capacity: 4x 3000mAh = 3000mAh @ 14.8V = 44.4Wh
Runtime calculation:
- Total power consumption: ~40-50W
- Runtime: 44.4Wh / 45W ≈ 1 hour
- Recommend: 2x battery packs for extended use
```

### 9.2 Buck Converter Distribution

```
┌────────────────────────────────────────────────────┐
│         Power Distribution from 14.8V Battery      │
├────────────────────────────────────────────────────┤
│                                                     │
│  Main Battery (14.8V)                              │
│         │                                           │
│         ├──► Buck 1 (5V 5A) ──► Raspberry Pi 5     │
│         │                       - Pi 5: 3A         │
│         │                       - NVMe SSD: 0.5A   │
│         │                       - Margin: 1.5A     │
│         │                                           │
│         ├──► Buck 2 (12V 5A) ──► Gimbal Motors     │
│         │                        SimpleBGC: 3-5A   │
│         │                                           │
│         ├──► Buck 3 (12V 3A) ──► LED Lights        │
│         │                        Zifon T6C: 2A     │
│         │                        IR LEDs: 1A       │
│         │                                           │
│         ├──► Buck 4 (5V 3A) ──► USB Hub + Webcams  │
│         │                        3x Webcam: 1.5A   │
│         │                        Hub: 0.5A         │
│         │                        Margin: 1A        │
│         │                                           │
│         ├──► Buck 5 (6V 2A) ──► Servo Motors       │
│         │                        Via PCA9685       │
│         │                                           │
│         └──► Buck 6 (5V 1A) ──► Touchscreen        │
│                                  Display: 0.5A     │
│                                  Margin: 0.5A      │
└────────────────────────────────────────────────────┘
```

---

## 🔟 COMPLETE SYSTEM WIRING DIAGRAM

```
┌──────────────────────────────────────────────────────────────────────┐
│                    COMPLETE GIMBAL SYSTEM WIRING                      │
└──────────────────────────────────────────────────────────────────────┘

                        ┌──────────────┐
                        │  4S Battery  │
                        │   14.8V      │
                        │   5000mAh    │
                        └──────┬───────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
   ┌────▼────┐            ┌───▼────┐            ┌───▼────┐
   │  Buck   │            │  Buck  │            │  Buck  │
   │  5V 5A  │            │ 12V 5A │            │ 12V 3A │
   └────┬────┘            └───┬────┘            └───┬────┘
        │                     │                      │
   ┌────▼──────────┐    ┌────▼──────┐         ┌─────▼─────┐
   │ Raspberry     │    │ SimpleBGC │         │  Zifon    │
   │ Pi 5          │    │ Gimbal    │         │  T6C LED  │
   │               │    │ Controller│         │  3x IR LED│
   │ GPIO ─────────┼───►│ UART      │         └───────────┘
   │ I2C  ─────────┼───►│           │
   │ SPI  ──────┐  │    │ Motors:   │
   │ UART ────┐ │  │    │ - Pitch   │
   │ USB Hub──┼─┼──┼──┐ │ - Roll    │
   │ CSI ───┐ │ │  │  │ │ - Yaw     │
   │ HDMI ─┐│ │ │  │  │ └───────────┘
   └───────┼┼─┼─┼──┘  │
           ││ │ │     │
           ││ │ │   ┌─▼──────────┐
           ││ │ │   │  Arduino   │
           ││ │ │   │  Mega      │
           ││ │ │   │            │
           ││ │ └──►│ UART ◄─────┤ Control stepper/servo
           ││ │     │ I2C  ──────┼─► PCA9685 ──► Servos
           ││ │     │ GPIO ──────┼─► A4988 ──► Steppers
           ││ │     └────────────┘
           ││ │
           ││ └────► NRF24L01 (RF Module)
           ││
           │└──────► BH1750 (Light Sensors x4)
           │
           └───────► 5" Touchscreen Display
                     
   ┌──────────────────────────────────────┐
   │       Camera Connections             │
   ├──────────────────────────────────────┤
   │                                      │
   │  Pi CSI ──► Pi HQ Camera Module     │
   │  USB 1  ──► Logitech Brio 100 (1)   │
   │  USB 2  ──► Logitech Brio 100 (2)   │
   │  USB 3  ──► Logitech Brio 100 (3)   │
   │  USB 4  ──► Sony PJ670 (control)    │
   │  HDMI   ──► Capture Card ──► USB    │
   │  USB 5  ──► 4G LTE Dongle           │
   └──────────────────────────────────────┘
```

---

## ⚠️ IMPORTANT NOTES

### Safety Precautions

1. **Always connect GND first** before connecting power lines
2. **Use proper gauge wire**:
   - Power (12V): 18-20 AWG
   - Signal (3.3V/5V): 22-24 AWG
3. **Add fuses** on battery output (10A recommended)
4. **Include capacitors** (100uF) near each power input
5. **Separate analog and digital grounds** if possible
6. **Use shielded cables** for motors to reduce EMI

### Testing Procedure

1. **Power test**: Connect power distribution only, measure voltages
2. **Pi 5 test**: Boot Pi 5, check GPIO outputs
3. **Motor test**: Test each motor individually
4. **Camera test**: Test each camera feed
5. **Integration test**: Combine all systems slowly
6. **Field test**: Test in actual use conditions

### Troubleshooting

- **No power**: Check fuses, BMS protection, battery voltage
- **Motors jerky**: Check power supply capacity, add capacitors
- **Camera not detected**: Check USB hub power, try different ports
- **RF not working**: Check antenna connection, power supply noise
- **Pi 5 crashes**: Insufficient power supply, add bigger capacitor

### Wire Color Standards (Suggested)

- **Red**: Positive power (Vcc, +12V, +5V, +3.3V)
- **Black**: Ground (GND, 0V)
- **Yellow**: Signal/Data
- **Green**: Signal/Data (differential pair)
- **Blue**: Signal/Data
- **White**: Signal/Data
- **Orange**: PWM/Servo signals
- **Brown**: I2C/Serial communication

---

## 📐 Physical Layout Suggestion

```
┌─────────────────────────────────────────────────────┐
│                   TOP VIEW                          │
│                                                     │
│              [Zifon T6C LED]                        │
│                     ▲                               │
│         ┌───────────┼───────────┐                   │
│         │   Camera Cluster Box  │                   │
│         │  ┌────┐  ┌────┐       │                   │
│         │  │Brio│  │Sony│       │                   │
│         │  │ 1  │  │PJ70│       │                   │
│         │  └────┘  └────┘       │                   │
│         │  ┌────┐  ┌────┐       │                   │
│         │  │Pi  │  │Brio│       │                   │
│         │  │Cam │  │ 2  │       │                   │
│         │  └────┘  └────┘       │                   │
│         │          ┌────┐       │                   │
│         │  [Light] │Brio│       │                   │
│         │  [Sensor]│ 3  │       │                   │
│         │          └────┘       │                   │
│         │  [Glass Protection]   │                   │
│         └───────────────────────┘                   │
│                     │                               │
│            ┌────────▼────────┐                       │
│            │  Gimbal Frame   │                       │
│            │  (3-axis)       │                       │
│            └────────┬────────┘                       │
│                     │                               │
│            ┌────────▼────────┐                       │
│            │   Gimbal Handle │                       │
│            │ [5" Touchscreen]│                       │
│            │                 │                       │
│            │  ┌───────────┐  │                       │
│            │  │ Pi 5      │  │                       │
│            │  │ Arduino   │  │                       │
│            │  │ Battery   │  │                       │
│            │  │ Buck Conv │  │                       │
│            │  └───────────┘  │                       │
│            └─────────────────┘                       │
└─────────────────────────────────────────────────────┘
```

---

## 📦 Recommended Wire Lengths

| Connection | Length | Type |
|------------|--------|------|
| Battery to Buck Converters | 15cm | 18 AWG |
| Buck to Pi 5 | 20cm | 20 AWG |
| Buck to SimpleBGC | 30cm | 18 AWG |
| Pi GPIO to Arduino | 25cm | 24 AWG ribbon |
| Camera CSI ribbon | 30cm | Official Pi ribbon |
| USB extensions | 50cm | USB 3.0 cables |
| Stepper motor wires | 40cm | 22 AWG (4-wire) |
| Servo wires | 35cm | 22 AWG (3-wire) |
| I2C sensor bus | 20cm | 24 AWG twisted pair |
| NRF24L01 antenna cable | 15cm | Coax with SMA |

---

End of Wiring Diagrams Document
