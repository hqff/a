# Multi-Camera Gimbal System

Hệ thống gimbal đa camera tự động hoàn toàn, điều khiển bởi Raspberry Pi 5, tích hợp nhiều loại camera, đèn chiếu sáng thông minh, và khả năng truyền tải video đa phương thức.

## 🎯 Tính Năng Chính

- **Multi-Camera System**: 5 cameras (Sony PJ670, Pi HQ Cam, 3x Logitech Brio 100)
- **3-Axis Gimbal**: Brushless motors với SimpleBGC controller
- **Auto-Adjustment**: Tự động điều chỉnh ISO, zoom, focus, lighting dựa trên môi trường
- **Smart Lighting**: LED chính (Zifon T6C) + IR LEDs với điều chỉnh tự động
- **Frequency Hopping**: Chống nhiễu sóng RF thông minh
- **Multi-View Display**: Hiển thị nhiều camera trên màn hình cảm ứng 5"
- **Multiple Output**: HDMI, RF, Bluetooth, 4G/5G streaming

## 📋 Yêu Cầu Phần Cứng

Xem chi tiết trong [`docs/PARTS_LIST_VIETNAM.md`](docs/PARTS_LIST_VIETNAM.md)

### Thành Phần Chính:
- Raspberry Pi 5 (8GB RAM recommended)
- SSD NVMe 256GB
- Sony PJ670 Handycam
- Raspberry Pi HQ Camera Module
- 3x Logitech Brio 100 Webcam
- SimpleBGC 32-bit Gimbal Controller
- Arduino Mega 2560
- 4S Li-ion Battery Pack (14.8V)
- Và nhiều linh kiện khác...

**Chi phí dự kiến**: 42-64 triệu VNĐ

## 🔧 Cài Đặt

### 1. Chuẩn Bị Raspberry Pi 5

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-opencv python3-numpy
sudo apt install -y python3-serial python3-smbus python3-rpi.gpio
sudo apt install -y ffmpeg v4l-utils

# Install picamera2
sudo apt install -y python3-picamera2
```

### 2. Clone Repository

```bash
cd ~
git clone https://github.com/yourusername/multi-camera-gimbal.git
cd multi-camera-gimbal
```

### 3. Cài Đặt Python Dependencies

```bash
pip3 install -r requirements.txt
```

### 4. Cấu Hình Phần Cứng

Xem hướng dẫn chi tiết tại:
- [`docs/WIRING_DIAGRAMS.md`](docs/WIRING_DIAGRAMS.md) - Sơ đồ đấu nối
- [`docs/ASSEMBLY_GUIDE.md`](docs/ASSEMBLY_GUIDE.md) - Hướng dẫn lắp ráp (sẽ được tạo)

### 5. Cấu Hình Hệ Thống

Chỉnh sửa `src/config.py` để điều chỉnh các thông số:
- Camera settings
- Motor calibration
- Network configuration
- GPIO pin assignments

## 🚀 Sử Dụng

### Khởi Động Hệ Thống

```bash
cd ~/multi-camera-gimbal
python3 src/main.py
```

### Các Chế Độ Hoạt Động

1. **AUTO Mode** (Mặc định): Tự động điều chỉnh tất cả
2. **MANUAL Mode**: Điều khiển thủ công qua touchscreen
3. **NIGHT Mode**: Tối ưu cho quay đêm (IR LEDs, high ISO)
4. **STREAMING Mode**: Tối ưu cho streaming
5. **RECORDING Mode**: Chất lượng cao nhất

### Phím Tắt

- `M`: Toggle multi-view / single view
- `O`: Toggle overlay information
- `1`: Chuyển sang AUTO mode
- `2`: Chuyển sang MANUAL mode
- `3`: Chuyển sang NIGHT mode
- `ESC`: Thoát / Emergency stop

## 📁 Cấu Trúc Dự Án

```
multi-camera-gimbal/
├── docs/                      # Tài liệu
│   ├── PARTS_LIST_VIETNAM.md  # Danh sách vật liệu VN
│   ├── WIRING_DIAGRAMS.md     # Sơ đồ đấu nối
│   └── ASSEMBLY_GUIDE.md      # Hướng dẫn lắp ráp
├── diagrams/                  # Sơ đồ và flowcharts
├── src/                       # Source code
│   ├── main.py               # Main controller
│   ├── config.py             # Configuration
│   ├── camera_controller/    # Camera modules
│   ├── motor_controller/     # Motor control
│   ├── lighting/             # LED control
│   ├── video_processing/     # Video processing
│   ├── ui/                   # Display & UI
│   ├── transmission/         # RF/network streaming
│   └── utils/                # Utilities
├── tests/                    # Unit tests
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🔌 Sơ Đồ Kết Nối

Xem chi tiết tại [`docs/WIRING_DIAGRAMS.md`](docs/WIRING_DIAGRAMS.md)

### Tổng Quan Hệ Thống

```
Battery (14.8V 4S)
    │
    ├─► Buck Converters (5V, 12V)
    │       │
    │       ├─► Raspberry Pi 5
    │       ├─► SimpleBGC Gimbal
    │       ├─► Arduino Mega
    │       └─► LED Lights
    │
    └─► Cameras
            ├─► Sony PJ670 (HDMI capture)
            ├─► Pi HQ Cam (CSI)
            └─► 3x Webcams (USB)
```

## 🛠️ Troubleshooting

### Camera không được nhận diện
```bash
# Check USB devices
lsusb

# Check video devices
ls -l /dev/video*

# Test camera
v4l2-ctl --list-devices
```

### Pi 5 quá nóng
- Kiểm tra tản nhiệt đã lắp đúng chưa
- Giảm clock speed nếu cần
- Đảm bảo thông gió tốt

### Motors không hoạt động
- Kiểm tra kết nối serial với Arduino
- Kiểm tra nguồn điện cho motors
- Xem log file trong `logs/`

### RF transmission lỗi
- Kiểm tra antenna NRF24L01
- Kiểm tra kết nối SPI
- Test với distance ngắn hơn

## 📊 Hiệu Năng

- **Frame Rate**: 30 FPS từ mỗi camera
- **Processing Latency**: < 50ms
- **RF Range**: Tối đa 1000m (line of sight)
- **Battery Life**: ~1 giờ (với 5000mAh 4S)
- **Gimbal Stabilization**: ±0.02° accuracy

## 🔒 An Toàn

⚠️ **QUAN TRỌNG**:
- Luôn giám sát nhiệt độ Pi 5
- Không để battery quá sạc/xả
- Tắt nguồn khi không sử dụng
- Kiểm tra kết nối trước khi bật nguồn
- Có nút Emergency Stop (GPIO 25)

## 📝 License

MIT License - Xem file LICENSE

## 👥 Đóng Góp

Contributions are welcome! Please:
1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📧 Liên Hệ

- GitHub Issues: [Report bugs hoặc feature requests](https://github.com/yourusername/multi-camera-gimbal/issues)
- Email: your.email@example.com

## 🙏 Credits

- SimpleBGC protocol documentation
- Raspberry Pi Foundation
- OpenCV community
- Python community

---

**Made with ❤️ for DIY Gimbal Enthusiasts**
