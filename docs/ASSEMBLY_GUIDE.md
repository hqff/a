# Hướng Dẫn Lắp Ráp - Assembly Guide

## Multi-Camera Gimbal System

### ⚠️ Lưu Ý Trước Khi Bắt Đầu

- Đọc kỹ toàn bộ hướng dẫn trước khi lắp ráp
- Chuẩn bị đầy đủ công cụ và linh kiện
- Làm việc trong môi trường sạch sẽ, khô ráo
- Ngắt điện trước khi hàn hoặc kết nối
- Chụp ảnh mỗi bước để dễ troubleshoot sau này

---

## Công Cụ Cần Thiết

### Công Cụ Bắt Buộc
- [ ] Mỏ hàn 60W + thiếc hàn
- [ ] Tuốc nơ vít (Phillips + flathead)
- [ ] Kìm cắt dây
- [ ] Kìm tuốt dây điện
- [ ] Đồng hồ vạn năng (multimeter)
- [ ] Súng keo nóng
- [ ] Băng keo điện / heat shrink tubing

### Công Cụ Hữu Ích
- [ ] Máy in 3D (nếu tự làm parts)
- [ ] Máy khoan
- [ ] Bộ mũi khoan (2-10mm)
- [ ] Kẹp giữ mạch khi hàn
- [ ] Thước kẹp (caliper)

---

## Phần 1: Chuẩn Bị Nguồn Điện

### 1.1. Lắp Ráp Battery Pack (4S)

**Cảnh báo**: Pin Li-ion rất nguy hiểm nếu lắp sai!

```
Bước 1: Chuẩn bị cells
- Sử dụng 4 cells 18650 CÙNG LOẠI, CÙNG DUNG LƯỢNG
- Đo voltage từng cell (phải gần bằng nhau, chênh < 0.05V)
- Dán băng keo cách điện lên cực dương

Bước 2: Lắp vào battery holder
- Đặt cells theo đúng cực (+/-)
- Series connection: (+) cell 1 → (-) cell 2 → ... → (+) cell 4
- Voltage tổng = 14.8V (3.7V × 4)

Bước 3: Gắn BMS 4S
- Red wire (B+) → Positive của cell 4
- Black wire (B-) → Negative của cell 1
- Balance wires:
  * B1 → giữa cell 1 và cell 2
  * B2 → giữa cell 2 và cell 3
  * B3 → giữa cell 3 và cell 4
  * B4 → Positive của cell 4

Bước 4: Test
- Đo voltage output: phải là 14.4-16.8V
- Test balance charging
- Kiểm tra overcurrent protection (nối tắt 1s → phải tự ngắt)
```

### 1.2. Lắp Buck Converters

**Cần 5-6 buck converters**:

```
Buck 1: 14.8V → 5V 5A (cho Pi 5)
├─ Input: Battery output
├─ Output: USB-C PD cable tới Pi 5
└─ Settings: Set voltage chính xác 5.00V với multimeter

Buck 2: 14.8V → 12V 5A (cho Gimbal motors)
├─ Input: Battery output
├─ Output: SimpleBGC controller
└─ Settings: 12.00V

Buck 3: 14.8V → 12V 3A (cho LED)
├─ Input: Battery output
├─ Output: Relay module (cho Zifon T6C + IR LEDs)
└─ Settings: 12.00V

Buck 4: 14.8V → 5V 3A (cho USB Hub)
├─ Input: Battery output
├─ Output: Powered USB Hub
└─ Settings: 5.00V

Buck 5: 14.8V → 6V 2A (cho Servos)
├─ Input: Battery output
├─ Output: PCA9685 V+ pin
└─ Settings: 6.00V

Buck 6: 14.8V → 5V 1A (cho Display)
├─ Input: Battery output
├─ Output: 5" touchscreen power
└─ Settings: 5.00V
```

**Lắp đặt**:
1. Hàn dây input từ battery (sử dụng XT60 connectors)
2. Điều chỉnh voltage với trimpot trên buck
3. Đo lại bằng multimeter
4. Ghi nhãn từng buck
5. Lắp vào hộp, cố định bằng ốc hoặc keo nóng

---

## Phần 2: Lắp Ráp Camera Cluster

### 2.1. Hộp Bảo Vệ Camera

**Vật liệu**: Hộp nhựa ABS 20x15x10cm

```
Bước 1: Khoan lỗ cho cameras
┌─────────────────────────┐
│  [Brio]  [Sony]  [Brio] │  ← Front view
│                         │
│  [Sensor] [Pi]  [Brio]  │
│                         │
│  [Glass Protection]     │
└─────────────────────────┘

Vị trí khoan:
- Sony PJ670: Center, đường kính 70mm
- Pi HQ Camera: 40mm bên trái Sony
- 3x Logitech Brio: Đường kính 40mm mỗi cái
- Light sensors: 4x lỗ 10mm ở 4 góc

Bước 2: Lắp kính bảo vệ
- Cắt mica/acrylic trong suốt 3mm
- Dán gioăng cao su chống nước
- Cố định bằng ốc M3

Bước 3: Lắp cameras
- Sony: Mount trên pan servo
- Pi Cam: Mount trên pan servo riêng
- Webcams: Mount cố định (không pan)
```

### 2.2. Cơ Cấu Pan cho Sony và Pi Cam

```
Sony PJ670 Pan System:
┌──────────────┐
│  MG996R Servo│
│      │       │
│      ▼       │
│  Pan Bracket │
│      │       │
│      ▼       │
│  Sony Camera │
└──────────────┘

Lắp đặt:
1. Gắn servo vào bracket
2. Gắn camera lên servo horn
3. Cân bằng để servo không bị tải nặng
4. Test góc quay (-90° đến +90°)
```

### 2.3. Hệ Thống Zoom/Focus

**Cho Sony PJ670**:
```
Zoom Control:
┌─────────────┐      ┌──────────────┐
│ NEMA 11     │─────▶│ Flexible     │
│ Stepper     │      │ Coupling     │
└─────────────┘      └──────┬───────┘
                            │
                            ▼
                     ┌──────────────┐
                     │ Zoom Ring    │
                     │ của Camera   │
                     └──────────────┘

Focus Control: Tương tự

Lắp đặt:
1. 3D print hoặc gia công bracket cho stepper
2. Gắn stepper song song với camera body
3. Flexible coupling nối stepper shaft với zoom ring
4. Cố định chắc chắn, tránh rung
```

---

## Phần 3: Lắp Ráp Gimbal

### 3.1. Khung Gimbal

**Sử dụng**: Gimbal frame carbon fiber hoặc tự làm từ thanh nhôm 20x20mm

```
Cấu trúc 3 trục:

     YAW (Motor 3)
          │
          ▼
    ┌─────────┐
    │ Roll    │◄── ROLL (Motor 2)
    │  Arm    │
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │ Pitch   │◄── PITCH (Motor 1)
    │  Arm    │
    └────┬────┘
         │
         ▼
    Camera Cluster
```

**Lắp Motor**:
1. Gắn brushless motor 2208 vào mỗi trục
2. Đấu dây 3 phase (A, B, C) vào SimpleBGC
3. Cân bằng gimbal (rất quan trọng!)
4. Gắn IMU sensor lên camera platform

### 3.2. SimpleBGC Controller

**Kết nối**:
```
SimpleBGC Board:
├─ BAT+/BAT-  → 12V from Buck Converter
├─ PITCH Motor → Motor 1 (A, B, C)
├─ ROLL Motor  → Motor 2 (A, B, C)
├─ YAW Motor   → Motor 3 (A, B, C)
├─ IMU → Built-in hoặc external MPU6050
└─ UART → Level shifter → Pi 5 GPIO
```

**Cấu hình** (qua SimpleBGC GUI):
1. Kết nối SimpleBGC với PC qua USB
2. Mở SimpleBGC GUI software
3. Calibrate IMU sensor
4. Set motor power (thường 50-150)
5. Tune PID parameters
6. Test manual control
7. Enable stabilization

---

## Phần 4: Arduino & Motor Control

### 4.1. Arduino Mega 2560

**Kết nối**:
```
Arduino Mega:
├─ VIN → 12V from Buck
├─ GND → Common ground
├─ Serial1 (TX1/RX1) → Pi 5 UART (with level shifter!)
├─ I2C (SDA/SCL) → PCA9685
├─ Stepper pins:
│   ├─ Pin 22-23 → A4988 #1 (Sony Zoom)
│   ├─ Pin 24-25 → A4988 #2 (Sony Focus)
│   ├─ Pin 26-27 → A4988 #3 (Pi Cam Zoom)
│   └─ Pin 28-29 → A4988 #4 (Pi Cam Focus)
└─ Power → Share GND with all drivers
```

**Upload Code**:
1. Cài Arduino IDE
2. Install libraries: Adafruit_PWMServoDriver, AccelStepper, ArduinoJson
3. Mở `arduino/gimbal_controller/gimbal_controller.ino`
4. Chọn board: Arduino Mega 2560
5. Upload

### 4.2. Stepper Drivers (A4988)

**Mỗi driver A4988**:
```
A4988 Pinout:
├─ VMOT → 12V
├─ GND → Common GND
├─ VDD → 5V (from Arduino or separate LDO)
├─ STEP → Arduino pin
├─ DIR → Arduino pin
├─ 1A, 1B, 2A, 2B → Stepper motor coils
└─ MS1, MS2, MS3 → 5V (for 1/16 microstepping)
```

**Điều chỉnh Current**:
1. Đặt multimeter ở chế độ đo voltage
2. Đo giữa wiper của trimpot và GND
3. Công thức: Vref = Current × 8 × Rsense
4. Ví dụ: Motor 1A, Rsense = 0.1Ω → Vref = 0.4V
5. Xoay trimpot để đạt Vref mong muốn

### 4.3. PCA9685 Servo Driver

**Kết nối**:
```
PCA9685:
├─ VCC → 5V (logic)
├─ GND → Common GND
├─ SDA → Arduino SDA (Pin 20)
├─ SCL → Arduino SCL (Pin 21)
├─ V+ → 6V (servo power, từ Buck converter riêng)
├─ Channels:
│   ├─ 0 → Sony Pan Servo
│   ├─ 1 → Pi Cam Pan Servo
│   ├─ 2 → LED Pan Servo
│   ├─ 3 → LED Tilt Servo
│   └─ 4 → Wiper Servo
```

---

## Phần 5: Raspberry Pi 5 Setup

### 5.1. Hardware Assembly

**Lắp Pi 5**:
```
1. Gắn Pi 5 vào case/mounting plate
2. Lắp Active Cooler (quạt tản nhiệt)
3. Lắp NVMe Base + SSD 256GB
4. Kết nối:
   ├─ USB-C Power (5V 5A from Buck)
   ├─ USB Hub (powered)
   ├─ HDMI → 5" Touchscreen
   ├─ CSI ribbon → Pi HQ Camera
   ├─ GPIO → Sensors, relays, NRF24L01
   └─ USB Hub → 3x Webcams, 4G Dongle, Arduino
```

### 5.2. Wiring GPIO

**Tham khảo**: `docs/WIRING_DIAGRAMS.md`

**Quan trọng**:
- Sử dụng common ground cho tất cả
- Level shifter cho UART (5V Arduino ↔ 3.3V Pi)
- Đo voltage trước khi kết nối
- Màu dây: Đỏ=+, Đen=GND, Vàng=Signal

### 5.3. Software Installation

**Xem**: `install.sh`

```bash
# Clone repository
git clone https://github.com/yourusername/multi-camera-gimbal.git
cd multi-camera-gimbal

# Run installation
chmod +x install.sh
./install.sh

# Reboot
sudo reboot
```

---

## Phần 6: Lighting System

### 6.1. Zifon T6C LED

**Lắp đặt**:
```
1. Mount lên gimbal handle hoặc top của camera cluster
2. Gắn 2 servos (pan/tilt) nếu cần auto-adjustment
3. Power: 12V from Buck → Relay → LED
4. Control: Relay controlled by Pi GPIO 17
```

### 6.2. IR LED Array

**3x IR LED 5V 3W**:
```
Connection (parallel):
     5V ────┬──── LED 1 (+) ──── LED 1 (-) ────┬──── GND
            ├──── LED 2 (+) ──── LED 2 (-) ────┤
            └──── LED 3 (+) ──── LED 3 (-) ────┘

Power: 5V, 1.8A total
Control: Relay (Pi GPIO 27)
Position: Around Pi HQ Camera lens
```

---

## Phần 7: Sensors

### 7.1. Light Sensors (BH1750)

**Lắp 4 sensors**:
```
Positions:
├─ Front: 0x23 (ADDR → GND)
├─ Top: 0x5C (ADDR → VCC)
├─ Left: Trên I2C bus riêng nếu có
└─ Right: Trên I2C bus riêng nếu có

Wiring (mỗi sensor):
├─ VCC → 3.3V (Pi)
├─ GND → GND
├─ SDA → GPIO 2
└─ SCL → GPIO 3
```

**Test**:
```bash
i2cdetect -y 1
# Should see devices at 0x23 and 0x5C
```

---

## Phần 8: Wireless Transmission

### 8.1. NRF24L01+ PA LNA

**Lắp đặt**:
```
NRF24L01+ Pinout:
├─ VCC → 3.3V (with 10μF capacitor!)
├─ GND → GND
├─ CE → GPIO 8
├─ CSN → GPIO 7
├─ SCK → GPIO 11 (SPI)
├─ MOSI → GPIO 10 (SPI)
├─ MISO → GPIO 9 (SPI)
└─ IRQ → (not used)

Antenna: Gắn external 2.4GHz antenna
Position: Tránh gần motors và cables nguồn
```

### 8.2. 4G/5G USB Dongle

**Đơn giản**: Cắm vào USB Hub, configure qua NetworkManager

---

## Phần 9: Final Assembly

### 9.1. Tích Hợp Tất Cả

```
1. Gắn camera cluster lên gimbal pitch arm
2. Cân bằng gimbal (rất quan trọng!)
   - Gimbal phải cân bằng khi motor tắt
   - Điều chỉnh position cho đến khi balanced
3. Lắp Pi 5, Arduino, drivers vào gimbal handle
4. Đấu tất cả dây điện
5. Cable management (zip ties, cable sleeves)
6. Lắp battery vào handle
7. Lắp 5" display lên handle
```

### 9.2. Weight Distribution

**Cân bằng**:
- Camera cluster: Trung tâm
- Battery: Phía dưới (counterweight cho camera)
- Electronics: Spread evenly

---

## Phần 10: Testing

### 10.1. Pre-Power Test

**Checklist**:
- [ ] Tất cả kết nối chắc chắn
- [ ] Không có short circuit (đo với multimeter)
- [ ] Battery voltage đúng (14.8V)
- [ ] Buck converter outputs đúng voltage
- [ ] Gimbal cân bằng
- [ ] Motors quay tự do

### 10.2. Power On Test

```
Test Sequence:
1. Bật nguồn (không gắn cameras lúc đầu)
2. Check Pi 5 boot (LED nhấp nháy)
3. Check Arduino (Serial monitor)
4. Check SimpleBGC (motors should stabilize)
5. Nếu OK → Tắt, gắn cameras, bật lại
```

### 10.3. Calibration

**Gimbal**:
```
1. Vào SimpleBGC GUI
2. Auto PID tuning
3. Test stabilization
4. Fine-tune nếu cần
```

**Cameras**:
```
1. Test từng camera trong software
2. Adjust zoom/focus ranges
3. Calibrate light sensors
4. Test multi-view
```

---

## Troubleshooting Lắp Ráp

**Motor quá nóng**:
- Giảm current trên A4988
- Kiểm tra mechanical binding
- Thêm heatsink

**Gimbal rung**:
- Cân bằng lại
- Giảm PID I-term
- Kiểm tra IMU mounting

**Cameras không kết nối**:
- Kiểm tra USB hub power
- Test với `lsusb`, `v4l2-ctl`
- Thử từng camera riêng lẻ

---

## Phụ Lục: 3D Printed Parts

**Các parts nên in 3D**:
1. Camera mounts
2. Stepper motor brackets
3. Servo horns/brackets
4. Cable management clips
5. Gimbal arm extensions
6. Pi 5 case/mount

**Settings**: PLA, 20% infill, 0.2mm layer height

---

**Chúc bạn lắp ráp thành công!** 🎉

Nếu gặp vấn đề, tham khảo:
- `docs/WIRING_DIAGRAMS.md`
- `docs/USER_MANUAL.md`
- GitHub Issues
