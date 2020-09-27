#本文件用于测试模型识别准确度（测试图片已经过预处理）

import os
import time
import glob
import torch
import torch.nn as nn
import torch.optim as optim
import torch.utils.data as data
import torchvision.transforms as transforms

from options import *
from pretreatment import recognize
from alive_progress import alive_bar


PATH = os.path.dirname(__file__)



choice=IM.CNN#识别方式
test_set='c:/train/test'#测试集


def main():

    count=0.0#总数
    correct=0.0#正确识别数
    print('Start testing...')

    paths = glob.glob(test_set+'/*.jpg')
    with alive_bar(len(paths)) as bar:
        for path in paths:
            bar()
            count+=1
            name=path.split('\\')[-1].split('.')[0]
            label=recognize(path,choice)
            if label==name:correct+=1

    print('Accuracy: '+str((correct/count)*100.0)+'%')


if __name__ == "__main__":
    main()