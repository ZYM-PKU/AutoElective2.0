#本文件通过对登录网站进行连续的错误表单请求来获得验证码示例，并利用网站反馈构造标签数据集

import re
import os
import sys
import time
import random
import selenium


from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select#选择框处理
from selenium.webdriver.common.action_chains import ActionChains#精细动作

from options import *
from pretreatment import recognize
from alive_progress import alive_bar


PATH = os.path.dirname(__file__)



browser = Chrome(os.path.join(PATH,'webdriver/chromedriver.exe'))
browser.implicitly_wait(1)


iters=10000#总抓取次数
save_count=0#成功抓取图片数




def main():
    global grab_count,save_count

    print('尝试连接服务器...\n')
    browser.get("https://portal.pku.edu.cn/")

    login_button=browser.find_element_by_link_text("请登录")
    login_button.click()


    print("尝试触发验证码...")
    while True:

        usernameinput=browser.find_element_by_id("user_name")
        passwordinput=browser.find_element_by_id("password")
        usernameinput.clear()
        passwordinput.clear()
        rand=str(random.randint(1000000000,2000000000))
        usernameinput.send_keys(rand)
        passwordinput.send_keys('12345678\n')

        try:
            code_img=browser.find_element_by_id("code_img")
            print('触发成功')
            break
        except:
            continue

    code_img=browser.find_element_by_id("code_img")
    code_input=browser.find_element_by_id('valid_code')

    with alive_bar(iters) as bar:
        for it in range(iters):
            bar()
            code_input.clear()
            save_path=os.path.join(PATH,'dataset/grab/'+str(it)+'.png')
            code_img.screenshot(save_path)

            content=""

            try:
                content=recognize(save_path,method=IM.CNN)
            except: 
                pass

            code_input.send_keys(content+'\n')
            msg=browser.find_element_by_id('msg')

            #print(msg.text)
            if '验证码错误' in msg.text:
                os.remove(save_path)
                continue
            else:
                newpath=os.path.join(PATH,'dataset/grab/'+content+'.png')
                try:
                    os.rename(save_path,newpath)#重命名
                    save_count+=1
                except: os.remove(save_path)#重复文件删除


    print(f"Completed. \n共尝试了{iters}次，存储了{save_count}张有效验证码图片")
    browser.close()


if __name__ == "__main__":
    main()