#本文件通过对登录网站进行连续的错误表单请求来获得验证码示例，并利用网站反馈构造标签数据集

import re
import os
import sys
import time
import random
import requests
import argparse
import selenium

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select#选择框处理
from selenium.webdriver.common.action_chains import ActionChains#精细动作
from selenium.webdriver.common.keys import Keys

from datetime import datetime
from PIL import Image
from pretreatment import ICR


from pykeyboard import PyKeyboard#键盘操作
from alive_progress import alive_bar


PATH = os.path.dirname(__file__)

save_path="c:\\train\\grab\\"#图片存储地址

browser = Chrome("D://ChromeDriver//chromedriver.exe")
browser.implicitly_wait(10)
#browser.maximize_window()#窗口最大化


grab_count=0
iters=10000
save_count=0


def getimg1():
    '''模拟键盘操作进行图片下载'''
    global grab_count,save_path
    k = PyKeyboard()
    img=browser.find_element_by_id('code_img')#找到验证码元素
    ac = ActionChains(browser)
    ac.move_to_element(img).perform
    time.sleep(0.5)
    ac.context_click(img).perform()

    k.press_key(k.shift_key)
    k.tap_key('v')
    k.release_key(k.shift_key)
    
    time.sleep(1)
    k.tap_key(k.backspace_key)
    path=list(save_path)
    for key in path:
        k.tap_key(key)
    name=list(str(grab_count))
    for n in name:
        k.tap_key(n)

    tail=list(".jpg")
    for key in tail:
        k.tap_key(key)

    k.tap_key(k.enter_key)
    k.tap_key(k.enter_key)
    time.sleep(1)
    grab_count+=1

    return


def getimg2():
    '''通过截屏获取图片'''
    #browser.maximize_window()#窗口最大化
    browser.save_screenshot(os.path.join(PATH,'pics/p.png')) 
    img=browser.find_element_by_id('code_img')#找到验证码元素
    location=img.location
    size = img.size 
    area = (int(location['x']), int(location['y']), int(location['x'] + size['width']),int(location['y'] + size['height']))
    pic=Image.open(os.path.join(PATH,'pics/p.png'))
    #frame = pic.crop((1316,405,1432,449))  
    frame = pic.crop((1004,405,1120,449))  
    frame.save(os.path.join(PATH,'pics/save.png'))

def main():
    global grab_count
    global save_count
    print('尝试连接服务器...\n')
    browser.get("https://portal.pku.edu.cn/")

    login_button=browser.find_element_by_link_text("请登录")
    login_button.click()


    print("尝试触发验证码...")
    for i in range(3):
        usernameinput=browser.find_element_by_id("user_name")
        passwordinput=browser.find_element_by_id("password")
        usernameinput.clear()
        passwordinput.clear()
        test=str(random.randint(1000000000,2000000000))
        usernameinput.send_keys(test)
        passwordinput.send_keys('12345678\n')

    print('触发成功')


    codeinput=browser.find_element_by_id('valid_code')
    with alive_bar(iters) as bar:
        for _ in range(iters):
            bar()
            codeinput.clear()
            getimg1()
            path=save_path+str(grab_count-1)+'.jpg'
            icr=ICR(path)
            error_count=0
            while(True):
                try:
                    content=icr.ToText()
                    break
                except: 
                    time.sleep(0.5)
                    error_count+=1
                    if error_count==10:break

            if error_count==10:continue

            content=icr.ToText()
            if not content: content='z'
            codeinput.send_keys(content+'\n')
            time.sleep(0.1)
            msg=browser.find_element_by_id('msg')
            #print(msg.text)
            if '验证码错误' in msg.text:
                os.remove(path)
                continue
            else:
                newpath=save_path+content+'.jpg'
                try:
                    os.rename(path,newpath)#重命名
                    save_count+=1
                except: os.remove(path)#重复文件删除


    print(f"Completed. \n共尝试了{grab_count}次，存储了{save_count}张有效验证码图片")
    browser.close()


if __name__ == "__main__":
    main()