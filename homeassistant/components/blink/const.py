"""Constants for Blink."""
DOMAIN = "blink"
DEVICE_ID = "Safegate Pro"

CONF_MIGRATE = "migrate"
CONF_CAMERA = "camera"
CONF_ALARM_CONTROL_PANEL = "alarm_control_panel"

DEFAULT_BRAND = "Blink"
DEFAULT_ATTRIBUTION = "Data provided by immedia-semi.com"
DEFAULT_SCAN_INTERVAL = 300
DEFAULT_OFFSET = 1
SIGNAL_UPDATE_BLINK = "blink_update"

TYPE_CAMERA_ARMED = "motion_enabled"
TYPE_MOTION_DETECTED = "motion_detected"
TYPE_TEMPERATURE = "temperature"
TYPE_BATTERY = "battery"
TYPE_WIFI_STRENGTH = "wifi_strength"

SERVICE_REFRESH = "blink_update"
SERVICE_TRIGGER = "trigger_camera"
SERVICE_SAVE_VIDEO = "save_video"
SERVICE_SEND_PIN = "send_pin"

PLATFORMS = ("alarm_control_panel", "binary_sensor", "camera", "sensor")
