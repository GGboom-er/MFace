# coding:utf-8
import traceback
import sys

try:
    import maya.cmds as cmds
    from maya.api.OpenMaya import MGlobal
    _IS_MAYA = True
except ImportError:
    _IS_MAYA = False


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

    # ====== 视口 HUD 提示（统一替代散落的 cmds.inViewMessage）======
    _HUD_TEMPLATE = u'<span style="color: {color}; font-size: 20px;">{msg}</span>'

    @classmethod
    def hud(cls, msg, color="#00FF00"):
        """
        在 Maya 视口正中央显示一行半透明淡出的富文本提示。
        :param msg: 提示文字，支持 \\n 换行
        :param color: 十六进制颜色，默认成功绿，警告用 #FFFF00，错误用 #FF0000
        """
        if _IS_MAYA:
            amg = cls._HUD_TEMPLATE.format(color=color, msg=msg)
            cmds.inViewMessage(amg=amg, pos='midCenter', fade=True)

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

logger = MFaceLogger
