#pragma once
#include "trusted_roots.h"

// Copy to config.h locally. Never commit credentials.
#define MONITOR_WIFI_SSID ""
#define MONITOR_WIFI_PASSWORD ""
#define MONITOR_API_URL "https://foodsave-smart.onrender.com/api/temperatures"
#define MONITOR_DEVICE_TOKEN ""
// Confirm an available bidirectional GPIO from the exact board schematic.
// -1 deliberately prevents sensor access and transmission.
#define MONITOR_DHT_PIN -1
// Plain HTTP is permitted only for a trusted local demonstration network.
#define MONITOR_ALLOW_LOCAL_HTTP false
// Use a trusted CA certificate for HTTPS; never disable verification.
#define MONITOR_ROOT_CA MONITOR_PUBLIC_ROOTS
