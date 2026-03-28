/*
 * Arduino Mega 2560 - Gimbal Motor Controller
 * Controls stepper motors (zoom/focus) and servos (pan/tilt)
 * Communicates with Raspberry Pi 5 via Serial (JSON protocol)
 */

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <AccelStepper.h>
#include <ArduinoJson.h>

// ============================================================================
// CONFIGURATION
// ============================================================================

// Stepper motor pins
#define SONY_ZOOM_STEP_PIN    22
#define SONY_ZOOM_DIR_PIN     23
#define SONY_FOCUS_STEP_PIN   24
#define SONY_FOCUS_DIR_PIN    25
#define PI_CAM_ZOOM_STEP_PIN  26
#define PI_CAM_ZOOM_DIR_PIN   27
#define PI_CAM_FOCUS_STEP_PIN 28
#define PI_CAM_FOCUS_DIR_PIN  29

// Servo driver
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(0x40);

// Servo channels
#define SERVO_SONY_PAN    0
#define SERVO_PI_CAM_PAN  1
#define SERVO_LED_PAN     2
#define SERVO_LED_TILT    3
#define SERVO_WIPER       4

// Servo pulse widths (microseconds)
#define SERVO_MIN 500
#define SERVO_MAX 2500
#define SERVO_FREQ 50  // Hz

// ============================================================================
// STEPPER MOTORS
// ============================================================================

AccelStepper sonyZoom(AccelStepper::DRIVER, SONY_ZOOM_STEP_PIN, SONY_ZOOM_DIR_PIN);
AccelStepper sonyFocus(AccelStepper::DRIVER, SONY_FOCUS_STEP_PIN, SONY_FOCUS_DIR_PIN);
AccelStepper piCamZoom(AccelStepper::DRIVER, PI_CAM_ZOOM_STEP_PIN, PI_CAM_ZOOM_DIR_PIN);
AccelStepper piCamFocus(AccelStepper::DRIVER, PI_CAM_FOCUS_STEP_PIN, PI_CAM_FOCUS_DIR_PIN);

// Motor positions
long sonyZoomPos = 0;
long sonyFocusPos = 0;
long piCamZoomPos = 0;
long piCamFocusPos = 0;

// ============================================================================
// SETUP
// ============================================================================

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  while (!Serial) {
    delay(10);
  }
  
  Serial.println(F("{\"status\":\"ok\",\"msg\":\"Arduino Gimbal Controller Starting\"}"));
  
  // Initialize I2C for PCA9685
  Wire.begin();
  
  // Initialize PCA9685
  pwm.begin();
  pwm.setPWMFreq(SERVO_FREQ);
  delay(10);
  
  // Initialize stepper motors
  sonyZoom.setMaxSpeed(1000);
  sonyZoom.setAcceleration(500);
  
  sonyFocus.setMaxSpeed(800);
  sonyFocus.setAcceleration(400);
  
  piCamZoom.setMaxSpeed(600);
  piCamZoom.setAcceleration(300);
  
  piCamFocus.setMaxSpeed(600);
  piCamFocus.setAcceleration(300);
  
  // Center all servos
  centerAllServos();
  
  Serial.println(F("{\"status\":\"ok\",\"msg\":\"Initialization complete\"}"));
}

// ============================================================================
// MAIN LOOP
// ============================================================================

void loop() {
  // Run stepper motors
  sonyZoom.run();
  sonyFocus.run();
  piCamZoom.run();
  piCamFocus.run();
  
  // Check for serial commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command.length() > 0) {
      processCommand(command);
    }
  }
}

// ============================================================================
// COMMAND PROCESSING
// ============================================================================

void processCommand(String jsonStr) {
  StaticJsonDocument<512> doc;
  DeserializationError error = deserializeJson(doc, jsonStr);
  
  if (error) {
    sendError("JSON parse error");
    return;
  }
  
  const char* cmd = doc["cmd"];
  
  if (strcmp(cmd, "SM") == 0) {  // Stepper Move
    handleStepperMove(doc);
  }
  else if (strcmp(cmd, "SS") == 0) {  // Stepper Stop
    handleStepperStop(doc);
  }
  else if (strcmp(cmd, "SV") == 0) {  // Servo Move
    handleServoMove(doc);
  }
  else if (strcmp(cmd, "GS") == 0) {  // Get Status
    handleGetStatus();
  }
  else if (strcmp(cmd, "SP") == 0) {  // Set Speed
    handleSetSpeed(doc);
  }
  else if (strcmp(cmd, "CAL") == 0) {  // Calibrate
    handleCalibrate(doc);
  }
  else {
    sendError("Unknown command");
  }
}

// ============================================================================
// STEPPER MOTOR CONTROL
// ============================================================================

void handleStepperMove(JsonDocument& doc) {
  const char* motor = doc["motor"];
  long position = doc["position"];
  
  if (strcmp(motor, "SONY_ZOOM") == 0) {
    sonyZoom.moveTo(position);
    sonyZoomPos = position;
  }
  else if (strcmp(motor, "SONY_FOCUS") == 0) {
    sonyFocus.moveTo(position);
    sonyFocusPos = position;
  }
  else if (strcmp(motor, "PI_CAM_ZOOM") == 0) {
    piCamZoom.moveTo(position);
    piCamZoomPos = position;
  }
  else if (strcmp(motor, "PI_CAM_FOCUS") == 0) {
    piCamFocus.moveTo(position);
    piCamFocusPos = position;
  }
  else {
    sendError("Unknown motor");
    return;
  }
  
  sendOK();
}

void handleStepperStop(JsonDocument& doc) {
  const char* motor = doc["motor"];
  
  if (strcmp(motor, "SONY_ZOOM") == 0) {
    sonyZoom.stop();
  }
  else if (strcmp(motor, "SONY_FOCUS") == 0) {
    sonyFocus.stop();
  }
  else if (strcmp(motor, "PI_CAM_ZOOM") == 0) {
    piCamZoom.stop();
  }
  else if (strcmp(motor, "PI_CAM_FOCUS") == 0) {
    piCamFocus.stop();
  }
  
  sendOK();
}

void handleSetSpeed(JsonDocument& doc) {
  const char* motor = doc["motor"];
  int speed = doc["speed"];
  
  if (strcmp(motor, "SONY_ZOOM") == 0) {
    sonyZoom.setMaxSpeed(speed);
  }
  else if (strcmp(motor, "SONY_FOCUS") == 0) {
    sonyFocus.setMaxSpeed(speed);
  }
  else if (strcmp(motor, "PI_CAM_ZOOM") == 0) {
    piCamZoom.setMaxSpeed(speed);
  }
  else if (strcmp(motor, "PI_CAM_FOCUS") == 0) {
    piCamFocus.setMaxSpeed(speed);
  }
  
  sendOK();
}

// ============================================================================
// SERVO CONTROL
// ============================================================================

void handleServoMove(JsonDocument& doc) {
  const char* servo = doc["servo"];
  float angle = doc["angle"];
  int pulse = doc["pulse"];
  
  int channel = -1;
  
  if (strcmp(servo, "SONY_PAN") == 0) {
    channel = SERVO_SONY_PAN;
  }
  else if (strcmp(servo, "PI_CAM_PAN") == 0) {
    channel = SERVO_PI_CAM_PAN;
  }
  else if (strcmp(servo, "LED_PAN") == 0) {
    channel = SERVO_LED_PAN;
  }
  else if (strcmp(servo, "LED_TILT") == 0) {
    channel = SERVO_LED_TILT;
  }
  else if (strcmp(servo, "WIPER") == 0) {
    channel = SERVO_WIPER;
  }
  
  if (channel >= 0) {
    setServoPulse(channel, pulse);
    sendOK();
  } else {
    sendError("Unknown servo");
  }
}

void setServoPulse(uint8_t channel, uint16_t pulseMicroseconds) {
  // Convert microseconds to PWM value for PCA9685
  // PCA9685 is 12-bit (4096 steps) at 50Hz
  // Each step is: (1000000 / 50Hz) / 4096 = 4.88 microseconds
  uint16_t pwmValue = (pulseMicroseconds * 4096) / (1000000 / SERVO_FREQ);
  pwm.setPWM(channel, 0, pwmValue);
}

void centerAllServos() {
  uint16_t centerPulse = (SERVO_MIN + SERVO_MAX) / 2;
  
  for (int i = 0; i <= 4; i++) {
    setServoPulse(i, centerPulse);
  }
}

// ============================================================================
// CALIBRATION
// ============================================================================

void handleCalibrate(JsonDocument& doc) {
  Serial.println(F("{\"status\":\"info\",\"msg\":\"Starting calibration\"}"));
  
  // Move all steppers to home position (0)
  sonyZoom.setCurrentPosition(0);
  sonyFocus.setCurrentPosition(0);
  piCamZoom.setCurrentPosition(0);
  piCamFocus.setCurrentPosition(0);
  
  sonyZoom.moveTo(0);
  sonyFocus.moveTo(0);
  piCamZoom.moveTo(0);
  piCamFocus.moveTo(0);
  
  // Wait for completion
  while (sonyZoom.isRunning() || sonyFocus.isRunning() || 
         piCamZoom.isRunning() || piCamFocus.isRunning()) {
    sonyZoom.run();
    sonyFocus.run();
    piCamZoom.run();
    piCamFocus.run();
  }
  
  // Center all servos
  centerAllServos();
  
  sendOK();
}

// ============================================================================
// STATUS REPORTING
// ============================================================================

void handleGetStatus() {
  StaticJsonDocument<512> doc;
  
  doc["status"] = "ok";
  doc["sony_zoom_pos"] = sonyZoom.currentPosition();
  doc["sony_focus_pos"] = sonyFocus.currentPosition();
  doc["pi_cam_zoom_pos"] = piCamZoom.currentPosition();
  doc["pi_cam_focus_pos"] = piCamFocus.currentPosition();
  doc["sony_zoom_running"] = sonyZoom.isRunning();
  doc["sony_focus_running"] = sonyFocus.isRunning();
  doc["pi_cam_zoom_running"] = piCamZoom.isRunning();
  doc["pi_cam_focus_running"] = piCamFocus.isRunning();
  
  String output;
  serializeJson(doc, output);
  Serial.println(output);
}

// ============================================================================
// UTILITIES
// ============================================================================

void sendOK() {
  Serial.println(F("{\"status\":\"ok\"}"));
}

void sendError(const char* msg) {
  Serial.print(F("{\"status\":\"error\",\"msg\":\""));
  Serial.print(msg);
  Serial.println(F("\"}"));
}
