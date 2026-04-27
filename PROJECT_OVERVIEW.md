# Hệ Thống Gimbal Đa Camera Tự Chế - DIY Multi-Camera Gimbal System

## Tổng Quan Dự Án (Project Overview)

Hệ thống gimbal đa camera tự động hoàn toàn, điều khiển bởi Raspberry Pi 5, tích hợp nhiều loại camera, đèn chiếu sáng thông minh, và khả năng truyền tải video đa phương thức.

### Thành Phần Chính (Main Components)

#### 1. Camera Cluster (Cụm Camera)
- **Sony PJ670**: Camera chính, xoay độc lập theo chiều ngang
- **Raspberry Pi HQ Camera**: Camera phụ, xoay độc lập theo chiều ngang
- **3x Logitech Brio 100**: Camera quan sát toàn cảnh, gắn cố định
- **Protective Housing**: Hộp bảo vệ với kính chắn và gạt nước

#### 2. Lighting System (Hệ Thống Chiếu Sáng)
- **3x LED IR Raspberry Pi**: 5V 3W cho Raspberry Pi Camera
- **1x Zifon T6C LED Videolight**: Đèn chính, điều chỉnh hướng và độ sáng tự động

#### 3. Control System (Hệ Thống Điều Khiển)
- **Raspberry Pi 5**: 16GB RAM, 256GB storage, Ubuntu OS
- **Stepper Motors**: Điều khiển zoom, focus, pan cho cameras
- **Light Sensors**: Đo độ sáng môi trường
- **5" Touchscreen Display**: Giao diện điều khiển trên gimbal

#### 4. Transmission System (Hệ Thống Truyền Tải)
- **Wired**: HDMI/USB port output
- **Wireless**: RF, Bluetooth, 4G/5G
- **Anti-Jamming**: Frequency hopping khi bị phá sóng

### Tính Năng Chính (Key Features)

1. **Offline Image Processing**: Xử lý hình ảnh hoàn toàn offline trên Pi 5
2. **Auto Exposure Control**: Tự động điều chỉnh ISO, brightness dựa trên light sensors
3. **Auto Focus/Zoom**: Điều khiển chính xác qua stepper motors
4. **Multi-View UI**: Hiển thị tất cả camera feeds, chọn camera chính
5. **Frequency Hopping**: Chống nhiễu sóng thông minh
6. **Weather Protection**: Kính bảo vệ và gạt nước tự động

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GIMBAL SYSTEM                             │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌───────────────────────────────────────────────┐          │
│  │         CAMERA CLUSTER (Protected Housing)     │          │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐   │          │
│  │  │ Brio 100 │  │ Sony     │  │ Brio 100 │   │          │
│  │  │ (Fixed)  │  │ PJ670    │  │ (Fixed)  │   │          │
│  │  └──────────┘  │(Pan Ctrl)│  └──────────┘   │          │
│  │                 └──────────┘                  │          │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐   │          │
│  │  │Light     │  │Pi HQ Cam │  │ Brio 100 │   │          │
│  │  │Sensor    │  │(Pan Ctrl)│  │ (Fixed)  │   │          │
│  │  └──────────┘  └──────────┘  └──────────┘   │          │
│  │  [Glass Protection] [Rain Wiper]             │          │
│  └───────────────────────────────────────────────┘          │
│                         │                                     │
│  ┌─────────────────────▼───────────────────────┐            │
│  │         Raspberry Pi 5 Controller            │            │
│  │  - Ubuntu OS                                 │            │
│  │  - 16GB RAM, 256GB Storage                   │            │
│  │  - Multi-camera processing                   │            │
│  │  - Motor control                             │            │
│  │  - Video streaming                           │            │
│  │  - Frequency hopping                         │            │
│  └──────────────────────────────────────────────┘            │
│           │         │         │         │                     │
│  ┌────────▼──┐ ┌───▼────┐ ┌──▼─────┐ ┌▼──────────┐         │
│  │ Stepper  │ │ Gimbal │ │ Light  │ │ 5" Touch  │         │
│  │ Motors   │ │ Motors │ │ Control│ │ Display   │         │
│  └──────────┘ └────────┘ └────────┘ └───────────┘         │
│                                                               │
│  OUTPUT OPTIONS:                                             │
│  ┌──────┐ ┌────────┐ ┌────────┐ ┌──────────┐               │
│  │ HDMI │ │ RF/BT  │ │ 4G/5G  │ │ USB Port │               │
│  └──────┘ └────────┘ └────────┘ └──────────┘               │
└─────────────────────────────────────────────────────────────┘
```

## Cấu Trúc Thư Mục Dự Án (Project Structure)

```
multi-camera-gimbal/
├── docs/
│   ├── PARTS_LIST_VIETNAM.md          # Danh sách vật liệu thị trường VN
│   ├── WIRING_DIAGRAMS.md             # Sơ đồ đấu nối
│   ├── ASSEMBLY_GUIDE.md              # Hướng dẫn lắp ráp
│   └── USER_MANUAL.md                 # Hướng dẫn sử dụng
├── diagrams/
│   ├── system_architecture.svg        # Sơ đồ kiến trúc hệ thống
│   ├── wiring_schematic.svg           # Sơ đồ điện
│   ├── flowchart_main.svg             # Lưu đồ chính
│   └── mindmap.svg                    # Sơ đồ tư duy
├── src/
│   ├── main.py                        # Main controller
│   ├── config.py                      # Configuration
│   ├── camera_controller/
│   │   ├── __init__.py
│   │   ├── sony_pj670.py             # Sony camera control
│   │   ├── pi_hq_camera.py           # Pi HQ camera control
│   │   ├── webcam_controller.py      # Logitech webcam control
│   │   └── camera_manager.py         # Multi-camera manager
│   ├── motor_controller/
│   │   ├── __init__.py
│   │   ├── gimbal_motors.py          # Gimbal motor control
│   │   ├── stepper_motors.py         # Focus/zoom stepper control
│   │   └── servo_controller.py       # Pan/tilt servo control
│   ├── lighting/
│   │   ├── __init__.py
│   │   ├── led_controller.py         # LED light control
│   │   └── light_sensor.py           # Ambient light sensor
│   ├── video_processing/
│   │   ├── __init__.py
│   │   ├── multi_stream.py           # Multi-camera streaming
│   │   ├── video_encoder.py          # Video encoding
│   │   └── offline_processor.py      # Offline processing
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── display_manager.py        # 5" touchscreen UI
│   │   ├── camera_selector.py        # Camera selection UI
│   │   └── overlay_renderer.py       # Info overlay (ISO, zoom, etc)
│   ├── transmission/
│   │   ├── __init__.py
│   │   ├── hdmi_output.py            # HDMI output
│   │   ├── rf_transmitter.py         # RF transmission
│   │   ├── bluetooth_stream.py       # Bluetooth streaming
│   │   ├── cellular_stream.py        # 4G/5G streaming
│   │   └── frequency_hopper.py       # Anti-jamming frequency hopping
│   └── utils/
│       ├── __init__.py
│       ├── logger.py                 # Logging utility
│       └── helpers.py                # Helper functions
├── tests/
│   ├── test_cameras.py
│   ├── test_motors.py
│   └── test_transmission.py
├── requirements.txt                   # Python dependencies
├── install.sh                         # Installation script
└── README.md                          # Project README
```

## Workflow Chính (Main Workflow)

1. **Khởi động hệ thống** → Pi 5 boot Ubuntu
2. **Khởi tạo cameras** → Kết nối và configure tất cả cameras
3. **Khởi tạo motors** → Calibrate gimbal và stepper motors
4. **Đọc light sensors** → Đo độ sáng môi trường
5. **Auto-adjust** → Điều chỉnh ISO, zoom, focus, lighting
6. **Start streaming** → Bắt đầu capture và stream video
7. **Display UI** → Hiển thị multi-view trên touchscreen
8. **Monitor & Control** → Liên tục monitor và điều chỉnh
9. **Handle jamming** → Phát hiện và xử lý nhiễu sóng

## Các Chế Độ Hoạt Động (Operating Modes)

1. **Auto Mode**: Tự động điều chỉnh tất cả parameters
2. **Manual Mode**: Điều khiển thủ công qua touchscreen
3. **Night Mode**: Tối ưu cho quay đêm (IR LEDs, high ISO)
4. **Streaming Mode**: Tối ưu cho truyền tải video
5. **Recording Mode**: Tối ưu cho ghi hình chất lượng cao
