import serial
import struct
import cv2
import pprint

img = cv2.imread("./images/kinoko.jpg", 0)
threshold = 150
ret, img_thresh = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)

vl = len(img_thresh)
hl = len(img_thresh[0])
char_n = int(hl / 8)
pad_n = 8 - (hl % 8)
if pad_n == 8 :
    pad_n = 0

ser = serial.Serial(
    port = '/dev/cu.usbserial-1420',
    baudrate=12000000, 
    parity=serial.PARITY_NONE
    )

# LED Display SD-LEDSIGN-RD
# https://www.amazon.co.jp/gp/product/B01AUPJXYI/ref=ppx_yo_dt_b_asin_title_o02_s00?ie=UTF8&psc=1

# 1: order number
# end: checksum
data1 = [0x01, 0x05, 0x01, 0x55, 0xAA, 0x5A, 0xA5]
data1.append(sum(data1)%256);

# 1: order number
# 3: speed & direction
# end: checksum
data2 = [0x02, 0x08, 0x21, 0x91, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
data2.append(sum(data2)%256);

# 1: order number
# 4: display character length
# end: checksum
data3 = [0x03, 0x10, 0x00, int(char_n), 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
data3.append(sum(data3)%256);

# 1: order number
# 2: led data length + 1
# 3: packet data counter.
# 4 ~ led data length: led image data per 8bits
#   (example
#     data   led pattern
#     0xFF = x x x x x x x x
#     0x00 = o o o o o o o o
#     0xA5 = x o x o o x o x
#   
# end: checksum

data4 = [0x04, int(vl * char_n), 0x00]
for line in img_thresh:
    bline = []
    for i in line:
        bline.append(int(i))

    for j in range(char_n):
        b = 0
        for i in range(8):
            if char_n == j and pad_n <= i:
                b += (2 ** (7 - i)) * 1
            else:
                b += (2 ** (7 - i)) * int(bline[i]/255)
        del bline[0:8]
        data4.append(int(b))

#data4 = [0x04, 0x11, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFE, 0x00, 0xFF, 0xFF]
data4.append(sum(data4)%256);

# 1: order number
# end: checksum
data5 = [0x05, 0x03, 0x10, 0x03, 0x00, 0x1b]
data5.append(sum(data5)%256);

ser.write(data1)
ser.write(data2)
ser.write(data3)
ser.write(data4)
ser.write(data5)

ser.close()
