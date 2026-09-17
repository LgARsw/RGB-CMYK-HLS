from PyQt5.QtWidgets import QColorDialog
from PyQt5.QtGui import QColor
import model.spaces as space_math
import model.illuminants as illum_math

class ConverterViewModel:
    def __init__(self):
        self.view = None
        self.r, self.g, self.b = 128, 128, 128
        self.lock = False

    def set_view(self, view):
        self.view = view

    def on_illum_changed(self):
        # Принудительно вызываем пересчет матриц Брэдфорда в логах
        illum = self.view.combo_illum.currentText()
        illum_math.get_rgb_to_xyz_matrix(illum)
        self.sync_all_from_rgb()

    def sync_all_from_rgb(self):
        if self.lock or not self.view: return
        self.lock = True
        
        cmyk_m = self.view.combo_cmyk.currentText()
        h, l, s = space_math.rgb_to_hls(self.r, self.g, self.b)
        c, m, y_c, k = space_math.rgb_to_cmyk(self.r, self.g, self.b, cmyk_m)
        
        self._update_ui_elements(h, l, s, c, m, y_c, k)
        self.lock = False

    def _update_ui_elements(self, h, l, s, c, m, y_c, k):
        v = self.view
        v.sld_r.setValue(self.r); v.edt_r.setText(str(self.r))
        v.sld_g.setValue(self.g); v.edt_g.setText(str(self.g))
        v.sld_b.setValue(self.b); v.edt_b.setText(str(self.b))
        
        v.sld_h.setValue(int(round(h))); v.edt_h.setText(f"{h:.1f}°")
        v.sld_hl.setValue(int(round(l))); v.edt_hl.setText(f"{l:.1f}%")
        v.sld_hs.setValue(int(round(s))); v.edt_hs.setText(f"{s:.1f}%")
        
        v.sld_cc.setValue(int(round(c))); v.edt_cc.setText(f"{c:.1f}")
        v.sld_cm.setValue(int(round(m))); v.edt_cm.setText(f"{m:.1f}")
        v.sld_cy.setValue(int(round(y_c))); v.edt_cy.setText(f"{y_c:.1f}")
        v.sld_ck.setValue(int(round(k))); v.edt_ck.setText(f"{k:.1f}")
        
        v.color_box.setStyleSheet(f"background-color: rgb({self.r},{self.g},{self.b}); border: 1px solid #333;")
        
        # Динамические интерактивные градиенты под слайдерами (Требование 5)
        v.sld_g.setStyleSheet(f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgb({self.r},0,{self.b}), stop:1 rgb({self.r},255,{self.b}));")
        v.sld_b.setStyleSheet(f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgb({self.r},{self.g},0), stop:1 rgb({self.r},{self.g},255));")

    def update_from_sliders(self, source_space):
        if self.lock: return
        v = self.view
        strat = v.combo_gamut.currentText()
        
        if source_space == 'RGB':
            self.r = v.sld_r.value()
            self.g = v.sld_g.value()
            self.b = v.sld_b.value()
        elif source_space == 'HLS':
            h = v.sld_h.value()
            l = v.sld_hl.value()
            s = v.sld_hs.value()
            self.r, self.g, self.b, out = space_math.hls_to_rgb(h, l, s, strat)
            if out: v.status.showMessage(f"Превышен охват! Выполнено: {strat}", 3000)
        elif source_space == 'CMYK':
            c, m, y, k = v.sld_cc.value(), v.sld_cm.value(), v.sld_cy.value(), v.sld_ck.value()
            self.r, self.g, self.b = space_math.cmyk_to_rgb(c, m, y, k)
            
        self.sync_all_from_rgb()

    def update_from_edits(self, source_space):
        try:
            if source_space == 'RGB':
                self.r = max(0, min(255, int(self.view.edt_r.text())))
                self.g = max(0, min(255, int(self.view.edt_g.text())))
                self.b = max(0, min(255, int(self.view.edt_b.text())))
                self.sync_all_from_rgb()
        except ValueError:
            pass

    def open_dialog_picker(self):
        color = QColorDialog.getColor(QColor(self.r, self.g, self.b), self.view, "Выберите цвет")
        if color.isValid():
            self.r, self.g, self.b = color.red(), color.green(), color.blue()
            self.sync_all_from_rgb()
