from cv2 import cv2 as cv
import numpy as np
import sys
from threading import Thread

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

run = True

def filter_image(image, option='b'):
    if(len(image.shape) == 3):
        image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    if(option == 'b'):
        return cv.bilateralFilter(image, 9, 9, 75)
    elif(option == 'm'):
        return cv.medianBlur(image, 3)
    elif(option == 'b+m'):
        image = cv.medianBlur(image, 3)
        return cv.bilateralFilter(image, 15, 9, 75)
    else:
        raise ValueError('Unknown option filter!')
    
def correct_illumination(image, kernel_size=5):
    if kernel_size <= 2 or kernel_size % 2 == 0:
        raise ValueError('Invalid kernel size! Must be >= 3 and odd!')
    float_image = image.astype(np.float32)
    
    illumination = cv.GaussianBlur(float_image, (kernel_size, kernel_size), 0)
    illumination[illumination == 0] = 1
    corrected = float_image / illumination * np.mean(illumination)
    
    corrected = np.clip(corrected, 0, 255).astype(np.uint8)
    return corrected

def prepare_image(image, filter_option='m', illumination_kernel=5, bright_thresh=90):
    if(len(image.shape) == 3):
        image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    if(bright_thresh is not None):
        image = np.where(image > bright_thresh, 255, 0).astype(np.uint8)
    image = filter_image(image, option=filter_option)
    
    image = correct_illumination(image, kernel_size=illumination_kernel)
    image = cv.adaptiveThreshold(image, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 31, 10)

    
    kernel = np.ones((1,1), np.uint8)
    image = cv.dilate(image, kernel, iterations=1)
    image = cv.erode(image, kernel, iterations=1)
    return image

def invert_image(image):
    return (255-image)

def get_text_images(image, filter_option='b', img_threshold=50, line_threshold=20, upscaling_factor=1.0, illumination_kernel=5, bright_thresh=90):
    image = cv.resize(image, None, fx=upscaling_factor, fy=upscaling_factor, interpolation=cv.INTER_LANCZOS4)

    processed_image = prepare_image(image, filter_option=filter_option, illumination_kernel=illumination_kernel, bright_thresh=bright_thresh)
    showcase_image = processed_image.copy()
    showcase_image = invert_image(showcase_image)
    showcase_image = cv.cvtColor(showcase_image, cv.COLOR_GRAY2BGR)
    clear_image = showcase_image.copy()
    
    images = []
    bounding_rects = []
    _, contours, _ = cv.findContours(processed_image, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        x, y, w, h = cv.boundingRect(contour)
        if(w * h > img_threshold):
            bounding_rects.append([x, y, w, h])
    bounding_rects.sort(key=lambda b:b[1])
    
    #print(len(bounding_rects))

    if(len(bounding_rects) == 0):
        return _, _, showcase_image, _
    
    rows = []
    row = [bounding_rects[0]]
    for i in range(1, len(bounding_rects)):
        x, y, w, h = bounding_rects[i]
        _, prev_y, _, prev_h = row[-1]
        if(abs(y - prev_y) <= line_threshold) or (abs(y + h - prev_h - prev_y)) <= line_threshold:
            row.append(bounding_rects[i])
        else:
            rows.append(row)
            row = []
            row.append(bounding_rects[i])

    if row:
        rows.append(row)

    row_data = []
    for row in rows:
        x1 = min(row, key= lambda x: x[0])[0]
        x2 = max(row, key=lambda x: x[0])[0] + max(row, key=lambda x: x[0])[2]
        y1 = min(row, key=lambda x:x[1])[1]
        y2 = max(row, key=lambda x:x[1])[1] + max(row, key=lambda x:x[1])[3]
        cv.rectangle(showcase_image, (x1, y1), (x2, y2), (255, 0, 0), 2)
        row_data.append([x1, y1, x2, y2])
    return row_data, image, showcase_image, clear_image

def send_image(app, image):
    while(run):
        filter = app.filters_slider.value()
        if(filter == 1):
            filter = 'b'
        elif(filter == 2):
            filter = 'm'
        else:
            filter='b+m'
        
        image_thresh = app.text_thresh_slider.value()
        line_thresh = app.line_thresh_slider.value()
        upscaling_thresh = round(app.upscaling_slider.value() / 100, 2)
    
        illumination_val = app.illumination_slider.value()
        if(illumination_val % 2 == 0):
            illumination_val = illumination_val + 1
        
        brightness_val = app.brightness_slider.value()
        if(brightness_val < 2):
            brightness_val = None

        _, _, new_image, _ = get_text_images(image, filter_option=filter, img_threshold=image_thresh, line_threshold=line_thresh, upscaling_factor=upscaling_thresh, illumination_kernel=illumination_val, bright_thresh=brightness_val)
        new_image = cv.resize(new_image, (1024, 768))
        new_image = QImage(new_image, new_image.shape[1], new_image.shape[0], new_image.strides[0], QImage.Format_RGB888)
        app.image_label.setPixmap(QPixmap(new_image))

class main(object):
    def create(self, main_window):
        window_x = 1024
        window_y = 1024#768
        main_window.setObjectName('main_window')
        main_window.setWindowTitle('Image preprocessing')
        main_window.setFixedSize(window_x, window_y)

        self.central_widget = QWidget(main_window)
        self.central_widget.setObjectName("central_widget")
        self.central_widget.setStyleSheet("QWidget {background-color: #cfcfd1;}")
        self.central_widget.setFixedSize(window_x, window_y)
        
        self.image_frame = QFrame(self.central_widget)
        self.image_frame.setGeometry(QRect(0, 0, window_x, int(window_y * 2 / 3)))
        self.image_frame.setFrameShape(QFrame.StyledPanel)
        self.image_frame.setFrameShadow(QFrame.Raised)
        self.image_frame.setObjectName("image_frame")
        self.image_frame.setStyleSheet("QFrame {background-color:#cfcfd1;}")
        self.image_frame_layout = QVBoxLayout(self.image_frame)
        self.image_frame_layout.setObjectName("image_frame_layout")

        self.image = QHBoxLayout()
        self.image_label =  QLabel()
        self.image.addWidget(self.image_label)
        self.image_frame_layout.addLayout(self.image)

        self.options_frame = QFrame(self.central_widget)
        self.options_frame.setGeometry(QRect(0, int(window_y * 2 / 3), window_x, int(window_y * 1 / 3)))
        self.options_frame.setFrameShape(QFrame.StyledPanel)
        self.options_frame.setFrameShadow(QFrame.Raised)
        self.options_frame.setObjectName("options_frame")
        self.options_frame.setStyleSheet("QFrame {background-color:#cfcfd1;}")
        self.options_frame_layout = QVBoxLayout(self.options_frame)
        self.options_frame_layout.setObjectName("options_frame_layout")

        #Option 1: The filter
        self.filters = QHBoxLayout()
        self.filters.addWidget(QLabel("Filter options"))
        self.filters_slider = QSlider(Qt.Horizontal)
        self.filters_slider.setMinimum(1)
        self.filters_slider.setMaximum(3)
        self.filters_slider.setSingleStep(1)
        self.filters_slider.setTickInterval(1)
        self.filters_slider.setTickPosition(QSlider.TicksBelow)
        self.filters.addWidget(self.filters_slider)
        self.filters_value = QLabel('Bilateral')
        self.filters.addWidget(self.filters_value)
        self.options_frame_layout.addLayout(self.filters)
        self.filters_slider.valueChanged.connect(self.filters_label)
        
        #Option 2: The illumination values
        self.illumination = QHBoxLayout()
        self.illumination.addWidget(QLabel("Illumination kernel size"))
        self.illumination_slider = QSlider(Qt.Horizontal)
        self.illumination_slider.setMinimum(3)
        self.illumination_slider.setValue(5)
        self.illumination_slider.setMaximum(101)
        self.illumination_slider.setSingleStep(2)
        self.illumination_slider.setTickInterval(2)
        self.illumination_slider.setTickPosition(QSlider.TicksBelow)
        self.illumination.addWidget(self.illumination_slider)
        self.illumination_value = QLabel('5')
        self.illumination.addWidget(self.illumination_value)
        self.options_frame_layout.addLayout(self.illumination)
        self.illumination_slider.valueChanged.connect(self.illumination_label)

        # #Option 3: The brightness threshold
        self.brightness = QHBoxLayout()
        self.brightness.addWidget(QLabel("Brightness Threshold"))
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setMinimum(0)
        self.brightness_slider.setMaximum(230)
        self.brightness_slider.setValue(160)
        self.brightness_slider.setSingleStep(1)
        self.brightness_slider.setTickInterval(1)
        self.brightness_slider.setTickPosition(QSlider.TicksBelow)
        self.brightness.addWidget(self.brightness_slider)
        self.brightness_value = QLabel('80')
        self.brightness.addWidget(self.brightness_value)
        self.options_frame_layout.addLayout(self.brightness)
        self.brightness_slider.valueChanged.connect(self.brightness_label)

        #Option 4: The text threshold
        self.text_thresh = QHBoxLayout()
        self.text_thresh.addWidget(QLabel("Text threshold value"))
        self.text_thresh_slider = QSlider(Qt.Horizontal)
        self.text_thresh_slider.setMinimum(5)
        self.text_thresh_slider.setMaximum(1000)
        self.text_thresh_slider.setValue(150)
        self.text_thresh_slider.setSingleStep(1)
        self.text_thresh_slider.setTickInterval(1)
        self.text_thresh_slider.setTickPosition(QSlider.TicksBelow)
        self.text_thresh.addWidget(self.text_thresh_slider)
        self.text_thresh_value = QLabel('150')
        self.text_thresh.addWidget(self.text_thresh_value)
        self.options_frame_layout.addLayout(self.text_thresh)
        self.text_thresh_slider.valueChanged.connect(self.text_thresh_label)

        #Option 5: The line threshold
        self.line_thresh = QHBoxLayout()
        self.line_thresh.addWidget(QLabel("Line threshold value"))
        self.line_thresh_slider = QSlider(Qt.Horizontal)
        self.line_thresh_slider.setMinimum(1)
        self.line_thresh_slider.setValue(20)
        self.line_thresh_slider.setMaximum(200)
        self.line_thresh_slider.setSingleStep(1)
        self.line_thresh_slider.setTickInterval(1)
        self.line_thresh_slider.setTickPosition(QSlider.TicksBelow)
        self.line_thresh.addWidget(self.line_thresh_slider)
        self.line_thresh_value = QLabel('20')
        self.line_thresh.addWidget(self.line_thresh_value)
        self.options_frame_layout.addLayout(self.line_thresh)
        self.line_thresh_slider.valueChanged.connect(self.line_thresh_label)

        # #Option 6: The upscaling factor
        self.upscaling = QHBoxLayout()
        self.upscaling.addWidget(QLabel("Upscaling factor"))
        self.upscaling_slider = QSlider(Qt.Horizontal)
        self.upscaling_slider.setMinimum(100)
        self.upscaling_slider.setMaximum(400)
        self.upscaling_slider.setValue(200)
        self.upscaling_slider.setSingleStep(1)
        self.upscaling_slider.setTickInterval(1)
        self.upscaling_slider.setTickPosition(QSlider.TicksBelow)
        self.upscaling.addWidget(self.upscaling_slider)
        self.upscaling_value = QLabel('2.0')
        self.upscaling.addWidget(self.upscaling_value)
        self.options_frame_layout.addLayout(self.upscaling)
        self.upscaling_slider.valueChanged.connect(self.upscaling_label)

    def filters_label(self, value):
        if (value == 1):
            self.filters_value.setText('Bilateral')
        elif (value == 2):
            self.filters_value.setText('Median')
        else:
            self.filters_value.setText('Bilateral + Median')

    def illumination_label(self, value):
        self.illumination_value.setText(str(value))

    def brightness_label(self, value):
        if(value == 0):
            self.brightness_value.setText('None')
        else:
            self.brightness_value.setText(str(value))
        
    def text_thresh_label(self, value):
        self.text_thresh_value.setText(str(value))

    def line_thresh_label(self, value):
        self.line_thresh_value.setText(str(value))

    def upscaling_label(self, value):
        self.upscaling_value.setText(str(round(value / 100.0, 2)))

if __name__ == "__main__":
    image_path = '../../testimage3.png'
    image = cv.imread(image_path)
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    m = main()
    m.create(main_window)
    main_window.show()
    process_thread = Thread(target=send_image, args=(m, image))
    process_thread.start()
    app.exec()
    run = False
    process_thread.join()
    sys.exit(app)



