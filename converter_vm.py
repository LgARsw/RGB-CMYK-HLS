from PyQt5.QtWidgets import QColorDialog
from PyQt5.QtGui import QColor
import model.spaces as space_math

class ConverterViewModel:
    def __init__(self):
        self.view = None
        self.r, self.g, self.b = 128, 128, 128
        self.lock = False

    def set_view(self, view):
        self.view = view

    def sync_all_from_rgb(self):
        if self.lock or not self.view: return
        self.lock = True
        
        # Прямой расчет HLS и CMYK на основе базового состояния RGB
        h, l, s = space_math.rgb_to_hls(self.r, self.g, self.b)
        c, m, y_c, k = space_math.rgb_to_cmyk(self.r, self.g, self.b)
        
        self._update_ui_elements(h, l, s, c, m, y_c, k)
        self.lock = False

    def _update_ui_elements(self, h, l, s, c, m, y_c, k):
        v = self.view
        v.sld_r.setValue(self.r); v.edt_r.setText(str(self.r))
        v.sld_g.setValue(self.g); v.edt_g.setText(str(self.g))
        v.sld_b.setValue(self.b); v.edt_b.setText(str(self.b))
        
        h_val, l_val, s_val = int(round(h)), int(round(l)), int(round(s))
        c_val, m_val, y_val, k_val = int(round(c)), int(round(m)), int(round(y_c)), int(round(k))
        
        v.sld_h.setValue(h_val); v.edt_h.setText(str(h_val))
        v.sld_hl.setValue(l_val); v.edt_hl.setText(str(l_val))
        v.sld_hs.setValue(s_val); v.edt_hs.setText(str(s_val))
        
        v.sld_cc.setValue(c_val); v.edt_cc.setText(str(c_val))
        v.sld_cm.setValue(m_val); v.edt_cm.setText(str(m_val))
        v.sld_cy.setValue(y_val); v.edt_cy.setText(str(y_val))
        v.sld_ck.setValue(k_val); v.edt_ck.setText(str(k_val))
        
        v.color_box.setStyleSheet(f"background-color: rgb({self.r},{self.g},{self.b}); border: 1px solid #333;")

    def update_from_sliders(self, source_space):
        if self.lock: return
        v = self.view
        
        if source_space == 'RGB':
            self.r = v.sld_r.value()
            self.g = v.sld_g.value()
            self.b = v.sld_b.value()
        elif source_space == 'HLS':
            h, l, s = v.sld_h.value(), v.sld_hl.value(), v.sld_hs.value()
            self.r, self.g, self.b = space_math.hls_to_rgb(h, l, s)
        elif source_space == 'CMYK':
            c, m, y, k = v.sld_cc.value(), v.sld_cm.value(), v.sld_cy.value(), v.sld_ck.value()
            self.r, self.g, self.b = space_math.cmyk_to_rgb(c, m, y, k)
            
        self.sync_all_from_rgb()

    def update_from_edits(self, source_space):
        if self.lock: return
        try:
            if source_space == 'RGB':
                self.r = max(0, min(255, int(self.view.edt_r.text() or 0)))
                self.g = max(0, min(255, int(self.view.edt_g.text() or 0)))
                self.b = max(0, min(255, int(self.view.edt_b.text() or 0)))
            elif source_space == 'HLS':
                h = max(0, min(360, int(self.view.edt_h.text() or 0)))
                l = max(0, min(100, int(self.view.edt_hl.text() or 0)))
                s = max(0, min(100, int(self.view.edt_hs.text() or 0)))
                self.r, self.g, self.b = space_math.hls_to_rgb(h, l, s)
            elif source_space == 'CMYK':
                c = max(0, min(100, int(self.view.edt_cc.text() or 0)))
                m = max(0, min(100, int(self.view.edt_cm.text() or 0)))
                y = max(0, min(100, int(self.view.edt_cy.text() or 0)))
                k = max(0, min(100, int(self.view.edt_ck.text() or 0)))
                self.r, self.g, self.b = space_math.cmyk_to_rgb(c, m, y, k)
                
            self.sync_all_from_rgb()
        except ValueError:
            pass

    def open_dialog_picker(self):
        color = QColorDialog.getColor(QColor(self.r, self.g, self.b), self.view, "Выберите цвет")
        if color.isValid():
            self.r, self.g, self.b = color.red(), color.green(), color.blue()
            self.sync_all_from_rgb()
