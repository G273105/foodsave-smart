#pragma once
#if MONITOR_DISPLAY_ENABLED
#include <TFT_eSPI.h>
TFT_eSPI screen;
enum class Page { Home, History, Connection };
Page page = Page::Home;
uint32_t lastPaint = 0;
bool touchHeld = false;
bool hasPainted = false;
Page paintedPage = Page::Home;
uint32_t lastGraphPaint = 0;
size_t graphNextSample = HISTORY_CAPACITY;
struct LabelCache { int x = -1, y = -1; String text; uint16_t colour = 0; int size = 0; };
LabelCache labels[24];
void clearLabelCache() { for (auto &item : labels) item.x = -1; }
constexpr uint16_t BG = 0x0863, PANEL = 0x10C5, INK = 0xFFFF, MUTED = 0xAD75, ACCENT = 0x4ED2;
String localTimeText(time_t t, bool date = false) {
  if (!t) return "Time not synchronised";
  struct tm parts;
  localtime_r(&t, &parts);
  char text[32];
  strftime(text, sizeof(text), date ? "%d/%m/%Y %H:%M:%S" : "%H:%M:%S", &parts);
  return String(text);
}
void label(int x, int y, const String &text, uint16_t colour = INK, int size = 2) {
  LabelCache *cached = nullptr;
  for (auto &item : labels) {
    if (item.x == x && item.y == y) { cached = &item; break; }
  }
  if (cached && cached->text == text && cached->colour == colour && cached->size == size) return;
  if (!cached) for (auto &item : labels) if (item.x < 0) { cached = &item; break; }
  // Compose the entire field off-screen, then transfer it without a visible erase.
  int width = screen.width() - x - 16;
  if (page == Page::History && y >= 100) {
    width = x == 3 ? 43 : (x == screen.width()-36 ? 20 : 180);
  }
  int height = 8 * size;
  TFT_eSprite field(&screen);
  field.setColorDepth(16);
  if (field.createSprite(width, height)) {
    field.fillSprite(BG);
    field.setTextColor(colour, BG);
    field.setTextSize(size);
    field.setCursor(0, 0);
    field.print(text);
    field.pushSprite(x, y);
    field.deleteSprite();
  } else {
    // Low-memory fallback clears only this field, never the whole page.
    screen.fillRect(x, y, width, height, BG);
    screen.setTextColor(colour, BG);
    screen.setTextSize(size);
    screen.setCursor(x, y);
    screen.print(text);
  }
  if (cached) { cached->x=x; cached->y=y; cached->text=text; cached->colour=colour; cached->size=size; }
}
void row(int y, const char *title, const String &value) {
  label(16, y, title, MUTED, 1);
  label(135, y, value, INK, 1);
}
void paintUi() {
  int w = screen.width(), h = screen.height();
  bool full = !hasPainted || paintedPage != page;
  if (full) {
    screen.fillScreen(BG);
    clearLabelCache();
    paintedPage = page;
    hasPainted = true;
  }
  label(16, 12, "FOODSAVE SMART", ACCENT);
  label(16, 38, localTimeText(clockTime(), true), MUTED, 1);
  if (page == Page::Home) {
    label(16, 66, "CURRENT TEMPERATURE", MUTED, 1);
    label(16, 88, isfinite(monitor.temperature) ? String(monitor.temperature, 1) + " C" : "-- C", ACCENT, 5);
    row(140, "Humidity", isfinite(monitor.humidity) ? String(monitor.humidity, 1) + " % RH" : "-- % RH");
    row(160, "Sensor (temp)", monitor.sensorStatus);
    row(180, "Wi-Fi", WiFi.status() == WL_CONNECTED ? "Connected" : "Disconnected");
    row(200, "Server", monitor.serverStatus);
    row(220, "Last accepted", monitor.acceptedOnce ? localTimeText(monitor.lastAcceptedAt) : "None");
  } else if (page == Page::Connection) {
    label(16, 65, "CONNECTION", ACCENT);
    row(102, "Device", DEVICE_ID);
    row(124, "Wi-Fi", WiFi.status() == WL_CONNECTED ? "Connected" : "Disconnected");
    row(146, "API result", monitor.serverStatus);
    row(168, "HTTP code", String(monitor.lastHttpCode));
    row(190, "Last accepted", monitor.acceptedOnce ? localTimeText(monitor.lastAcceptedAt) : "None");
    row(212, "Accepted age", monitor.acceptedOnce ? String((millis()-monitor.lastAcceptedMs)/1000) + " s" : "--");
    label(16, 238, "API acceptance; database storage not verified", MUTED, 1);
  } else {
    label(16, 65, "HISTORY - LAST 60 MIN", ACCENT);
    bool graphDirty = full || graphNextSample != monitor.nextSample ||
                      millis() - lastGraphPaint >= 30000UL;
    if (graphDirty) {
    lastGraphPaint = millis();
    graphNextSample = monitor.nextSample;
    screen.fillRect(0, 100, w, h-160, BG);
    for (auto &item : labels) if (item.y >= 100) item.x = -1;
    const int left=48, right=w-18, top=105, bottom=h-86;
    float low=0, high=10;
    for(size_t i=0;i<monitor.sampleCount;i++) {
      const Sample &v=monitor.history[i];
      if(v.valid && millis()-v.uptimeMs<=3600000UL) {low=fminf(low,floorf(v.temperature)-1); high=fmaxf(high,ceilf(v.temperature)+1);}
    }
    screen.drawRect(left,top,right-left+1,bottom-top+1,MUTED);
    label(3,top,String(high,0)+" C",MUTED,1);
    label(3,bottom-8,String(low,0)+" C",MUTED,1);
    label(left,bottom+8,"-60 min",MUTED,1);
    label(right-18,bottom+8,"Now",MUTED,1);
    bool previous=false; int px=0,py=0;
    size_t first=(monitor.nextSample+HISTORY_CAPACITY-monitor.sampleCount)%HISTORY_CAPACITY;
    for(size_t i=0;i<monitor.sampleCount;i++) {
      const Sample &v=monitor.history[(first+i)%HISTORY_CAPACITY];
      uint32_t age=millis()-v.uptimeMs;
      if(!v.valid || age>3600000UL) {previous=false;continue;}
      int x=right-(uint64_t(age)*(right-left)/3600000UL);
      int y=bottom-int((v.temperature-low)/(high-low)*(bottom-top));
      if(previous) screen.drawLine(px,py,x,y,ACCENT);
      screen.fillCircle(x,y,2,ACCENT);px=x;py=y;previous=true;
    }
    if(!monitor.sampleCount) label(left+12,top+28,"Waiting for sensor readings",MUTED,1);
    }
    label(16,h-54,"RAM only; sensor errors leave gaps",MUTED,1);
  }
  if (full) {
  const char *tabs[]={"Home","History","Connection"};
  for(int i=0;i<3;i++) {
    int x=i*w/3;
    screen.fillRect(x,h-34,w/3-2,34,int(page)==i?ACCENT:PANEL);
    screen.setTextColor(int(page)==i?BG:INK);screen.setTextSize(1);
    screen.setCursor(x+12,h-21);screen.print(tabs[i]);
  }
  }
}
void uiBegin() {
  screen.init();screen.setRotation(MONITOR_DISPLAY_ROTATION);
#ifdef TFT_BL
  pinMode(TFT_BL, OUTPUT);
  digitalWrite(TFT_BL, TFT_BACKLIGHT_ON);
#endif
#if defined(TOUCH_CS) && MONITOR_TOUCH_CALIBRATED
  uint16_t calibration[5]=MONITOR_TOUCH_CALIBRATION;
  screen.setTouch(calibration);
#endif
  paintUi();
  Serial.println("UI navigation: h=Home, g=History, c=Connection");
}
void uiTick() {
  bool dirty=false;
  if(Serial.available()) {
    char key=Serial.read();
    if(key=='h') {page=Page::Home;dirty=true;}
    if(key=='g') {page=Page::History;dirty=true;}
    if(key=='c') {page=Page::Connection;dirty=true;}
  }
#if defined(TOUCH_CS) && MONITOR_TOUCH_CALIBRATED
  uint16_t x,y;
  bool pressed=screen.getTouch(&x,&y);
  if(pressed && !touchHeld && y>=screen.height()-34 && x<screen.width()) {
    page=static_cast<Page>(min(2,int(x)*3/screen.width()));dirty=true;
  }
  touchHeld=pressed;
#endif
  if(dirty || millis()-lastPaint>=1000) {lastPaint=millis();paintUi();}
}
#else
void uiBegin() { Serial.println("Display disabled: board pinout pending."); }
void uiTick() {}
#endif
