from paddleocr import PaddleOCR

ocr = PaddleOCR(use_angle_cls=True, lang='en')  # good defaults
result = ocr.ocr('im.jpg', cls=True)

for line in result[0]:
    text = line[1][0]
    conf = line[1][1]
    print(text, conf)

