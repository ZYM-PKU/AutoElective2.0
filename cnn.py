#本文件定义验证码识别使用的卷积神经网络模型  

import constant
import torch.nn as nn

class CNN(nn.Module):
    def __init__(self,test=False):
        super(CNN,self).__init__()

        self.layer1 = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=5, padding=2),
            nn.Conv2d(32, 32, kernel_size=5, padding=2),
            nn.BatchNorm2d(32),
            nn.Dropout(0.2),  # drop 50% of the neuron
            nn.ReLU(),
            nn.MaxPool2d(2))
        self.layer2 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.Dropout(0.2),  # drop 50% of the neuron
            nn.ReLU(),
            nn.MaxPool2d(2))
        self.layer3 = nn.Sequential(
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.Dropout(0.2),  # drop 50% of the neuron
            nn.ReLU(),
            nn.MaxPool2d(2))
        self.fc1 = nn.Sequential(
            nn.Linear((constant.IMAGE_WIDTH//8)*(constant.IMAGE_HEIGHT//8)*64, 2048),
            nn.Dropout(0.2),  # drop 50% of the neuron
            nn.ReLU())
        self.fc2 = nn.Sequential(
            nn.Linear(2048, 1024),
            nn.ReLU()
        )
        self.fc3 = nn.Sequential(
            nn.Linear(1024, constant.Cnum*constant.Total_num),
        )

        if test: #测试情形
            for param in self.parameters():
                param.requires_grad = False#测试时对decoder不进行梯度下降，防止显存爆炸


    def forward(self, x):
        x=x.permute(0,1,3,2)#图片翻转，使字符位置与向量匹配
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = x.view(x.size(0), -1)#提取长向量
        x = self.fc1(x)
        x = self.fc2(x)
        x = self.fc3(x)

        return x