#本文件定义字符串与其对应向量的转换方法

import torch
import constant

def encode(text):
    vector = torch.zeros(constant.Cnum*constant.Total_num,dtype=torch.float64)

    def char2pos(c):#找到某个字符对应的分量位置
        
        assert c.isdigit() or c.isalpha()

        if c.isdigit():
            return int(c)
        elif c.isalpha():
            if 'A'<=c and c<='Z':
                return ord(c)-65+10
            elif 'a'<=c and c<='z':
                return ord(c)-97+26+10

    for i, c in enumerate(text):
        idx = i * constant.Total_num + char2pos(c)
        vector[idx] = 1.0#正确字母位置对应的分量为1，其余为0

    return vector


def decode(vector):
    
    result=str()#输出字符串

    for i in range(constant.Cnum):#长向量切片
        slide=vector.squeeze(0)[i*constant.Total_num:(i+1)*constant.Total_num]
        pos=slide.argmax().item()#取最大位置

        assert pos<62

        if pos < 10:
            result=result+str(pos)
        elif pos <36:
            result=result+ chr(pos - 10 + ord('A'))
        elif pos < 62:
            result=result+ chr(pos - 36 + ord('a'))
    return result

