# Hướng Dẫn Sử Dụng - User Manual

## Multi-Camera Gimbal System

### 📖 Mục Lục

1. [Giới Thiệu](#giới-thiệu)
2. [An Toàn](#an-toàn)
3. [Khởi Động Hệ Thống](#khởi-động-hệ-thống)
4. [Các Chế Độ Hoạt Động](#các-chế-độ-hoạt-động)
5. [Điều Khiển](#điều-khiển)
6. [Bảo Trì](#bảo-trì)
7. [Xử Lý Sự Cố](#xử-lý-sự-cố)

---

## Giới Thiệu

Hệ thống gimbal đa camera được thiết kế để:
- Quay video ổn định với nhiều góc nhìn
- Tự động điều chỉnh theo điều kiện ánh sáng
- Truyền tải video qua nhiều kênh
- Hoạt động trong điều kiện khắc nghiệt

### Thông Số Kỹ Thuật

- **Cameras**: 5 (Sony PJ670, Pi HQ, 3x Logitech Brio 100)
- **Gimbal**: 3 trục, brushless motors
- **Nguồn**: 14.8V Li-ion (4S), runtime ~1 giờ
- **Điều khiển**: Raspberry Pi 5 (8GB RAM)
- **Display**: 5" touchscreen 800x480
- **Trọng lượng**: ~2-3kg (tùy cấu hình)

---

## An Toàn

### ⚠️ CẢNH BÁO

1. **Nguồn Điện**
   - Luôn kiểm tra voltage battery trước khi sử dụng (14.8V ±0.5V)
   - Không để battery quá sạc (> 16.8V) hoặc quá xả (< 12.0V)
   - Ngắt nguồn khi không sử dụng

2. **Nhiệt Độ**
   - Raspberry Pi 5 có thể nóng (> 80°C)
   - Đảm bảo thông gió tốt
   - Hệ thống tự động tắt nếu quá nóng (> 85°C)

3. **Cơ Khí**
   - Motors có thể gây thương tích
   - Giữ tay xa khỏi phần chuyển động
   - Kiểm tra ốc vít trước mỗi lần sử dụng

4. **Điện Tử**
   - Không chạm vào mạch khi đang có điện
   - Tránh nước và độ ẩm cao
   - Sử dụng trong nhiệt độ 0-40°C

### Nút Emergency Stop

- **Vị trí**: GPIO 25 (hoặc phím ESC trên màn hình)
- **Chức năng**: Tắt ngay lập tức tất cả motors và dừng hệ thống
- **Khi nào dùng**: 
  - Có tiếng động bất thường
  - Gimbal mất cân bằng
  - Nhiệt độ quá cao
  - Bất kỳ tình huống nguy hiểm nào

---

## Khởi Động Hệ Thống

### Chuẩn Bị

1. **Kiểm tra trước khi bật**:
   - [ ] Battery đầy (> 14.0V)
   - [ ] Tất cả kết nối chắc chắn
   - [ ] Không có vật cản quanh gimbal
   - [ ] Cameras được lắp đúng
   - [ ] Thẻ SD/NVMe có dung lượng trống

2. **Bật nguồn**:
   ```
   1. Kết nối battery
   2. Bật công tắc nguồn chính
   3. Đợi Pi 5 boot (30-60 giây)
   4. Màn hình sẽ hiển thị khi ready
   ```

### Khởi Động Tự Động

Nếu đã cài đặt systemd service:
```bash
sudo systemctl start gimbal-system
```

Xem status:
```bash
sudo systemctl status gimbal-system
```

### Khởi Động Thủ Công

```bash
cd ~/multi-camera-gimbal
python3 src/main.py
```

### Quá Trình Khởi Động

```
[0-5s]   Pi 5 boot, load OS
[5-10s]  Initialize GPIO, I2C, SPI
[10-15s] Detect and initialize cameras
[15-20s] Initialize motors, calibrate gimbal
[20-25s] Initialize sensors and lighting
[25-30s] Start video processing
[30s+]   System ready - display shows video
```

---

## Các Chế Độ Hoạt Động

### 1. AUTO Mode (Mặc định)

**Đặc điểm**:
- Tự động điều chỉnh ISO dựa trên ánh sáng
- Tự động bật/tắt đèn LED
- Tự động bật IR LEDs trong tối
- Gimbal tự ổn định

**Khi nào dùng**: Hầu hết các tình huống quay phim thông thường

**Cách kích hoạt**: Nhấn phím `1` hoặc chọn trong menu

### 2. MANUAL Mode

**Đặc điểm**:
- Điều khiển thủ công tất cả thông số
- Điều chỉnh zoom, focus qua touchscreen
- Tắt auto-adjustment

**Khi nào dùng**: Khi cần kiểm soát hoàn toàn (studio, điều kiện ánh sáng ổn định)

**Cách kích hoạt**: Nhấn phím `2`

**Điều khiển**:
- Touch vào camera để chọn
- Slider để điều chỉnh zoom
- Buttons để điều chỉnh focus

### 3. NIGHT Mode

**Đặc điểm**:
- ISO cao (1600-3200)
- Bật IR LEDs
- Giảm noise
- Tối ưu cho quay đêm

**Khi nào dùng**: Quay trong điều kiện ánh sáng yếu hoặc ban đêm

**Cách kích hoạt**: Nhấn phím `3`

### 4. STREAMING Mode

**Đặc điểm**:
- Giảm resolution để tiết kiệm bandwidth
- Tối ưu encoding
- Ưu tiên latency thấp

**Khi nào dùng**: Live streaming qua 4G/5G hoặc WiFi

**Cách kích hoạt**: Menu → Streaming Mode

### 5. RECORDING Mode

**Đặc điểm**:
- Chất lượng cao nhất
- Bitrate cao
- Lưu file lớn

**Khi nào dùng**: Ghi hình chất lượng cao, chỉnh sửa sau

**Cách kích hoạt**: Menu → Recording Mode

---

## Điều Khiển

### Phím Tắt

| Phím | Chức Năng |
|------|-----------|
| `1` | AUTO mode |
| `2` | MANUAL mode |
| `3` | NIGHT mode |
| `M` | Toggle multi-view / single view |
| `O` | Toggle overlay (thông tin hiển thị) |
| `R` | Bắt đầu/dừng recording |
| `S` | Chụp ảnh |
| `ESC` | Emergency stop / Exit |

### Touchscreen

**Vùng chính (Main View)**:
- Tap để chọn camera làm primary
- Swipe lên/xuống: Điều chỉnh brightness
- Swipe trái/phải: Chuyển camera
- Pinch: Zoom in/out

**Vùng thumbnail**:
- Tap để chuyển camera đó thành primary

**Menu Button** (góc trên phải):
- Settings
- Mode selection
- System info
- Shutdown

### Gimbal Control

**Tự động**:
- Gimbal tự cân bằng dựa trên IMU
- Giữ camera luôn thẳng

**Thủ công** (MANUAL mode):
- Tilt: Touch và kéo lên/xuống
- Pan: Touch và kéo trái/phải
- Roll: Hai tay xoay

---

## Bảo Trì

### Hàng Ngày

- [ ] Lau sạch ống kính cameras
- [ ] Kiểm tra battery level
- [ ] Kiểm tra ốc vít lỏng
- [ ] Xóa file recording cũ nếu hết dung lượng

### Hàng Tuần

- [ ] Kiểm tra và lau chùi toàn bộ hệ thống
- [ ] Cân bằng gimbal lại nếu cần
- [ ] Backup dữ liệu quan trọng
- [ ] Kiểm tra nhiệt độ Pi 5 (thermal paste)

### Hàng Tháng

- [ ] Calibrate gimbal motors
- [ ] Calibrate light sensors
- [ ] Cập nhật firmware nếu có
- [ ] Kiểm tra tất cả kết nối điện
- [ ] Bảo dưỡng battery (charge/discharge cycle)

### Battery Care

**Sạc**:
- Sử dụng balance charger cho 4S
- Sạc ở 1C (5A cho 5000mAh)
- Không sạc quá đêm
- Sạc trong túi chống cháy

**Bảo quản**:
- Lưu ở 40-60% khi không dùng lâu
- Nhiệt độ 15-25°C
- Tránh va đập
- Kiểm tra voltage mỗi cell định kỳ

**Thay thế khi**:
- Voltage cell chênh lệch > 0.1V
- Phồng rộp
- Giảm dung lượng > 20%
- Quá 300 chu kỳ sạc/xả

---

## Xử Lý Sự Cố

### Camera Không Hoạt Động

**Sony PJ670**:
```
Vấn đề: Không nhận diện qua HDMI
Giải pháp:
1. Kiểm tra HDMI cable
2. Kiểm tra capture card (ls -l /dev/video*)
3. Reboot Pi 5
4. Kiểm tra nguồn camera
```

**Pi HQ Camera**:
```
Vấn đề: Không kết nối được
Giải pháp:
1. Kiểm tra ribbon cable CSI
2. Chạy: libcamera-hello
3. Kiểm tra trong raspi-config: Interface Options → Camera
4. Reboot
```

**Webcams**:
```
Vấn đề: USB webcam không nhận diện
Giải pháp:
1. lsusb để kiểm tra
2. Thử port USB khác
3. Kiểm tra nguồn USB hub
4. v4l2-ctl --list-devices
```

### Gimbal Issues

**Gimbal rung/không ổn định**:
1. Calibrate lại: Menu → Calibrate Gimbal
2. Kiểm tra cân bằng camera
3. Kiểm tra PID settings trong SimpleBGC
4. Kiểm tra IMU sensor

**Motors không quay**:
1. Kiểm tra nguồn 12V
2. Kiểm tra kết nối SimpleBGC
3. Enable motors: M command
4. Kiểm tra motor phases (A, B, C)

### Hệ Thống Quá Nóng

```
Lỗi: "CRITICAL: Temperature too high!"

Giải pháp ngay:
1. Nhấn Emergency Stop
2. Tắt nguồn
3. Để nguội 10-15 phút

Giải pháp lâu dài:
1. Kiểm tra quạt tản nhiệt Pi 5
2. Cải thiện thông gió
3. Giảm overclock (nếu có)
4. Thêm heatsink lớn hơn
```

### Battery Hết Nhanh

```
Nguyên nhân:
- Battery cũ/hỏng
- Quá nhiều thiết bị hoạt động
- LED brightness quá cao
- Gimbal motors làm việc liên tục

Giải pháp:
1. Kiểm tra battery health
2. Tắt thiết bị không cần thiết
3. Giảm LED brightness
4. Sử dụng battery dung lượng lớn hơn (7000mAh+)
5. Mang thêm battery dự phòng
```

### Mất Tín Hiệu RF

```
Lỗi: "RF connection lost"

Giải pháp:
1. Kiểm tra antenna NRF24L01
2. Giảm khoảng cách
3. Tránh vật cản kim loại
4. Kiểm tra nguồn RF module
5. Thử channel khác
6. Sử dụng LoRa module thay thế (longer range)
```

### Lỗi Software

**Python Errors**:
```bash
# Xem log
tail -f logs/gimbal_system.log

# Restart service
sudo systemctl restart gimbal-system

# Kiểm tra dependencies
pip3 list | grep opencv
pip3 list | grep picamera2
```

**Permission Errors**:
```bash
# Add user to groups
sudo usermod -a -G video,i2c,spi,gpio $USER
# Logout and login again
```

---

## Các Câu Hỏi Thường Gặp (FAQ)

**Q: Runtime bao lâu với 1 battery?**  
A: Khoảng 45-60 phút tùy thuộc vào mức sử dụng. Ghi hình nhiều + LED sáng = hết pin nhanh hơn.

**Q: Có thể dùng battery khác không?**  
A: Có, miễn là 4S Li-ion (14.8V) và đủ current (> 5A). Khuyến nghị 5000mAh+

**Q: Range của RF transmission là bao nhiêu?**  
A: NRF24L01+ PA+LNA: ~500-1000m line of sight. Thực tế ~200-300m.

**Q: Có thể thêm camera không?**  
A: Có thể thêm webcam USB nếu còn port. Pi HQ camera chỉ có thể 1-2 (CSI ports).

**Q: Quay được bao nhiêu camera cùng lúc?**  
A: Tất cả 5 cameras quay đồng thời. Display có thể show multi-view.

**Q: File recording lưu ở đâu?**  
A: Trong thư mục `recordings/` trên NVMe SSD.

**Q: Có thể stream lên YouTube/Facebook không?**  
A: Có, configure RTMP URL trong config.py

---

## Thông Tin Liên Hệ

- **GitHub Issues**: Report bugs
- **Documentation**: Xem trong thư mục `docs/`
- **Email**: your.email@example.com

---

**Phiên bản**: 1.0  
**Ngày cập nhật**: 2026-03-28
