import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QSlider, QLineEdit, QPushButton, QStatusBar, QMessageBox) 
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator

class MainWindow(QMainWindow):
    def __init__(self, vm):
        super().__init__()
        self.vm = vm
        self.setWindowTitle("Лабораторная работа №1 — Прямые переходы (RGB ↔ CMYK ↔ HLS)")
        self.setGeometry(100, 100, 850, 650) # Стабильный стартовый размер окна
        
        self.init_ui()
        self.vm.set_view(self)
        self.vm.sync_all_from_rgb()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # --- ВЕРХНЯЯ ПАНЕЛЬ С КНОПКОЙ ---
        cfg_layout = QHBoxLayout()
        cfg_layout.addStretch()
        
        self.btn_help = QPushButton("Справка")
        self.btn_help.setFixedWidth(120)  # Кнопка расширена, текст не зажат
        cfg_layout.addWidget(self.btn_help)
        layout.addLayout(cfg_layout)
        
        # --- ПАЛИТРА И ПРОСМОТР ---
        preview_layout = QHBoxLayout()
        self.btn_picker = QPushButton("Выбрать цвет из палитры")
        preview_layout.addWidget(self.btn_picker)
        
        self.color_box = QWidget()
        self.color_box.setMinimumHeight(50)
        preview_layout.addWidget(self.color_box)
        layout.addLayout(preview_layout)
        
        # --- БЛОК RGB ---
        layout.addWidget(QLabel("<h3>Модель RGB (0 - 255)</h3>"))
        self.sld_r, self.edt_r = self.add_row(layout, "Red:")
        self.sld_g, self.edt_g = self.add_row(layout, "Green:")
        self.sld_b, self.edt_b = self.add_row(layout, "Blue:")
        
        # --- БЛОК HLS ---
        layout.addWidget(QLabel("<h3>Модель HLS (H: 0..360, L/S: 0..100)</h3>"))
        self.sld_h, self.edt_h = self.add_row(layout, "Hue (H):", 0, 360)
        self.sld_hl, self.edt_hl = self.add_row(layout, "Lightness (L):", 0, 100)
        self.sld_hs, self.edt_hs = self.add_row(layout, "Saturation (S):", 0, 100)
        
        # --- БЛОК CMYK ---
        layout.addWidget(QLabel("<h3>Модель CMYK (0 - 100)</h3>"))
        self.sld_cc, self.edt_cc = self.add_row(layout, "Cyan (C):", 0, 100)
        self.sld_cm, self.edt_cm = self.add_row(layout, "Magenta (M):", 0, 100)
        self.sld_cy, self.edt_cy = self.add_row(layout, "Yellow (Y):", 0, 100)
        self.sld_ck, self.edt_ck = self.add_row(layout, "Key (K):", 0, 100)
        
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        
        self.connect_signals()

    def add_row(self, parent_layout, label_text, min_v=0, max_v=255):
        row = QHBoxLayout()
        
        # Создаем фиксированные зазоры в строке, чтобы элементы не слипались при растяжении
        row.setContentsMargins(10, 0, 10, 0)
        row.setSpacing(15)
        
        lbl = QLabel(label_text)
        # Выравнивание текста строго по правому краю и центру по вертикали
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Расширили ширину до 180px — теперь любое длинное слово гарантированно влезет целиком
        lbl.setFixedWidth(180) 
        # Небольшой визуальный отступ справа, чтобы текст не лип к началу ползунка
        lbl.setStyleSheet("padding-right: 6px; font-weight: 500;") 
        row.addWidget(lbl)
        
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_v, max_v)
        slider.setSingleStep(1)
        slider.setPageStep(10)
        row.addWidget(slider, 5)
        
        edit = QLineEdit()
        edit.setFixedWidth(90)  # Увеличенные поля для целых чисел
        
        # --- ИСПРАВЛЕНИЕ: Выравнивание текста внутри числовых полей ввода по правому краю ---
        edit.setAlignment(Qt.AlignRight) 
        
        edit.setValidator(QIntValidator(min_v, max_v, self))  # Запрет букв и некорректного ввода
        row.addWidget(edit, 1)
        
        parent_layout.addLayout(row)
        return slider, edit

    def connect_signals(self):
        self.btn_picker.clicked.connect(self.vm.open_dialog_picker)
        self.btn_help.clicked.connect(self.show_help)
        
        # Изменение ползунков (работает мгновенно)
        self.sld_r.valueChanged.connect(lambda: self.vm.update_from_sliders('RGB'))
        self.sld_g.valueChanged.connect(lambda: self.vm.update_from_sliders('RGB'))
        self.sld_b.valueChanged.connect(lambda: self.vm.update_from_sliders('RGB'))
        
        self.sld_h.valueChanged.connect(lambda: self.vm.update_from_sliders('HLS'))
        self.sld_hl.valueChanged.connect(lambda: self.vm.update_from_sliders('HLS'))
        self.sld_hs.valueChanged.connect(lambda: self.vm.update_from_sliders('HLS'))
        
        self.sld_cc.valueChanged.connect(lambda: self.vm.update_from_sliders('CMYK'))
        self.sld_cm.valueChanged.connect(lambda: self.vm.update_from_sliders('CMYK'))
        self.sld_cy.valueChanged.connect(lambda: self.vm.update_from_sliders('CMYK'))
        self.sld_ck.valueChanged.connect(lambda: self.vm.update_from_sliders('CMYK'))
        
        # Изменение полей ввода (срабатывает только после окончания ввода — цифры не прыгают)
        self.edt_r.editingFinished.connect(lambda: self.vm.update_from_edits('RGB'))
        self.edt_g.editingFinished.connect(lambda: self.vm.update_from_edits('RGB'))
        self.edt_b.editingFinished.connect(lambda: self.vm.update_from_edits('RGB'))
        
        self.edt_h.editingFinished.connect(lambda: self.vm.update_from_edits('HLS'))
        self.edt_hl.editingFinished.connect(lambda: self.vm.update_from_edits('HLS'))
        self.edt_hs.editingFinished.connect(lambda: self.vm.update_from_edits('HLS'))
        
        self.edt_cc.editingFinished.connect(lambda: self.vm.update_from_edits('CMYK'))
        self.edt_cm.editingFinished.connect(lambda: self.vm.update_from_edits('CMYK'))
        self.edt_cy.editingFinished.connect(lambda: self.vm.update_from_edits('CMYK'))
        self.edt_ck.editingFinished.connect(lambda: self.vm.update_from_edits('CMYK'))

    def show_help(self):
        help_text = (
            "<b>Лабораторная работа №1 — Вариант 2</b><br><br>"
            "Приложение демонстрирует прямую конвертацию между цветовыми моделями "
            "<b>RGB</b>, <b>CMYK</b> и <b>HLS</b> без привлечения сторонних пространств."
        )
        QMessageBox.information(self, "О программе", help_text)
