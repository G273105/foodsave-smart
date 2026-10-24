#pragma once
// Safe defaults for missing fields; explicit private settings take precedence.
#ifndef MONITOR_WIFI_SSID
#define MONITOR_WIFI_SSID ""
#endif
#ifndef MONITOR_WIFI_PASSWORD
#define MONITOR_WIFI_PASSWORD ""
#endif
#ifndef MONITOR_API_URL
#define MONITOR_API_URL ""
#endif
#ifndef MONITOR_DEVICE_TOKEN
#define MONITOR_DEVICE_TOKEN ""
#endif
#ifndef MONITOR_DHT_PIN
#define MONITOR_DHT_PIN -1
#endif
#ifndef MONITOR_ALLOW_LOCAL_HTTP
#define MONITOR_ALLOW_LOCAL_HTTP false
#endif
#ifndef MONITOR_ROOT_CA
#define MONITOR_ROOT_CA ""
#endif
