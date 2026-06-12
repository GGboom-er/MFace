# coding:utf-8
import traceback
import sys

try:
    import maya.cmds as cmds
    from maya.api.OpenMaya import MGlobal
    _IS_MAYA = True
except ImportError:
    _IS_MAYA = False

# ---------- PySide 兼容导入 ----------
try:
    from PySide6.QtWidgets import QLabel
    from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
    from PySide6.QtGui import QFont
except ImportError:
    try:
        from PySide2.QtWidgets import QLabel
        from PySide2.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
        from PySide2.QtGui import QFont
    except ImportError:
        QLabel = None


# ---------- QLabel 浮窗 HUD ----------
class _HudOverlay(QLabel):
    """半透明淡出的视口浮窗提示，替代 cmds.inViewMessage。"""

    _STAY_MS = 2000   # 停留时长（毫秒）
    _FADE_MS = 1000   # 淡出时长（毫秒）

    def __init__(self, msg, color="#00FF00"):
        if QLabel is None:
            return
        # 获取 Maya 主窗口作为 parent，确保浮窗在 Maya 窗口层级内
        import maya.OpenMayaUI as omui
        try:
            from shiboken6 import wrapInstance
        except ImportError:
            from shiboken2 import wrapInstance
        from PySide6.QtWidgets import QWidget
        maya_win = wrapInstance(int(omui.MQtUtil.mainWindow()), QWidget)

        super().__init__(maya_win)

        # ---- 窗口属性 ----
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        # ---- 样式 ----
        html = msg.replace("\n", "<br>")
        self.setText(
            '<div style="'
            'background: rgba(0,0,0,90); '
            'border-radius: 12px; '
            'padding: 16px 28px; '
            'text-align: center;'
            '">'
            '<span style="color:{color}; font-size:18px; '
            'font-family: Segoe UI, Microsoft YaHei, sans-serif;">'
            '{html}</span></div>'.format(color=color, html=html)
        )
        self.setFont(QFont("Segoe UI", 18))
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background: transparent;")

        # ---- 淡出定时器 ----
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._start_fade)

    def popup(self):
        """计算位置并显示。"""
        if QLabel is None:
            return
        self.adjustSize()
        # 尝试定位到活动 modelPanel 中央，否则用 Maya 主窗口中央
        rect = self._get_viewport_rect()
        x = rect[0] + (rect[2] - self.width()) // 2
        y = rect[1] + (rect[3] - self.height()) // 2
        self.move(x, y)
        self.setWindowOpacity(1.0)
        self.show()
        self._timer.start(self._STAY_MS)

    def _get_viewport_rect(self):
        """获取活动 3D viewport 的屏幕矩形，返回 (x, y, w, h)。"""
        import maya.OpenMayaUI as omui
        try:
            from shiboken6 import wrapInstance
        except ImportError:
            from shiboken2 import wrapInstance
        from PySide6.QtWidgets import QWidget
        try:
            panel = cmds.getPanel(wf=True)
            if cmds.getPanel(to=panel) == "modelPanel":
                ptr = omui.MQtUtil.findControl(panel)
                if ptr:
                    widget = wrapInstance(int(ptr), QWidget)
                    tl = widget.mapToGlobal(widget.rect().topLeft())
                    return (tl.x(), tl.y(), widget.width(), widget.height())
        except Exception:
            pass
        # fallback: Maya 主窗口
        ptr = omui.MQtUtil.mainWindow()
        widget = wrapInstance(int(ptr), QWidget)
        tl = widget.mapToGlobal(widget.rect().topLeft())
        return (tl.x(), tl.y(), widget.width(), widget.height())

    def _start_fade(self):
        """启动淡出动画。"""
        self._anim = QPropertyAnimation(self, b"windowOpacity")
        self._anim.setDuration(self._FADE_MS)
        self._anim.setStartValue(1.0)
        self._anim.setEndValue(0.0)
        self._anim.setEasingCurve(QEasingCurve.OutQuad)
        self._anim.finished.connect(self._on_fade_done)
        self._anim.start()

    def _on_fade_done(self):
        """动画结束后销毁。"""
        self.close()
        self.deleteLater()


class MFaceLogger(object):
    """
    中央日志与通知中心，统管所有 UI 样式弹窗、底栏警告和后台调试。
    """
    DEBUG_MODE = True

    @classmethod
    def info(cls, msg, in_view=False):
        """
        普通信息或成功提示
        :param msg: 信息内容
        :param in_view: 是否在屏幕中央浮现文字 (HUD)
        """
        if _IS_MAYA:
            if in_view:
                cmds.inViewMessage(msg=msg, pos='midCenter', fade=True, fadeStayTime=1500)
            else:
                MGlobal.displayInfo("[MFace2 INFO] " + str(msg))
        else:
            print("[MFace2 INFO] " + str(msg))

    @classmethod
    def warning(cls, msg):
        """温和警告（右下角黄字）"""
        if _IS_MAYA:
            cmds.warning("[MFace2] " + str(msg))
        else:
            print("[MFace2 WARNING] " + str(msg))

    @classmethod
    def debug(cls, msg, *args):
        """调试日志；DEBUG_MODE 关闭时静默。"""
        if not cls.DEBUG_MODE:
            return
        if args:
            try:
                msg = msg % args
            except Exception:
                msg = "{} {}".format(msg, args)
        if _IS_MAYA:
            MGlobal.displayInfo("[MFace2 DEBUG] " + str(msg))
        else:
            print("[MFace2 DEBUG] " + str(msg))

    @classmethod
    def error(cls, msg, exc=None):
        """报错与拦截（红字或完整栈追踪）"""
        err_msg = "[MFace2 ERROR] " + str(msg)
        if exc:
            err_msg += "\n" + traceback.format_exc()
            
        if _IS_MAYA:
            MGlobal.displayError(err_msg)
        else:
            sys.stderr.write(err_msg + "\n")

    @classmethod
    def catch_all(cls, msg="捕获到隐蔽级别故障", default_return=None):
        """
        一个超级装饰器，用来替代所有暴力的裸捕获
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    cls.error("%s: %s" % (msg, str(e)), exc=e)
                    return default_return
            return wrapper
        return decorator

    # ====== 视口 HUD 提示（QLabel 浮窗，替代 cmds.inViewMessage）======
    _hud_overlay = None  # 当前活跃的浮窗实例（避免堆叠）

    @classmethod
    def hud(cls, msg, color="#00FF00"):
        """
        在 Maya 视口正中央显示半透明淡出的富文本提示（QLabel 浮窗）。
        :param msg: 提示文字，支持 \\n 换行
        :param color: 十六进制颜色，默认成功绿，警告用 #FFFF00，错误用 #FF0000
        """
        if not _IS_MAYA:
            print("[MFace2 HUD] " + str(msg))
            return
        # 关闭上一条（不堆叠）
        if cls._hud_overlay is not None:
            try:
                cls._hud_overlay.close()
                cls._hud_overlay.deleteLater()
            except RuntimeError:
                pass
            cls._hud_overlay = None

        overlay = _HudOverlay(msg, color)
        cls._hud_overlay = overlay
        overlay.popup()

    @classmethod
    def confirm(cls, title, message, accept=u"确认", cancel=u"取消"):
        """
        统一弹窗确认（替代散落的 cmds.confirmDialog / QMessageBox）。
        :return: True 如果用户点了接受按钮，否则 False
        """
        if _IS_MAYA:
            res = cmds.confirmDialog(
                title=title, message=message,
                button=[accept, cancel],
                defaultButton=accept,
                cancelButton=cancel,
                dismissString=cancel
            )
            return res == accept
        return True

class MSG:
    # --- 按钮与通用交互 ---
    BTN_CONFIRM = u"确认"
    BTN_CANCEL = u"取消"
    TITLE_SYNC_CONFIRM = u"极值同步确认"

    # --- 绑定与工具 ---
    CLUSTER_EDIT_START = u"开始修改: %s"
    CLUSTER_EDIT_FINISH = u"结束修改: %s"
    CLUSTER_EDIT_FINISH_GENERIC = u"结束修改"
    CLUSTER_SELECT_UNIQUE = u"请先在场景中选择唯一一个需要修改的 Cluster 控制器！"
    CLUSTER_MIRROR_SELF = u"%s 自身镜像完成"

    RIG_REBUILD_SUCCESS = u"模块绑定成功！"
    RIG_REBUILD_ERROR = u"模块绑定失败，请检查脚本编辑器错误详情。"
    RIG_TYPE_MISSING = u"未找到 Rig 类型 '%s'（可用: %s）。请执行完整热重载。"
    RIG_CLEANUP_SKIP = u"清理旧组件跳过: %s"
    RIG_CLEANUP_FAIL = u"清理旧组件失败: 记录=%s 类型=%s 名称=%s 原因=%s"
    TOOL_BW_CLEAN_LIST = u"[Cluster 镜像列表]\n\n%s"
    TOOL_MATCH_ROT_DONE = u"已成功将 %d 个控制器的旋转完全匹配并冻结至最后所选: %s"
    TOOL_FOLLOW_DONE = u"已成功绑定控制器跟随！"
    TOOL_ORIENT_HINT = u"请按顺序选择至少两个以上控制器！（系统会将前面选中的所有控制器旋转匹配并冻结至最后一个选中的位目标）"

    # --- FACS 系统 ---
    FACS_COMB_CREATED = u"成功创建组合: %s"
    FACS_IB_CREATED = u"成功插入中间帧: %s"
    FACS_MIRROR_DONE = u"姿势镜像完成！\n%s"
    FACS_FLIP_DONE = u"拷贝翻转完成！%s -> %s"
    FACS_SYNC_DONE = u"[组合: %s] 的下属触发阈值已同步更新！"
    FACS_MOD_DONE = u"[%s] 修改成功"
    FACS_MOD_NO_CHANGE = u"[%s] 修改成功 (极值不变)"
    FACS_TARGET_DELETED = u"所选物体的目标已被删除:\n%s"
    FACS_RESET_ALL = u"全场景所有控制器及修形目标极值已重置归零！"
    FACS_RESET_SEL = u"您所选中的控制器及相关修形极值已被归零！"
    FACS_CANCEL_EDIT = u"已放弃修改，恢复原始模型状态"
    FACS_CANCEL_EDIT_FAIL = u"关闭窗口时取消编辑修形失败: %s"
    FACS_THRESHOLD_UPDATED = u"已将 %s 触发阈值更新为 %.3f"
    FACS_THRESHOLD_HINT = u"[%s] —— 修改至 —— %.3f"
    FACS_DIRECT_INJECT_DONE = u"[%s] —— 所见即所得直接注入成功 (极值不变)"
    FACS_WYSIWYG_EDIT_START = u"[%s] 已创建所见即所得修型模型"
    FACS_WYSIWYG_EDIT_DONE = u"[%s] 修型已写入"
    FACS_WYSIWYG_SINGLE_TARGET = u"Mesh 修型一次只支持一个基础目标"
    FACS_WYSIWYG_UNSUPPORTED_TARGET = u"[%s] 暂不支持 COMB / IB 的 Mesh 修型"
    FACS_WYSIWYG_DRIVER_MISSING = u"[%s] 未找到基础驱动，无法创建 Mesh 修型"
    FACS_WYSIWYG_DRIVER_LOW = u"[%s] 当前驱动值过低，无法按当前状态修型"
    FACS_WYSIWYG_NO_EDIT = u"未找到可提交的所见即所得修型模型"
    FACS_ADD_SDK_FAIL = u"从选择项添加驱动失败: %s"

    # --- 采集与恢复 (RigSnapshot) ---
    SNAP_CAPTURE_ERROR = u"RigSnapshot: 采集 %s 失败: %s"
    SNAP_RESTORE_ERROR = u"RigSnapshot: 恢复 %s 失败: %s"
    SNAP_RESTORE_SKIP = u"RigSnapshot: 恢复跳过 %s: %s"
    PRESET_LOAD_CANCEL = u"加载预设已取消。"

    # --- 校验与提示 ---
    SELECT_TARGET_FIRST = u"请先选择要操作的目标！"
    SELECT_EDGE_FIRST = u"请先选择边(Edge)！"
    SELECT_MESH_FIRST = u"请先选择模型网格！"
    SELECT_CLUSTER_FIRST = u"请先在场景中选择一个需要修改权重的 Cluster 控制器！"
    ZERO_DELTA_ERROR = u"[%s] 差值为0！请先在视窗中推拉该控制器数值，再点击添加。"
    CLEAN_BW_DONE = u"已清除全场景 BlendWeighted 中 %d 个废弃属性。"
    CLEAN_BW_EMPTY = u"全场景的 BW 属性非常干净，无废弃隔离槽位！"
    REFRESH_BW_DONE = u"已成功对全场景 %d 个 blendWeighted 节点进行深度脏数据刷新！"
    REFRESH_BW_EMPTY = u"未找到需要刷新的 Additive 节点。"
    EXPORT_SUCCESS = u"导出成功！"
    IMPORT_SUCCESS = u"导入成功！"

    # --- 错误定位 ---
    NOT_FOUND_TARGET = u"找不到目标: %s"
    NOT_FOUND_INPUT = u"找不到 %s 的输入连接"
    IB_INSERT_FAIL = u"无法插入中间帧"
    IB_VALUE_ERROR = u"无法插入中间帧: 值为 %s"
    BS_EXPORT_EMPTY_WARN = u"未选中任何模型网格，本次导出的 BlendShape 数据将为空。"

logger = MFaceLogger


class MFaceProgress(object):
    """百分比驱动的统一进度条（cmds.progressWindow）。

    用法::

        with MFaceProgress(u"MFace - Eye 绑定") as prog:
            prog.advance(10, u"Eye - 采集控制器")
            do_capture_ctrl()
            prog.advance(30, u"Eye - 采集骨骼偏移")
            do_capture_additive()
    """

    _WIN_WIDTH = 450

    def __init__(self, title):
        self._title = title
        self._pct = 0

    def __enter__(self):
        if _IS_MAYA:
            cmds.progressWindow(
                title=self._title,
                progress=0,
                maxValue=100,
                status=u"准备中...".ljust(50),
                isInterruptable=False,
                minValue=0,
            )
            cmds.refresh()
        return self

    def advance(self, pct, status=""):
        """将进度推进 pct 个百分点（累计不超过 100），并更新状态文字。"""
        self._pct = min(self._pct + pct, 100)
        if _IS_MAYA:
            cmds.progressWindow(
                e=True,
                progress=int(self._pct),
                status=(status or u"处理中...").ljust(50),
            )
            cmds.refresh()

    def set(self, pct, status=""):
        """直接设置到指定百分比。"""
        self._pct = min(pct, 100)
        if _IS_MAYA:
            cmds.progressWindow(
                e=True,
                progress=int(self._pct),
                status=(status or u"处理中...").ljust(50),
            )
            cmds.refresh()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if _IS_MAYA:
            cmds.progressWindow(endProgress=True)
        return False
