#本文件用于预处理验证码图片，包括降噪，上采样与样本筛选

import os
import glob
import pytesseract
import numpy as np
import random
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
from cnn import CNN
from alive_progress import alive_bar
from transfer import encode,decode



PATH = os.path.dirname(__file__)
target_path="c:/train/test"#待降噪目录
save_path="c:/train/testset"#降噪目标目录
sift_path="c:/train/grab"#过滤目录
train_path="c:/train/grab"#提取目录
test_path="c:/train/test"#提取目标目录



choice='denoise'#运行模式
error_count=0#受损文件数
extract_scale=3000#随机提取规模




class ICR():
    '''Intelligent Character Recognition'''

    def __init__(self,image_name,threshold=160,mode='bilinear'):
        super(ICR, self).__init__()
        self.threshold=threshold#灰度阈值
        self.image_name=image_name
        self.mode=mode

    def toNumpy(self):
        table = []
        for i in range(256):
            if i < self.threshold:
                table.append(0)
            else:
                table.append(1)
        image = Image.open(self.image_name).convert('L')#转化为灰度图
        image = image.point(table,'1')#二值化
        image=np.array(image)
        return image

    def denoising(self,image_array):

        h,w=image_array.shape

        padding=nn.ConstantPad2d(padding=(1, 1, 1, 1),value=1)
        image_array=(padding(torch.from_numpy(image_array))).numpy()

        for time in range(1):
            for i in range(1,h+1):
                for j in range(1,w+1):
                    if not image_array[i][j]:
                        count=0
                        for dh in range(-1,2):
                            for dw in range(-1,2):
                                if image_array[i+dh][j+dw]:count+=1
                    
                        if count>=6: image_array[i][j]=True#邻域去噪
            for i in range(h,0):
                for j in range(1,w+1):
                    if not image_array[i][j]:
                        count=0
                        for dh in range(-1,2):
                            for dw in range(-1,2):
                                if image_array[i+dh][j+dw]:count+=1
                    
                        if count>=6: image_array[i][j]=True#邻域去噪

                        
                        


            
                    
                        
        for time in range(1):
            for i in range(1,h+1):
                for j in range(1,w+1):
                    if not image_array[i][j]:
                        count=0
                        for dh in range(-1,2):
                            for dw in range(-1,2):
                                if image_array[i+dh][j+dw]:count+=1

                        #精细去噪
                        if not image_array[i-1][j+1] and not image_array[i][j+1] and  not image_array[i+1][j+1]:
                            if count>=5:image_array[i][j]=True
                            elif count==4 and not image_array[i+1][j]:
                                count1=0
                                for ddh in range(-1,2):
                                    for ddw in range(-1,2):
                                        if image_array[i+1+ddh][j+ddw]:count1+=1
                                if count1==4:
                                    image_array[i][j]=True
                                    image_array[i+1][j]=True
                        if not image_array[i-1][j-1] and not image_array[i][j-1] and  not image_array[i+1][j-1]:
                            if count>=5:image_array[i][j]=True
                            elif count==4 and not image_array[i+1][j]:
                                count1=0
                                for ddh in range(-1,2):
                                    for ddw in range(-1,2):
                                        if image_array[i+1+ddh][j+ddw]:count1+=1
                                if count1==4:
                                    image_array[i][j]=True
                                    image_array[i+1][j]=True
                        if not image_array[i-1][j-1] and not image_array[i-1][j] and  not image_array[i-1][j+1]:
                            if count>=5:image_array[i][j]=True
                            elif count==4 and not image_array[i][j+1]:
                                count1=0
                                for ddh in range(-1,2):
                                    for ddw in range(-1,2):
                                        if image_array[i+ddh][j+1+ddw]:count1+=1
                                if count1==4:
                                    image_array[i][j]=True
                                    image_array[i][j+1]=True
                        if not image_array[i+1][j-1] and not image_array[i+1][j] and  not image_array[i+1][j+1]:
                            if count>=5:image_array[i][j]=True
                            elif count==4 and not image_array[i][j+1]:
                                count1=0
                                for ddh in range(-1,2):
                                    for ddw in range(-1,2):
                                        if image_array[i+ddh][j+1+ddw]:count1+=1
                                if count1==4:
                                    image_array[i][j]=True
                                    image_array[i][j+1]=True
                        

        return image_array

    def upsample(self,save=False):
        image=Image.fromarray(self.denoising(self.toNumpy()))

        up=nn.Upsample(scale_factor=2, mode=self.mode)#pytorch上采样方法

        toTensor = transforms.ToTensor()
        image=up(toTensor(image).unsqueeze(0))
        toPIL = transforms.ToPILImage()
        image = toPIL(image.squeeze(0))

        if save:
            name=self.image_name.split('\\')[-1].split('.')[0]
            image.save(save_path+'/'+name+'.jpg')

        return image


    def toText(self):
        '''ocr方式'''
        content = pytesseract.image_to_string(self.upsample())   # 使用tesseractOCR解析图片
        return content#返回字符串


    def ToText(self):
        '''cnn方式'''
        toTensor = transforms.ToTensor()
        image = toTensor(self.upsample()).unsqueeze(0)
        cnn=CNN(test=True).eval()
        cnn.load_state_dict(torch.load(os.path.join(PATH,'model/newcnn10.pth'),map_location=torch.device('cpu')))
        content=decode(cnn(image))
        return content  # 返回字符串






def denoise():#图片预处理（降噪&上采样）
    global error_count
    paths = glob.glob(target_path+'/*.jpg')
    print('Start denoising...')
    with alive_bar(len(paths)) as bar:
        for path in paths:
            bar()
            icr=ICR(path)
            try:icr.upsample(save=True)
            except:
                error_count+=1
                os.remove(path)

    print('Completed.')
    print(f"errors: {error_count}")

def mark():#自动标注
    paths = glob.glob(save_path+'/*.jpg')
    print('Start marking...')
    with alive_bar(len(paths)) as bar:
        for path in paths:
            bar()
            image = Image.open(path)
            name=pytesseract.image_to_string(image)
            newpath=save_path+'/'+name+'.jpg'

            try:os.rename(path,newpath)#重命名
            except: os.remove(path)#重复文件删除

    print('Completed.')


def common(x):
    if x.isdigit():return True
    if 'a'<=x<='z' or 'A'<=x<='Z':return True
    return False

def sift():#过滤器（错误图片处理）
    print('Start sifting...')
    error_list=[]
    v_list=[]
    paths=glob.glob(sift_path+'/*.jpg')
    print("analyzing images...")
    with alive_bar(len(paths)) as bar:
        for path in paths:
            bar()
            name=path.split('\\')[-1].split('.')[0]
            if len(name)!=4:
                error_list.append(path)
                continue
            if 'v' in name and not 'V' in name and list(name).count('v')==1:v_list.append(path)
            for n in list(name):
                if not common(n):
                    error_list.append(path)
                    break

            
    V_count=0
    print("Special character processing...")
    with alive_bar(len(v_list)) as bar:
        for path in v_list:
            bar()
            icr=ICR(path,mode='nearest')
            content=icr.toText()
            name=path.split('\\')[-1].split('.')[0]
            if 'V' in content : 
                V_count+=1
                name=name.replace('v','V')
                newpath=sift_path+'/'+name+'.jpg'
                os.rename(path,newpath)
    print(f"imgs with error v: {V_count}")



    print('error_list:',error_list)
    print('removing error pics...')
    for path in error_list:
        os.remove(path)
    print('Completed.')



def extract():#从训练集中随机提取构成验证集/测试集
    print('Start extracting...')
    paths= glob.glob(train_path+'/*.jpg')
    with alive_bar(extract_scale) as bar:
        for _ in range(extract_scale):
            path=random.choice(paths)
            name=path.split('\\')[-1].split('.')[0]
            newpath=test_path+'/'+name+'.jpg'
            os.rename(path,newpath)
            paths.remove(path)
    print('Completed.')





if __name__ == "__main__":
    if choice=='denoise':denoise()
    elif choice=='mark':mark()
    elif choice=='sift':sift()
    elif choice=='extract':extract()