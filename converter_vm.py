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
        """Используется для полной синхронизации (например, при старте или из QColorDialog)"""
        if self.lock or not self.view: return
        self.lock = True
        
        h, l, s = space_math.rgb_to_hls(self.r, self.g, self.b)
        c, m, y_c, k = space_math.rgb_to_cmyk(self.r, self.g, self.b)
        
        # Передаем 'ALL', чтобы обновилось абсолютно всё
        self._update_ui_elements(h, l, s, c, m, y_c, k, exclude_space='NONE')
        self.lock = False

    def _update_ui_elements(self, h, l, s, c, m, y_c, k, exclude_space='NONE'):
        v = self.view
        
        # Временно блокируем сигналы абсолютно всех виджетов во избежание рекурсии PyQt
        widgets = [v.sld_r, v.edt_r, v.sld_g, v.edt_g, v.sld_b, v.edt_b,
                   v.sld_h, v.edt_h, v.sld_hl, v.edt_hl, v.sld_hs, v.edt_hs,
                   v.sld_cc, v.edt_cc, v.sld_cm, v.edt_cm, v.sld_cy, v.edt_cy, v.sld_ck, v.edt_ck]
        
        for w in widgets:
            w.blockSignals(True)
            
        h_val, l_val, s_val = int(round(h)), int(round(l)), int(round(s))
        c_val, m_val, y_val, k_val = int(round(c)), int(round(m)), int(round(y_c)), int(round(k))

        # Обновляем RGB только если изменения пришли НЕ из RGB
        if exclude_space != 'RGB':
            v.sld_r.setValue(self.r); v.edt_r.setText(str(self.r))
            v.sld_g.setValue(self.g); v.edt_g.setText(str(self.g))
            v.sld_b.setValue(self.b); v.edt_b.setText(str(self.b))
        
        # Обновляем HLS только если изменения пришли НЕ из HLS
        if exclude_space != 'HLS':
            v.sld_h.setValue(h_val); v.edt_h.setText(str(h_val))
            v.sld_hl.setValue(l_val); v.edt_hl.setText(str(l_val))
            v.sld_hs.setValue(s_val); v.edt_hs.setText(str(s_val))
        
        # Обновляем CMYK только если изменения пришли НЕ из CMYK
        if exclude_space != 'CMYK':
            v.sld_cc.setValue(c_val); v.edt_cc.setText(str(c_val))
            v.sld_cm.setValue(m_val); v.edt_cm.setText(str(m_val))
            v.sld_cy.setValue(y_val); v.edt_cy.setText(str(y_val))
            v.sld_ck.setValue(k_val); v.edt_ck.setText(str(k_val))
        
        # Цвет квадрата обновляем всегда
        v.color_box.setStyleSheet(f"background-color: rgb({self.r},{self.g},{self.b}); border: 1px solid #333;")

        # Возвращаем сигналы обратно
        for w in widgets:
            w.blockSignals(False)

    def update_from_sliders(self, source_space):
        if self.lock: return
        self.lock = True
        v = self.view
        
        if source_space == 'RGB':
            self.r = v.sld_r.value()
            self.g = v.sld_g.value()
            self.b = v.sld_b.value()
            h, l, s = space_math.rgb_to_hls(self.r, self.g, self.b)
            c, m, y_c, k = space_math.rgb_to_cmyk(self.r, self.g, self.b)
            
            # Синхронизируем текстовые поля для Самой RGB модели (чтобы циферка менялась при движении ползунка)
            v.edt_r.blockSignals(True); v.edt_r.setText(str(self.r)); v.edt_r.blockSignals(False)
            v.edt_g.blockSignals(True); v.edt_g.setText(str(self.g)); v.edt_g.blockSignals(False)
            v.edt_b.blockSignals(True); v.edt_b.setText(str(self.b)); v.edt_b.blockSignals(False)
            
        elif source_space == 'HLS':
            h, l, s = v.sld_h.value(), v.sld_hl.value(), v.sld_hs.value()
            self.r, self.g, self.b = space_math.hls_to_rgb(h, l, s)
            c, m, y_c, k = space_math.rgb_to_cmyk(self.r, self.g, self.b)
            
            # Синхронизируем текстовые поля для Самой HLS модели
            v.edt_h.blockSignals(True); v.edt_h.setText(str(h)); v.edt_h.blockSignals(False)
            v.edt_hl.blockSignals(True); v.edt_hl.setText(str(l)); v.edt_hl.blockSignals(False)
            v.edt_hs.blockSignals(True); v.edt_hs.setText(str(s)); v.edt_hs.blockSignals(False)
            
        elif source_space == 'CMYK':
            c, m, y_c, k = v.sld_cc.value(), v.sld_cm.value(), v.sld_cy.value(), v.sld_ck.value()
            self.r, self.g, self.b = space_math.cmyk_to_rgb(c, m, y_c, k)
            h, l, s = space_math.rgb_to_hls(self.r, self.g, self.b)
            
            # Синхронизируем текстовые поля для Самой CMYK модели
            v.edt_cc.blockSignals(True); v.edt_cc.setText(str(c)); v.edt_cc.blockSignals(False)
            v.edt_cm.blockSignals(True); v.edt_cm.setText(str(m)); v.edt_cm.blockSignals(False)
            v.edt_cy.blockSignals(True); v.edt_cy.setText(str(y_c)); v.edt_cy.blockSignals(False)
            v.edt_ck.blockSignals(True); v.edt_ck.setText(str(k)); v.edt_ck.blockSignals(False)
            
        # Обновляем всё, КРОМЕ той модели, ползунок которой мы сейчас тянем
        self._update_ui_elements(h, l, s, c, m, y_c, k, exclude_space=source_space)
        self.lock = False

    def update_from_edits(self, source_space):
        if self.lock: return
        self.lock = True
        try:
            v = self.view
            if source_space == 'RGB':
                self.r = max(0, min(255, int(v.edt_r.text() or 0)))
                self.g = max(0, min(255, int(v.edt_g.text() or 0)))
                self.b = max(0, min(255, int(v.edt_b.text() or 0)))
                h, l, s = space_math.rgb_to_hls(self.r, self.g, self.b)
                c, m, y_c, k = space_math.rgb_to_cmyk(self.r, self.g, self.b)
                
                # Синхронизируем ползунки внутри самой RGB
                v.sld_r.blockSignals(True); v.sld_r.setValue(self.r); v.sld_r.blockSignals(False)
                v.sld_g.blockSignals(True); v.sld_g.setValue(self.g); v.sld_g.blockSignals(False)
                v.sld_b.blockSignals(True); v.sld_b.setValue(self.b); v.sld_b.blockSignals(False)
                
            elif source_space == 'HLS':
                h = max(0, min(360, int(v.edt_h.text() or 0)))
                l = max(0, min(100, int(v.edt_hl.text() or 0)))
                s = max(0, min(100, int(v.edt_hs.text() or 0)))
                self.r, self.g, self.b = space_math.hls_to_rgb(h, l, s)
                c, m, y_c, k = space_math.rgb_to_cmyk(self.r, self.g, self.b)
                
                # Синхронизируем ползунки внутри самой HLS
                v.sld_h.blockSignals(True); v.sld_h.setValue(h); v.sld_h.blockSignals(False)
                v.sld_hl.blockSignals(True); v.sld_hl.setValue(l); v.sld_hl.blockSignals(False)
                v.sld_hs.blockSignals(True); v.sld_hs.setValue(s); v.sld_hs.blockSignals(False)
                
            elif source_space == 'CMYK':
                c = max(0, min(100, int(v.edt_cc.text() or 0)))
                m = max(0, min(100, int(v.edt_cm.text() or 0)))
                y_c = max(0, min(100, int(v.edt_cy.text() or 0)))
                k = max(0, min(100, int(v.edt_ck.text() or 0)))
                self.r, self.g, self.b = space_math.cmyk_to_rgb(c, m, y_c, k)
                h, l, s = space_math.rgb_to_hls(self.r, self.g, self.b)
                
                # Синхронизируем ползунки внутри самой CMYK
                v.sld_cc.blockSignals(True); v.sld_cc.setValue(c); v.sld_cc.blockSignals(False)
                v.sld_cm.blockSignals(True); v.sld_cm.setValue(m); v.sld_cm.blockSignals(False)
                v.sld_cy.blockSignals(True); v.sld_cy.setValue(y_c); v.sld_cy.blockSignals(False)
                v.sld_ck.blockSignals(True); v.sld_ck.setValue(k); v.sld_ck.blockSignals(False)
                
            self._update_ui_elements(h, l, s, c, m, y_c, k, exclude_space=source_space)
        except ValueError:
            pass
        finally:
            self.lock = False

    def open_dialog_picker(self):
        color = QColorDialog.getColor(QColor(self.r, self.g, self.b), self.view, "Выберите цвет")
        if color.isValid():
            self.r, self.g, self.b = color.red(), color.green(), color.blue()
            self.sync_all_from_rgb()
