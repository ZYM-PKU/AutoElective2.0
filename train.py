#本文件用于训练模型

import os
import time
import glob
import torch
import shelve
import numpy as np
import torch.nn as nn
import torch.optim as optim
import torch.utils.data as data
import torchvision.transforms as transforms
from PIL import Image
from cnn import CNN
from transfer import encode,decode
from alive_progress import alive_bar



train_dir="c:/train/trainset"#训练集
learning_rate=0.001126#学习率
iters=200000#迭代次数
save_dir='model/newcnn10.pth'#模型存储地址          cnn3(loss=0.3),cnn5(loss=0.2),cnn6(loss=0.1)
batch_size=64#打包规模
n_threads=16#处理线程数


PATH = os.path.dirname(__file__)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")#训练设备


def RecurrentSample(n):
    '''循环采样'''
    i = n - 1
    order = np.random.permutation(n)
    while True:
        yield order[i]
        i += 1
        if i >= n:
            np.random.seed()
            order = np.random.permutation(n)
            i = 0


class RecurrentSampler(data.sampler.Sampler):
    '''循环采样器'''
    def __init__(self, data_source):
        self.num_samples = len(data_source)

    def __iter__(self):
        return iter(RecurrentSample(self.num_samples))

    def __len__(self):
        return 2 ** 31


class captcha_Dataset(data.Dataset):
    '''验证码数据集'''
    def __init__(self, root):
        super(captcha_Dataset, self).__init__()
        self.root = root
        self.paths = glob.glob(self.root+'/*.jpg')

    def __getitem__(self, index):
        path = self.paths[index]
        img = Image.open(str(path)).convert('L')
        #img.show()
        toTensor = transforms.ToTensor()
        img=toTensor(img)
        img_name=path.split('\\')[-1].split('.')[0]
        label=encode(img_name)

        return img,label

    def __len__(self):
        return len(self.paths)

    def name(self):
        return 'captcha_Dataset'


def weights_init(m):
    classname = m.__class__.__name__
    if classname.find('Conv2d') != -1:
        nn.init.xavier_normal_(m.weight.data)
        nn.init.constant_(m.bias.data, 0.0)
    elif classname.find('Linear') != -1:
        nn.init.xavier_normal_(m.weight)
        nn.init.constant_(m.bias, 0.0)


def train(dataloader):
    print('Start training...')
    tic=time.time()

    cnn=CNN().to(device)
    cnn.train()
    cnn.apply(weights_init)

    criterion = nn.MultiLabelSoftMarginLoss()
    optimizer = torch.optim.AdamW(cnn.parameters(), lr=learning_rate)

    losslog=open(os.path.join(PATH,'loss/loss.txt'),'a')#存储损失
    loss_list=[]


    with alive_bar(iters) as bar:
        for epoch in range(iters):
            bar()
            img,labels = next(dataloader)
            img=img.to(device)
            labels=labels.to(device)


            predicted_labels=cnn(img)

            loss = criterion(predicted_labels.double(), labels.double())
            loss_list.append(loss.item())

            if (epoch+1)%(iters/100)==0: 
                losslog.write('loss at iter '+str(epoch+1)+':   '+str(loss.item())+'\n')

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()


    torch.save(cnn.state_dict(), os.path.join(PATH,save_dir))
    losslog.close()
    with shelve.open(os.path.join(PATH,"loss/lossdata")) as d:
        d['loss']=loss_list
        d['iter']=list(range(iters))

    print("model saved.")


def main():

    #定义数据加载器
    dataset = captcha_Dataset(root=train_dir)

    #dataloader = data.DataLoader(dataset, batch_size=1,shuffle=True, num_workers=0,pin_memory=True)
    dataloader = iter(data.DataLoader( dataset, batch_size=batch_size,sampler=RecurrentSampler(dataset), \
        num_workers=n_threads,pin_memory=True))

    train(dataloader)


if __name__ == "__main__":
    main()
