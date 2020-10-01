#本文件定义识别验证码可能用到的常量

from enum import Enum

#定义数字，大写字母，小写字母
NUMBER = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
ALPHABET_upper = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
ALPHABET_lower = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
#可能字符总数
Total_num=62


# 图像大小
IMAGE_HEIGHT = 48
IMAGE_WIDTH = 120

#验证码字符数
Cnum=4



class SR(Enum):  # 声音提醒
    NONE = 0
    ANYTIME = 1
    APPROPRIATE = 2


class LM(Enum):  # 登录方式
    PORTAL = 0
    ELECTIVE = 1


class IM(Enum):  # ICR识别方式
    CNN = 0
    OCR = 1


class ERROR(Enum):  # 错误信息
    EMAIL_ERROR = 0
    DRIVER_ERROR = 1
    INTERNET_ERROR = 2
    REFRESH_ERROR = 3
    VALID_CODE_ERROR = 4
    PASSWORD_ERROR = 5


class STATE(Enum):  # 运行状态
    LOADING = 0
    INITIALIZING = 1
    CONNECTING = 2
    LOGINING=3
    JUMPING=4
    EXAMINING = 5
    REFRESHING = 6
    SNATCHING = 7
    ERROR = 8
    RESTARTING = 9
    STOPPED = 10

class DRIVER(Enum): #驱动选择
    CHROME = 0
    EDGE = 1
    FIREFOX = 2
    IE = 3

