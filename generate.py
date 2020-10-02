#本文件利用通用字符集生成随机四位验证码，也可自定义字体生成随机4位标准验证码



import os
import glob
import random
import torchvision.transforms as transforms

from torch import ones,transpose,cat
from alive_progress import alive_bar
from PIL import Image, ImageDraw, ImageFont


PATH = os.path.dirname(__file__)
cpath=os.path.join(PATH,"dataset/characters")#通用字符集



def randomtxt():
    txt_list = []
    txt_list.extend([i for i in range(65,91)])
    txt_list.extend([i for i in range(97,123)])
    txt_list.extend([i for i in range(48,58)])
    return chr(txt_list[random.randint(0, len(txt_list)-1)])
 
 
def generate1():
    width = 120
    height = 48
    #myfont=ImageFont.FreeTypeFont('s8514sys.fon', 30)
    #BitDaylong11(sRB).TTF
    #arial.ttf
    myfont = ImageFont.truetype('arial.ttf', 30)
    

    print('Start generating...')
    with alive_bar(3000) as bar:
        for i in range(3000):
            bar()
            image = Image.new('RGB', (width, height), (255, 255, 255))
            draw = ImageDraw.Draw(image)
            name=str()
            for j in range(4):
                rand=randomtxt()
                draw.text((20*j+17,8), rand, font=myfont, fill=(0,0,0))
                name+=rand
            image.save(os.path.join(PATH,'res1/'+name+'.jpg'))

    print('Completed.')



def generate2():
    paths=glob.glob(cpath+'/*.jpg')
    characters=[]
    names=[]
    toTensor = transforms.ToTensor()
    for path in paths:
        character=Image.open(path).convert('L')
        character=toTensor(character)
        characters.append(character)

        name=path.split('\\')[-1].split('.')[0]
        if len(name)==2:name=name[0].upper()
        names.append(name)
    
    print('Start generating...')
    with alive_bar(3000) as bar:
        for i in range(3000):
            bar()
            mcount=0
            edge=ones(48,12)
            toPIL = transforms.ToPILImage()
            chosen_characters=[]
            chosen_names=str()
            for pos in range(4):
                choice=random.randint(0,len(characters)-1)
                character=characters[choice].squeeze(0)
                name=names[choice]
                if name=='m' or name=='M':
                    mcount+=1
                    edge=ones(48,12-mcount*2)
                else:
                    character=transpose(character,0,1)
                    character=character[:][2:-2]
                    character=transpose(character,0,1)
                chosen_characters.append(character)
                chosen_names+=name
            
            result=cat([edge,chosen_characters[0],chosen_characters[1],chosen_characters[2],chosen_characters[3],edge],dim=1)
            result = toPIL(result)

            result.save(os.path.join(PATH,'res1/'+chosen_names+'.jpg'))
    print('Completed.')



if __name__ == "__main__":
    generate2()
    
