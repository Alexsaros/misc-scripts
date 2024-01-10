import pyautogui
import time
import numpy as np


def LowLevelMouseProc(nCode, wParam, lParam):
    Source = ctypes.c_void_p(lParam)
    ctypes.windll.kernel32.RtlMoveMemory(ctypes.addressof(mll_hook.m_struct), lParam, ctypes.sizeof(mll_hook.m_struct))

    if wParam == win32con.WM_LBUTTONDOWN:
        if mll_hook.m_struct.flags and win32con.LLMHF_INJECTED:
            print("[+] Artificial mouse event detected.")
            mll_hook.m_struct.flags = 0

    return CallNextHookEx(mll_hook.hook, nCode, wParam, lParam)
