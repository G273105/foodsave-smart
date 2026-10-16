// Copy into TFT_eSPI/User_Setups and select from User_Setup_Select.h.
// LCDWIKI E32R40T profile; confirm board match before enabling.
#define USER_SETUP_ID 4032
#define ST7796_DRIVER
#define TFT_MISO 12
#define TFT_MOSI 13
#define TFT_SCLK 14
#define TFT_CS 15
#define TFT_DC 2
#define TFT_RST -1
#define TFT_BL 27
#define TFT_BACKLIGHT_ON HIGH
#define TOUCH_CS 33
#define LOAD_GLCD
#define LOAD_FONT2
#define LOAD_FONT4
// Conservative initial rates; validate panel colours and rotation physically.
#define SPI_FREQUENCY 20000000
#define SPI_READ_FREQUENCY 10000000
#define SPI_TOUCH_FREQUENCY 2500000
