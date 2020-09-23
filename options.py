#本文件定义枚举

from enum import Enum


class SR(Enum):  # 声音提醒
    NONE = 0
    ANYTIME = 1
    APPROPRIATE = 2


class LM(Enum):  # 登录方式
    PORTAL = 0
    ELECTIVE = 1


class IM(Enum):  # ICR识别方式
    CNN = 0
    TESSERACT = 1


class ERROR(Enum):  # 错误信息
    EMAIL_ERROR = 0
    DRIVER_ERROR = 1
    INTERNET_ERROR = 2
    REFRESH_ERROR = 3
    VALID_CODE_ERROR = 4


class STATE(Enum):  # 运行状态
    LOADING = 0
    INITIALIZING = 1
    CONNECTING = 2
    LOGINING=3
    JUMPING=4
    REFRESHING = 5
    SNATCHING = 6
    ERROR = 7
    RESTARTING = 8
    STOPPED = 9
