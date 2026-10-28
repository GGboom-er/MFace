# coding:utf-8

class Theme:
    """
    中央样式库：一切尺寸、色彩和组件背景的单点下发池
    """
    # ====== Color Palette ======
    COLOR_BACKGROUND = "#242424"
    COLOR_ACTIVE     = "#79dc7f" # 驱动高亮专属春绿
    COLOR_INACTIVE   = "gray"    # 默认黯淡
    COLOR_SELECTED   = "yellow"  # 单机选定后的边框提亮
    COLOR_DEFAULT_TEXT = "white"

    # ====== Typography ======
    FONT_FAMILY_CN = u"楷体"
    FONT_FAMILY_EN = "Arial"
    
    FONT_SIZE_BASE_PX = 14
    FONT_SIZE_TITLE_PX = 16
    
    # ====== Global QSS Block ======
    # 这就是你那些窗口和弹框的全局底色约束，统一用它，任何分屏比例全盘适配！
    GLOBAL_BOX_QSS = """
    QWidget {
        font-size: 14px;
        font-family: 楷体;
    }
    QGroupBox {
        border: 2px solid #242424;
        font-size: 16px;
        margin-top: 8px;
        padding-top: 4px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top center;
    }
    """
    
    @classmethod
    def apply_fonts(cls, qt_widget):
        """给传进来的 Qt 自定义组件（Label，Line，弹框）一次性贴上标配字体族"""
        try:
            from PySide6.QtGui import QFont
        except Exception:
            try:
                from PySide2.QtGui import QFont
            except Exception:
                from PySide.QtGui import QFont

        ft = QFont(cls.FONT_FAMILY_CN, 12)
        if not ft.exactMatch():
            ft = QFont(cls.FONT_FAMILY_EN, 10)
        qt_widget.setFont(ft)
