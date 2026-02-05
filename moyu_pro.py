import sys
import os
import json
import webbrowser
import fitz  # PyMuPDF
import keyboard  # 键盘监听
import requests  # 网络请求
from pynput import mouse  # 鼠标全局监听
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QFileDialog, QLabel, QLineEdit, QHBoxLayout, 
                             QMessageBox, QDialog, QTextBrowser, QProgressBar, 
                             QListWidget, QColorDialog, QSpinBox, QGridLayout,
                             QSystemTrayIcon, QMenu, QAction, QStyle, qApp, QCheckBox, QDesktopWidget)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QFont, QColor, QIcon, QKeySequence

# --- 资源路径处理 ---
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# --- 配置区域 ---
APP_DATA_DIR = os.path.join(os.getenv('APPDATA'), "OxygenReaderData")
if not os.path.exists(APP_DATA_DIR):
    os.makedirs(APP_DATA_DIR)

HISTORY_FILE = os.path.join(APP_DATA_DIR, "bookshelf.json")
CONFIG_FILE = os.path.join(APP_DATA_DIR, "config.json")

# 【更新】版本号 V1.1.2
CURRENT_VERSION = "V1.1.2" 
VERSION_URL = "http://my.wkblog.com.cn/new/bbh.html"
LOG_URL = "http://my.wkblog.com.cn/new/rz.html"
OFFICIAL_SITE = "http://my.wkblog.com.cn/"
DOWNLOAD_URL = "http://my.wkblog.com.cn/azb/Oxygen.exe"

class GlobalSignal(QObject):
    hide_signal = pyqtSignal()
    show_signal = pyqtSignal()
    next_signal = pyqtSignal()
    prev_signal = pyqtSignal()
    update_style_signal = pyqtSignal()

class ConfigManager:
    def __init__(self):
        self.config = {
            "window_title": "Oxygen阅读器", 
            "font_size": 12,
            "text_color": "#505050",
            "bg_color": "#00000000",
            "key_next": "t",
            "key_prev": "q",
            "key_boss": "ctrl+shift+q",
            "key_wake": "ctrl+shift+f",
            "focus_anchor": True 
        }
        self.load()

    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    self.config.update(saved)
                
                current_title = self.config.get("window_title", "")
                if "V0.0" in current_title or "Oxygen阅读器 V" in current_title:
                    self.config["window_title"] = "Oxygen阅读器"
            except: pass

    def save(self):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)

class BookShelf:
    def __init__(self):
        self.data = {}
        self.load()
    def load(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f: self.data = json.load(f)
            except: self.data = {}
    def save(self):
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f: json.dump(self.data, f, indent=2)
    def update_progress(self, filepath, line_index):
        if filepath: self.data[filepath] = line_index; self.save()
    def get_progress(self, filepath): return self.data.get(filepath, 0)
    def get_recent_books(self): return list(self.data.keys())

class HotkeyLineEdit(QLineEdit):
    def __init__(self, default_text="", parent=None):
        super().__init__(default_text, parent)
        self.setPlaceholderText("点击并按下按键...")
        self.setReadOnly(True) 

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Backspace or key == Qt.Key_Delete:
            self.setText("")
            return
        if key in (Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt, Qt.Key_Meta):
            return
        modifiers = event.modifiers()
        keys = []
        if modifiers & Qt.ControlModifier: keys.append("ctrl")
        if modifiers & Qt.ShiftModifier: keys.append("shift")
        if modifiers & Qt.AltModifier: keys.append("alt")
        key_text = QKeySequence(key).toString().lower()
        if key_text == "return": key_text = "enter"
        if key_text == "pgup": key_text = "page up"
        if key_text == "pgdown": key_text = "page down"
        if key_text == "left": key_text = "left"
        if key_text == "right": key_text = "right"
        if key_text == "up": key_text = "up"
        if key_text == "down": key_text = "down"
        if key_text: keys.append(key_text)
        self.setText("+".join(keys))

class UpdateWorker(QThread):
    result_signal = pyqtSignal(bool, str, str)
    def run(self):
        try:
            resp = requests.get(VERSION_URL, timeout=5)
            remote = resp.text.strip()
            def ver_to_int(v): return int(v.lower().replace('v','').replace('.',''))
            if ver_to_int(remote) > ver_to_int(CURRENT_VERSION):
                log = requests.get(LOG_URL, timeout=5); log.encoding='utf-8'
                self.result_signal.emit(True, remote, log.text)
            else: self.result_signal.emit(False, remote, "")
        except Exception as e: self.result_signal.emit(False, "Error", str(e))

class DownloadWorker(QThread):
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(str)
    def run(self):
        try:
            path = os.path.join(os.path.expanduser("~"), "Desktop", "Oxygen.exe")
            r = requests.get(DOWNLOAD_URL, stream=True)
            total = int(r.headers.get('content-length', 0))
            with open(path, 'wb') as f:
                dl = 0
                for d in r.iter_content(4096):
                    dl+=len(d); f.write(d)
                    if total>0: self.progress_signal.emit(int(dl/total*100))
            self.finished_signal.emit(path)
        except Exception as e: self.finished_signal.emit(f"Error: {e}")

class UpdateDialog(QDialog):
    def __init__(self, ver, log):
        super().__init__()
        self.setWindowTitle(f"新版本 {ver}"); self.resize(400,300); l=QVBoxLayout()
        b=QTextBrowser(); b.setHtml(log); l.addWidget(QLabel("日志:")); l.addWidget(b)
        btn1=QPushButton("去官网"); btn1.clicked.connect(lambda: webbrowser.open(OFFICIAL_SITE)); l.addWidget(btn1)
        self.btn2=QPushButton("下载到桌面"); self.btn2.clicked.connect(self.dl); l.addWidget(self.btn2)
        self.p=QProgressBar(); self.p.hide(); l.addWidget(self.p); self.setLayout(l)
    def dl(self):
        self.btn2.setEnabled(False); self.p.show(); self.w=DownloadWorker()
        self.w.progress_signal.connect(self.p.setValue)
        self.w.finished_signal.connect(lambda p: QMessageBox.information(self,"完成",p) if "Error" not in p else QMessageBox.warning(self,"失败",p))
        self.w.start()

class ReaderWindow(QWidget):
    def __init__(self, bookshelf, config_mgr):
        super().__init__()
        self.bookshelf = bookshelf
        self.cfg = config_mgr
        self.current_file = None
        self.is_focus_mode = False 
        
        icon_path = resource_path("logo.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.layout = QVBoxLayout(); self.layout.setContentsMargins(10, 5, 10, 5)
        self.text_label = QLabel("按 Ctrl+Shift+F 唤醒")
        self.layout.addWidget(self.text_label); self.setLayout(self.layout)
        self.content_lines = []; self.current_index = 0; self.drag_pos = None
        self.apply_style()

    def reset_focus(self):
        if self.cfg.config.get("focus_anchor", True):
            self.is_focus_mode = True
        else:
            self.is_focus_mode = False

    def apply_style(self):
        c = self.cfg.config
        bg = c["bg_color"] if c["bg_color"] != "#00000000" and c["bg_color"] != "transparent" else "transparent"
        self.setStyleSheet(f"QWidget {{ background-color: {bg}; }}")
        font = QFont("Microsoft YaHei", int(c["font_size"]))
        self.text_label.setFont(font)
        
        if not self.is_focus_mode:
            self.text_label.setStyleSheet(f"color: {c['text_color']}; background-color: transparent;")
        
        self.adjustSize()

    def load_book(self, path):
        if not os.path.exists(path): return
        self.current_file = path
        try:
            doc = fitz.open(path)
            text = "".join([page.get_text() for page in doc])
            self.content_lines = [l.strip() for l in text.split('\n') if l.strip()]
            doc.close()
            idx = self.bookshelf.get_progress(path)
            self.current_index = idx if idx < len(self.content_lines) else 0
        except Exception as e: self.text_label.setText(f"Err: {e}")

    def show_line(self):
        txt = self.content_lines[self.current_index] if 0<=self.current_index<len(self.content_lines) else "--- End ---"
        self.text_label.setText(txt)
        
        if self.is_focus_mode:
            self.text_label.setStyleSheet("color: #FF3333; font-weight: bold; background-color: transparent;")
            self.is_focus_mode = False
        else:
            c = self.cfg.config
            self.text_label.setStyleSheet(f"color: {c['text_color']}; font-weight: normal; background-color: transparent;")
            
        self.adjustSize()
        self.bookshelf.update_progress(self.current_file, self.current_index)

    def next_line(self):
        if self.current_file: self.current_index+=1; self.show_line()
    def prev_line(self):
        if self.current_file and self.current_index>0: self.current_index-=1; self.show_line()
    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton: self.drag_pos = e.globalPos() - self.frameGeometry().topLeft()
    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.RightButton and self.drag_pos: self.move(e.globalPos() - self.drag_pos)

class ControlPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.cfg = ConfigManager()
        
        icon_path = resource_path("logo.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.setWindowTitle(self.cfg.config.get("window_title", "Oxygen阅读器"))
        self.resize(600, 500)
        
        self.bookshelf = BookShelf()
        self.reader = ReaderWindow(self.bookshelf, self.cfg)
        self.comm = GlobalSignal()
        
        self.comm.hide_signal.connect(self.reader.hide)
        self.comm.show_signal.connect(lambda: (self.reader.show(), self.reader.activateWindow()) if self.reader.current_file else None)
        self.comm.update_style_signal.connect(self.reader.apply_style)
        self.comm.next_signal.connect(self.reader.next_line)
        self.comm.prev_signal.connect(self.reader.prev_line)

        self.init_tray()
        self.init_ui()
        self.start_hooks()

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        icon_path = resource_path("logo.ico")
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        
        tray_menu = QMenu()
        action_show = QAction("显示控制台", self)
        action_show.triggered.connect(self.showNormal)
        tray_menu.addAction(action_show)
        action_quit = QAction("彻底退出", self)
        action_quit.triggered.connect(qApp.quit)
        tray_menu.addAction(action_quit)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_click)
        self.tray_icon.show()

    def on_tray_click(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            if self.isVisible(): self.hide()
            else: self.showNormal(); self.activateWindow()

    def closeEvent(self, event):
        if self.tray_icon.isVisible():
            self.hide()
            self.tray_icon.showMessage("提示", "已缩略至系统托盘，右键托盘图标可退出。", QSystemTrayIcon.Information, 2000)
            event.ignore()
        else: event.accept()

    def init_ui(self):
        main_layout = QVBoxLayout()
        self.lbl_status = QLabel("Oxygen Reader 准备就绪")
        main_layout.addWidget(self.lbl_status)
        
        h1 = QHBoxLayout()
        btn_imp = QPushButton("导入书籍"); btn_imp.clicked.connect(self.import_book); h1.addWidget(btn_imp)
        btn_run = QPushButton("开始阅读"); btn_run.clicked.connect(self.start_reading); h1.addWidget(btn_run)
        btn_upd = QPushButton("检测更新"); btn_upd.clicked.connect(self.check_update); h1.addWidget(btn_upd)
        main_layout.addLayout(h1)

        grp_box = QGridLayout()
        grp_box.addWidget(QLabel("<b>伪装与外观:</b>"), 0, 0)
        
        self.inp_title = QLineEdit(self.cfg.config.get("window_title", ""))
        self.inp_title.setPlaceholderText("Oxygen阅读器") 
        grp_box.addWidget(QLabel("窗口伪装名:"), 0, 1)
        grp_box.addWidget(self.inp_title, 0, 2)

        self.spin_font = QSpinBox(); self.spin_font.setRange(8, 72); self.spin_font.setValue(int(self.cfg.config["font_size"]))
        self.spin_font.valueChanged.connect(self.save_appearance)
        grp_box.addWidget(QLabel("字号:"), 0, 3); grp_box.addWidget(self.spin_font, 0, 4)
        
        btn_col_txt = QPushButton("文字颜色"); btn_col_txt.clicked.connect(lambda: self.pick_color("text_color"))
        grp_box.addWidget(btn_col_txt, 1, 3)
        btn_col_bg = QPushButton("背景颜色"); btn_col_bg.clicked.connect(lambda: self.pick_color("bg_color"))
        grp_box.addWidget(btn_col_bg, 1, 4)
        
        self.chk_focus = QCheckBox("启用聚焦引导(启动时红字居中)")
        self.chk_focus.setChecked(self.cfg.config.get("focus_anchor", True))
        self.chk_focus.toggled.connect(self.toggle_focus)
        grp_box.addWidget(self.chk_focus, 1, 0, 1, 3)

        grp_box.addWidget(QLabel("<b>快捷键 (点框按下按键自动录入):</b>"), 2, 0)
        self.inp_next = HotkeyLineEdit(self.cfg.config["key_next"])
        grp_box.addWidget(QLabel("下一行:"), 2, 1); grp_box.addWidget(self.inp_next, 2, 2)
        self.inp_prev = HotkeyLineEdit(self.cfg.config["key_prev"])
        grp_box.addWidget(QLabel("上一行:"), 2, 3); grp_box.addWidget(self.inp_prev, 2, 4)
        self.inp_boss = HotkeyLineEdit(self.cfg.config["key_boss"])
        grp_box.addWidget(QLabel("老板键(隐):"), 3, 1); grp_box.addWidget(self.inp_boss, 3, 2)
        self.inp_wake = HotkeyLineEdit(self.cfg.config["key_wake"])
        grp_box.addWidget(QLabel("唤醒键(显):"), 3, 3); grp_box.addWidget(self.inp_wake, 3, 4)
        
        btn_layout = QHBoxLayout()
        btn_apply = QPushButton("应用全部设置"); btn_apply.clicked.connect(self.apply_settings)
        btn_reset = QPushButton("重置默认按键"); btn_reset.clicked.connect(self.reset_default_keys)
        btn_layout.addWidget(btn_apply); btn_layout.addWidget(btn_reset)
        grp_box.addLayout(btn_layout, 4, 0, 1, 5) 
        
        main_layout.addLayout(grp_box)
        main_layout.addWidget(QLabel("书架 (数据已保存至系统，删除软件不丢失):"))
        self.list_books = QListWidget()
        self.list_books.itemDoubleClicked.connect(lambda item: (self.reader.load_book(item.text()), self.lbl_status.setText(f"当前: {os.path.basename(item.text())}"), self.start_reading()))
        self.refresh_books()
        main_layout.addWidget(self.list_books)
        main_layout.addWidget(QLabel("提示: 点击右上角X会自动隐藏到系统托盘(右下角图标)。"))

        # --- 底部栏 (版本号 + 版权) ---
        bottom_layout = QHBoxLayout()
        
        # 左侧：版本号
        lbl_ver = QLabel(CURRENT_VERSION)
        lbl_ver.setStyleSheet("color: #aaaaaa; font-family: Arial; font-size: 11px;")
        bottom_layout.addWidget(lbl_ver)
        
        bottom_layout.addStretch() # 弹簧
        
        # 右侧：版权按钮
        btn_copy = QPushButton("© Oxygen Reader 访问官网")
        btn_copy.setCursor(Qt.PointingHandCursor)
        btn_copy.setStyleSheet("QPushButton { border: none; color: gray; } QPushButton:hover { color: #0078d7; text-decoration: underline; }")
        btn_copy.clicked.connect(lambda: webbrowser.open(OFFICIAL_SITE))
        bottom_layout.addWidget(btn_copy)
        
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

    def start_hooks(self):
        self.mouse_listener = mouse.Listener(on_click=lambda x,y,b,p: self.comm.hide_signal.emit() if (p and b==mouse.Button.left and self.reader.isVisible()) else None)
        self.mouse_listener.start()
        self.bind_keys(silent=True)

    def bind_keys(self, silent=False):
        keyboard.unhook_all()
        c = self.cfg.config
        try:
            keyboard.add_hotkey(c["key_next"], lambda: self.comm.next_signal.emit() if self.reader.isVisible() else keyboard.send(c["key_next"]))
            keyboard.add_hotkey(c["key_prev"], lambda: self.comm.prev_signal.emit() if self.reader.isVisible() else keyboard.send(c["key_prev"]))
            keyboard.add_hotkey(c["key_boss"], self.comm.hide_signal.emit)
            keyboard.add_hotkey(c["key_wake"], self.comm.show_signal.emit)
            if not silent: QMessageBox.information(self, "成功", "快捷键已生效！")
        except Exception as e:
            if not silent: QMessageBox.warning(self, "错误", f"快捷键冲突或格式错误: {e}")

    def reset_default_keys(self):
        self.inp_next.setText("t"); self.inp_prev.setText("q"); self.inp_boss.setText("ctrl+shift+q"); self.inp_wake.setText("ctrl+shift+f")
        self.apply_settings(); QMessageBox.information(self, "提示", "快捷键已重置为默认设置！")

    def toggle_focus(self, checked):
        self.cfg.config["focus_anchor"] = checked
        self.cfg.save()

    def pick_color(self, key):
        col = QColorDialog.getColor()
        if col.isValid():
            if key == "bg_color":
                reply = QMessageBox.question(self, "背景", "是否设为完全透明?", QMessageBox.Yes | QMessageBox.No)
                self.cfg.config[key] = "#00000000" if reply == QMessageBox.Yes else col.name()
            else: self.cfg.config[key] = col.name()
            self.cfg.save(); self.comm.update_style_signal.emit()

    def save_appearance(self):
        self.cfg.config["font_size"] = self.spin_font.value(); self.cfg.save(); self.comm.update_style_signal.emit()

    def apply_settings(self):
        c = self.cfg.config
        c["key_next"] = self.inp_next.text(); c["key_prev"] = self.inp_prev.text()
        c["key_boss"] = self.inp_boss.text(); c["key_wake"] = self.inp_wake.text()
        new_title = self.inp_title.text()
        if new_title: c["window_title"] = new_title; self.setWindowTitle(new_title)
        self.cfg.save(); self.bind_keys()

    def import_book(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择", "", "Files (*.txt *.pdf *.epub *.mobi *.azw3)")
        if path: self.reader.load_book(path); self.lbl_status.setText(f"当前: {os.path.basename(path)}"); self.refresh_books()

    def start_reading(self):
        if self.reader.current_file:
            self.reader.reset_focus()
            self.reader.show_line() 
            if self.cfg.config.get("focus_anchor", True):
                self.reader.adjustSize() 
                screen = QDesktopWidget().screenGeometry()
                size = self.reader.geometry()
                new_x = (screen.width() - size.width()) // 2
                new_y = (screen.height() - size.height()) // 2
                self.reader.move(new_x, new_y)
            else:
                self.reader.move(200, 200) 

            self.reader.show()
            self.reader.activateWindow()
            self.hide() 
            self.tray_icon.showMessage("Oxygen Reader", "控制台已隐藏，文字已居中显示。", QSystemTrayIcon.Information, 2000)
        else: QMessageBox.information(self, "提示", "请先导入书籍")
    
    def refresh_books(self):
        self.list_books.clear()
        [self.list_books.addItem(k) for k in self.bookshelf.get_recent_books()]
    
    def check_update(self):
        self.lbl_status.setText("Checking...")
        self.u = UpdateWorker()
        self.u.result_signal.connect(lambda h,v,l: UpdateDialog(v,l).exec_() if h else QMessageBox.information(self,"提示","已是最新") if v!="Error" else QMessageBox.warning(self,"Err",l))
        self.u.start()

    def closeEvent(self, e):
        if self.tray_icon.isVisible(): self.hide(); e.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    panel = ControlPanel()
    panel.show()
    sys.exit(app.exec_())