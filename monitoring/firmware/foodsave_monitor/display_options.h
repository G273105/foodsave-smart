#pragma once
// Enable only AFTER matching TFT_eSPI setup to the exact board schematic.
#ifndef MONITOR_DISPLAY_ENABLED
#define MONITOR_DISPLAY_ENABLED 1
#endif
#ifndef MONITOR_TOUCH_CALIBRATED
#define MONITOR_TOUCH_CALIBRATED 0
#endif
#ifndef MONITOR_DISPLAY_ROTATION
#define MONITOR_DISPLAY_ROTATION 1
#endif
#ifndef MONITOR_TIMEZONE
#define MONITOR_TIMEZONE "GMT0BST,M3.5.0/1,M10.5.0"
#endif
// Replace with values from TFT_eSPI Touch_calibrate for this board/rotation.
#ifndef MONITOR_TOUCH_CALIBRATION
#define MONITOR_TOUCH_CALIBRATION {0, 0, 0, 0, 0}
#endif
