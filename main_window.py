from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QSlider, QLineEdit, QComboBox, QPushButton, 
                             QStatusBar, QMessageBox) # Добавили QMessageBox для окна справки
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self, vm):
        super().__init__()
        self.vm = vm
        self.setWindowTitle("Лабораторная работа №1 — Вариант 2 (RGB ↔ CMYK ↔ HLS)")
        self.setGeometry(100, 100, 850, 600)
        
        self.init_ui()
        self.vm.set_view(self)
        self.vm.sync_all_from_rgb()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # --- НАСТРОЙКИ СТАНДАРТОВ ---
        cfg_layout = QHBoxLayout()
        cfg_layout.addWidget(QLabel("Стандарт освещения:"))
        self.combo_illum = QComboBox()
        self.combo_illum.addItems(["D65", "D50", "E"])
        cfg_layout.addWidget(self.combo_illum)
        
        cfg_layout.addWidget(QLabel("Метод CMYK:"))
        self.combo_cmyk = QComboBox()
        self.combo_cmyk.addItems(["GCR", "UCR"])
        cfg_layout.addWidget(self.combo_cmyk)
        
        cfg_layout.addWidget(QLabel("Вне охвата:"))
        self.combo_gamut = QComboBox()
        self.combo_gamut.addItems(["Clipping", "Scaling"])
        cfg_layout.addWidget(self.combo_gamut)
        
        # --- КНОПКА СПРАВКИ (HELP) ---
        self.btn_help = QPushButton("Справка")
        self.btn_help.setFixedWidth(80) # Аккуратный фиксированный размер
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
        
        # --- СЛАЙДЕРЫ ---
        layout.addWidget(QLabel("<h3>Модель RGB (0 - 255)</h3>"))
        self.sld_r, self.edt_r = self.add_row(layout, "Red:")
        self.sld_g, self.edt_g = self.add_row(layout, "Green:")
        self.sld_b, self.edt_b = self.add_row(layout, "Blue:")
        
        layout.addWidget(QLabel("<h3>Модель HLS (H: 0..360°, L/S: 0..100%)</h3>"))
        self.sld_h, self.edt_h = self.add_row(layout, "Hue (H):", 0, 360)
        self.sld_hl, self.edt_hl = self.add_row(layout, "Lightness (L):", 0, 100)
        self.sld_hs, self.edt_hs = self.add_row(layout, "Saturation (S):", 0, 100)
        
        layout.addWidget(QLabel("<h3>Модель CMYK (0% - 100%)</h3>"))
        self.sld_cc, self.edt_cc = self.add_row(layout, "C (%):", 0, 100)
        self.sld_cm, self.edt_cm = self.add_row(layout, "M (%):", 0, 100)
        self.sld_cy, self.edt_cy = self.add_row(layout, "Y (%):", 0, 100)
        self.sld_ck, self.edt_ck = self.add_row(layout, "K (%):", 0, 100)
        
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        
        self.connect_signals()

    def add_row(self, parent_layout, label_text, min_v=0, max_v=255):
        row = QHBoxLayout()
        row.addWidget(QLabel(label_text), 1)
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_v, max_v)
        row.addWidget(slider, 5)
        edit = QLineEdit()
        edit.setFixedWidth(60)
        row.addWidget(edit, 1)
        parent_layout.addLayout(row)
        return slider, edit

    def connect_signals(self):
        self.combo_illum.currentIndexChanged.connect(lambda: self.vm.on_illum_changed())
        self.combo_cmyk.currentIndexChanged.connect(lambda: self.vm.sync_all_from_rgb())
        self.combo_gamut.currentIndexChanged.connect(lambda: self.vm.sync_all_from_rgb())
        self.btn_picker.clicked.connect(self.vm.open_dialog_picker)
        
        # Подключаем клик по кнопке справки к методу отображения окна
        self.btn_help.clicked.connect(self.show_help)
        
        self.sld_r.valueChanged.connect(lambda v: self.vm.update_from_sliders('RGB'))
        self.sld_g.valueChanged.connect(lambda v: self.vm.update_from_sliders('RGB'))
        self.sld_b.valueChanged.connect(lambda v: self.vm.update_from_sliders('RGB'))
        
        self.sld_h.valueChanged.connect(lambda v: self.vm.update_from_sliders('HLS'))
        self.sld_hl.valueChanged.connect(lambda v: self.vm.update_from_sliders('HLS'))
        self.sld_hs.valueChanged.connect(lambda v: self.vm.update_from_sliders('HLS'))
        
        self.sld_cc.valueChanged.connect(lambda v: self.vm.update_from_sliders('CMYK'))
        self.sld_cm.valueChanged.connect(lambda v: self.vm.update_from_sliders('CMYK'))
        self.sld_cy.valueChanged.connect(lambda v: self.vm.update_from_sliders('CMYK'))
        self.sld_ck.valueChanged.connect(lambda v: self.vm.update_from_sliders('CMYK'))
        
        self.edt_r.editingFinished.connect(lambda: self.vm.update_from_edits('RGB'))
        self.edt_g.editingFinished.connect(lambda: self.vm.update_from_edits('RGB'))
        self.edt_b.editingFinished.connect(lambda: self.vm.update_from_edits('RGB'))

    # Новый метод, который будет показывать красивое всплывающее окошко
    def show_help(self):
        help_text = (
            "<b>Лабораторная работа №1 — Вариант 2</b><br><br>"
            "Приложение предназначено для конвертации цветов между цветовыми моделями "
            "<b>RGB</b>, <b>CMYK</b> и <b>HLS</b> в режиме реального времени.<br><br>"
            "<b>Основные возможности:</b><br>"
            "• Интерактивное изменение цвета слайдерами или вводом точных значений.<br>"
            "• Поддержка стандартов освещения (D65, D50, E).<br>"
            "• Расчет CMYK с использованием методов генерации черного (GCR / UCR).<br>"
            "• Обработка цветов вне цветового охвата (Clipping / Scaling).<br>"
            "• Быстрый выбор цвета с помощью системной палитры."
        )
        QMessageBox.information(self, "О программе / Справка", help_text)
