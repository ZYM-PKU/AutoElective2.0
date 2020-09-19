#本文件用于测试模型识别准确度（测试图片已经过预处理）

import os
import time
import glob
import torch
import torch.nn as nn
import torch.optim as optim
import torch.utils.data as data
import torchvision.transforms as transforms
from PIL import Image
from cnn import CNN
from transfer import encode,decode
from alive_progress import alive_bar
import pytesseract


PATH = os.path.dirname(__file__)
model_path='model/newcnn10.pth'
test_set='c:/train/testset'


choice='cnn'#识别方式


def main():
    global error_count
    cnn=CNN(test=True).eval()
    cnn.load_state_dict(torch.load(os.path.join(PATH,model_path)))

    paths = glob.glob(test_set+'/*.jpg')
    count=0.0
    correct=0.0
    print('Start testing...')
    with alive_bar(len(paths)) as bar:
        if choice=='cnn':
            for path in paths:
                bar()
                count+=1
                name=path.split('\\')[-1].split('.')[0]
                img = Image.open(path).convert('L')
                toTensor = transforms.ToTensor()
                img=toTensor(img).unsqueeze(0)
                label=decode(cnn(img))

                #print(label+'  '+name)

                if label==name:correct+=1
        elif choice=='ocr':
            for path in paths:
                bar()
                count+=1
                name=path.split('\\')[-1].split('.')[0]
                img = Image.open(path).convert('L')
                label=pytesseract.image_to_string(img)
                
                if label==name:correct+=1

    print('Accuracy: '+str((correct/count)*100.0)+'%')


if __name__ == "__main__":
    main()