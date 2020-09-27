#本文件执行为自动选课主程序

#I think there's a fault in my code...

import os
import sys
import time
import ctypes#声音报警提示
import smtplib#发送email



from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select#选择框处理
from selenium.webdriver.common.action_chains import ActionChains#精细动作
from selenium.webdriver import Chrome, Edge,Firefox,Ie,ChromeOptions



from options import *
from threading import Thread
from datetime import datetime
from pretreatment import recognize
from email.mime.text import MIMEText


PATH = os.path.dirname(__file__)



class Electool():
    '''自动选课功能类'''
    def __init__(self,window,targets,studentid,password,driver_choice,driverpath,sound_reminder,email_reminder,login_method,frequency,icr_permitted,icr_method,ms):
        
        self.ms=ms
        self.window=window
        self.targets = targets
        self.studentid = studentid
        self.password = password
        self.driver_choice = driver_choice
        self.driverpath = driverpath
        self.sound_reminder = sound_reminder
        self.email_reminder =email_reminder
        self.login_method = login_method
        self.frequency = frequency
        self.icr_permitted = icr_permitted
        self.icr_method = icr_method
        self.player = ctypes.windll.kernel32

        self.state=STATE.INITIALIZING
        self.closed=False
        self.refresh_speed=0
        self.refresh_count=0
        self.search_table=[]#查找表
        self.examined=False#是否经过首次查找

    

    def run(self):

        self.state=STATE.INITIALIZING
        self.closed=False
        self.refresh_speed=0
        self.refresh_count=1
        self.search_table=[]#查找表
        self.examined=False#是否经过首次查找

        self.pr("##########################")
        self.pr("-------------------------------------------------")
        self.pr("  北京大学学生课程补退选自动刷新提示系统   v2.1.0")
        self.pr("           版本号：v2.1.0")
        self.pr("            开发者：YM-Z")
        self.pr("-------------------------------------------------")
        self.pr("##########################")
        self.pr()
        self.pr("欢迎使用！")
        self.pr()
        self.pr("系统时间："+self.gettime())
        self.pr("系统正在启动，请稍候...\n")

        if self.email_reminder:
            self.emailinit()
        if self.email_reminder:
            self.sendemails('INITIALIZATION','事件提醒：   系统成功启动或重启')
        
        self.main()





    def pr(self,text="\n"):
        '''发送字符串信号'''
        self.ms.print_text.emit(text)

    def pe(self,e):
        '''发送错误信息'''
        self.ms.error_message.emit(e)

    def pm(self,path):
        '''发送图片路径'''
        self.ms.show_image.emit(path)



    #获取系统时间
    def gettime(self):
        dt=datetime.now()
        hour='0'+str(dt.hour) if len(str(dt.hour))==1 else str(dt.hour)
        minute='0'+str(dt.minute) if len(str(dt.minute))==1 else str(dt.minute)
        second='0'+str(dt.second) if len(str(dt.second))==1 else str(dt.second)
        timestr=str(dt.year)+'/'+str(dt.month)+'/'+str(dt.day)+' '+hour+':'+minute+':'+second

        return timestr
     

    def emailinit(self):
        #邮箱信息
        try:
            email_info=[]
            file_name=os.path.join(PATH, "email.txt")
            with open(file_name, mode='r') as file:
                for line in file:
                    email_info.append(line.replace('\n',""))#这里注意去掉换行符
            self.mailserver = email_info[0]  #邮箱服务器地址
            self.username_send = email_info[1]  #邮箱用户名(发件与收件相同)
            self.email_password = email_info[2]   #邮箱密码：需要使用授权码
        except:
            self.email_reminder=False
            self.pe(ERROR.EMAIL_ERROR)
            time.sleep(2)

    #发送邮件提醒
    def sendemails(self,subject,contains):

        try:
            mail = MIMEText('#北京大学学生课程补退选自动刷新提示系统 - v2.1.0# \n'+'系统时间：'+self.gettime()+'\n'+contains)
            mail['Subject'] = subject
            mail['From'] = self.username_send 
            mail['To'] = self.username_send
            smtp = smtplib.SMTP(self.mailserver,port=25) 
            smtp.login(self.username_send,self.email_password) 
            smtp.sendmail(self.username_send,self.username_send,mail.as_string())
            smtp.close()
        except:
            self.email_reminder=False
            self.pe(ERROR.EMAIL_ERROR)
            time.sleep(2)


    def noise(self):
        #声音警报
        tic=time.time()
        self.player.Beep(1000,3000)
        while True:
            player.Beep(1500,1000)#设置声音提醒（频率，持续时长（ms））
            toc=time.time()
            if toc-tic>=30: return


    #报警函数
    def reminder(self,target,occupied,total):
        #email提醒模块
        if self.email_reminder:
            self.sendemails('CATCHED','Member Found!\n'+target+':  '+str(occupied)+'/'+str(total))

        #声音提醒模块(响铃30s)
        if self.sound_reminder==SR.ANYTIME or (self.sound_reminder==SR.APPROPRIATE and datetime.now().hour>=7):
            noise_thread=Thread(target=self.noise)
            noise_thread.setDaemon(True)
            noise_thread.start()


    #连接到服务器
    def connect(self):
        
        self.state=STATE.CONNECTING
        self.pr("尝试连接到服务器...\n")

        URL_1="https://portal.pku.edu.cn/"#门户
        URL_2="https://elective.pku.edu.cn/"#选课网
        

        while True:
            try:
                if self.login_method==LM.PORTAL:
                    self.pr("正在通过门户进入选课系统...")
                    self.browser.get(URL_1)#通过webdriver的get方法直接访问网页

                    #js="Object.defineProperties(navigator,{webdriver:{get:() => false}});"
                    #browser.execute_script(js)

                    login_button=self.browser.find_element_by_link_text("请登录")
                    login_button.click()#2020.8.30 门户网站更新了路由表，该网址将无法直接映射到登录端口，故此处添加一个点击操作
                    
                elif self.login_method==LM.ELECTIVE:
                    self.pr("正在通过选课网进入选课系统...")
                    self.browser.get(URL_2)
 
                self.pr("已链接到端口.")
                return

            except:
                self.pr("[ERROR]*检测到网络错误*   时间："+self.gettime())   
                self.pr("尝试更换登录方式...\n")        
                self.login_method=LM.PORTAL if self.login_method==LM.ELECTIVE else LM.ELECTIVE
                if self.state not in (STATE.RESTARTING,STATE.STOPPED):
                    self.pe(ERROR.INTERNET_ERROR)
                    while True:time.sleep(1)

    #自动登录
    def login(self):

        self.state=STATE.LOGINING
        self.pr("尝试登录...\n")
        while True:
            try:

                self.pr("抓取账户接口...")
                usernameinput=self.browser.find_element_by_id("user_name")
                self.pr("抓取安全接口...")
                passwordinput=self.browser.find_element_by_id("password")

                #自动填写用户信息
                usernameinput.send_keys(self.studentid)#通过webelement的send_keys方法输入字符串
                passwordinput.send_keys(self.password)
                self.pr("身份信息已传入")

                #点击登录按钮
                button = self.browser.find_element_by_id("logon_button")
                button.click()
                self.pr("尝试页面跳转...")

                return
            except:
                if self.state not in (STATE.RESTARTING,STATE.STOPPED):

                    self.pr("[ERROR]*检测到网络延迟*   时间："+self.gettime())

                    self.login_method=LM.PORTAL if self.login_method==LM.ELECTIVE else LM.ELECTIVE
                    self.pe(ERROR.INTERNET_ERROR)
                    while 1:time.sleep(1)


    #进入选课界面
    def jump_to_elective(self):

        self.state=STATE.JUMPING

        while True:
            try:
                #找到选课按钮
                elective_button=self.browser.find_element_by_id("fav_elective")
                self.pr("跳转成功\n")
                elective_button.click()
                self.pr("尝试加载选课页面...\n")

                portal=self.browser.current_window_handle#可以保存当前门户网站，方便切换

                #更新browser
                for handle in self.browser.window_handles:#遍历当前浏览器的所有网页
                    if handle != portal:self.browser.switch_to_window(handle)#切换操作页面
                    if '帮助' in self.browser.title:#找到选课界面
                        return
                    elif '错误' in self.browser.title:
                        if self.state not in (STATE.RESTARTING,STATE.STOPPED):
                            self.pr("载入失败")
                            self.pr("[ERROR]*检测到网络错误*   时间："+self.gettime())
                            self.pr('尝试更换登录方式...\n')

                            self.login_method=LM.ELECTIVE
                            self.pe(ERROR.INTERNET_ERROR)
                            while 1:time.sleep(1)

            except:
                if self.state not in (STATE.RESTARTING,STATE.STOPPED):
                    self.pr("载入失败")
                    self.pr("*检测到网络错误*   时间："+self.gettime())
                    self.pr('尝试更换登录方式...\n')
                    

                    self.login_method=LM.ELECTIVE 
                    self.pe(ERROR.INTERNET_ERROR)
                    while 1:time.sleep(1)


    #进入‘补退选/补选’界面
    def jump_to_by_election(self):
        
        self.state=STATE.JUMPING

        #获取并点击“补退选/补选”按钮
        while True:
            try:
                add_drop_button=self.browser.find_element_by_link_text('补退选')#根据链接标签文本选择元素（只能选择链接）
                self.pr("加载完成\n")
                add_drop_button.click()
                self.pr("尝试进入‘补退选’界面...")

                if self.browser.title=="系统异常":
                    self.pr("失败，尝试进入‘补选’界面...")
                    add_button=self.browser.find_element_by_link_text('补  选')#补选中间有两个空格
                    add_button.click()

                if self.browser.title=="系统异常":
                    if self.state not in (STATE.RESTARTING,STATE.STOPPED):
                        self.pr("\n错误，无法进入补选/补退选界面...")
                        self.pr("[ERROR]*检测到网络错误*   时间："+self.gettime())
                        self.pe(ERROR.INTERNET_ERROR)
                        while 1:time.sleep(1)
                
                return

            except:

                if self.state not in (STATE.RESTARTING,STATE.STOPPED):

                    self.pr("载入失败")
                    self.pr("[ERROR]*检测到网络错误*   时间："+self.gettime())
                    self.pr('尝试更换登录方式...\n')
                    self.login_method=LM.PORTAL if self.login_method==LM.ELECTIVE else LM.ELECTIVE
                    self.pe(ERROR.INTERNET_ERROR)
                    while 1:time.sleep(1)



    #自动抢课（核心代码）
    def snatch(self,status_id,target,class_id):

        if self.state==STATE.SNATCHING:return #多线程堵塞
        self.pr(f"\n已发现{target}  班号：{class_id} 有空余名额！  开始自动抢课...")

        self.state=STATE.SNATCHING
        while True:

            captcha_input=self.browser.find_element_by_xpath("//input[@id='validCode']")#验证码输入框
            captcha_change=self.browser.find_element_by_link_text("换一个")#更换验证码按钮
            

            ###获取验证码
            self.pr("尝试获取验证码...")
            captcha_img=self.browser.find_element_by_id("imgname")#验证码元素

            self.pr(f"Valid Code Image Found:\n{captcha_img.get_attribute('outerHTML')}")
            img_path=os.path.join(PATH,"captcha/valid code.png")

            captcha_img.screenshot(img_path)#调用selenium元素的screenshot方法对验证码图片进行截取
            #2020.09.23：
            #此处不能采取直接下载图片或者打开img的src链接的方式获取该验证码图片，否则会得到另一张验证码图片
            #分析原因为后端服务器有验证码随机生成函数，该函数接收url中的rand参数作为种子构造随机图片，rand与图片无一一对应关系
            #因此，每次以相同的rand向服务器发送GET请求都会得到不同的验证码图片
            #综上，我们采用截图的方式直接获取已经加载到网页前端的验证码

            self.pm(img_path)
            
            ###识别验证码
            self.pr("验证码已获取.   尝试识别...")
            tic=time.time()

            try:
                result=recognize(img_path,self.icr_method)
            except:
                self.pr("验证码图片损毁，正在强制重启...")
                if self.state not in (STATE.RESTARTING,STATE.STOPPED):
                    self.pe(ERROR.VALID_CODE_ERROR)
                    while True:time.sleep(1)

            toc=time.time()
            self.pr(f"Recognize function called.  Time cost: {toc-tic}s\n")
            

            ###填入验证码
            self.window.coderesult.setText(result)     
            captcha_input.send_keys(result)
            self.pr(f"已填入识别结果： {result}")
            
            ###点击补选按钮，确认补选
            status=self.browser.find_element_by_id(status_id)
            row=status.find_element_by_xpath("./../..")#找到目标课程所在列表行
            target=row.find_element_by_xpath("./td/a/span").text#课程名
            add_button=row.find_element_by_xpath("./td[last()]//span")#找到补选按钮
            add_button.click()

            ###读取弹出框信息
            info=self.browser.switch_to.alert.text
            self.pr(f"\nGET RESPONSE:\n{info}\n")

            if "验证码不正确" in info:
                self.pr("验证码识别错误，正在重试...")
                self.browser.switch_to.alert.accept()#点击弹出框的确定
                captcha_change.click()#更换验证码
                continue
            
            self.browser.switch_to.alert.accept()#点击弹出框的确定
            self.examined=False#重新检索其他课程

            ###验证成功信息：
            try:
                message_box=self.browser.find_element_by_xpath("//*[@id='msgTips']/table/tbody/tr/td/table/tbody/tr/td[2]")#查找提示信息
                message=message_box.text
                if "成功" in message:
                    self.pr(f"\n成功补选{target}！\n[INFO]:{message}\n重启监控进程...")
                    if self.email_reminder:
                        self.sendemails('SUCCESS!',f"成功补选{target}！\nINFO:{message}")
                else:
                    self.pr(f"\n补选{target}失败...\n[INFO]:{message}\n重启监控进程...")
                    if self.email_reminder:
                        self.sendemails('FAILED',f"补选{target}失败\nINFO:{message}")
                    self.browser.refresh()
                    return
            except:
                self.pr(f"\n补选{target}失败...  \n重启监控进程...")
                if self.email_reminder:
                    self.sendemails('FAILED',f"补选{target}失败\n[INFO]:{message}")
                self.browser.refresh()
                return

            return


    #检测名额部分（核心代码）
    def examine(self):
        '''第一遍慢查找，确定每个课程对应信息的标签id'''
        
        self.examined=True
        self.pr("\n正在初始化检索课程信息（耗时较长）...\n")
        self.pr("----------------------------------------------------")
        self.search_table=[]
        for target in self.targets:#遍历所有目标课程

            try:
                rows=self.browser.find_elements_by_xpath(f"//span[text()='{target}']/../../..")#找到目标课程所在列表行
                
                for row in rows:

                    class_id=row.find_element_by_xpath("./td[last()-5]/span").text#找到班号

                    status=row.find_element_by_xpath("./td[last()-1]/span")#找到状态栏

                    status_id=status.get_attribute("id")#找到状态栏span标签对应id

                    self.search_table.append((target,class_id,status_id))

                    total,occupied=int(status.text.split('/')[0]),int(status.text.split('/')[1])#解析名额情况

                    self.pr("课程: "+target+"  班号："+class_id+"        目前情况: "+str(total)+"/"+str(occupied)) 
            
            except:
                continue


    def search_one(self,target,class_id,status_id):
        '''查找某一门课的信息'''
        try:

            status=self.browser.find_element_by_id(status_id)

            total,occupied=int(status.text.split('/')[0]),int(status.text.split('/')[1])#解析名额情况

            if self.state!=STATE.SNATCHING:self.pr("课程: "+target+"  班号："+class_id+"        目前情况: "+str(total)+"/"+str(occupied))


            if occupied<total and occupied!=0 :                
                self.reminder(target,occupied,total)#发送通知
                if not self.icr_permitted:time.sleep(60)#阻止过于频繁的邮件提醒
                if self.icr_permitted: 
                    self.snatch(status_id,target,class_id)#抢夺课程
                return#重新加载窗口
                
        except:
            pass


    def search(self):
        '''快速查找课程信息'''
        search_threads=[]#定义查找线程集

        #分发任务，启动多线程查找
        for search_target in self.search_table:
            t=Thread(target=self.search_one,args=search_target)
            search_threads.append(t)
            t.start()
        for t in search_threads:
            t.join()
            


    #循环刷新部分
    def refresh(self):
        
        self.pr("加载完成\n")
        self.pr("开始循环刷新...")
        while True:

            try:
                if "补选" not in self.browser.title:
                    raise Exception("System Error")
                if not self.examined:
                    self.state=STATE.EXAMINING
                    self.examine()#检查   
                    self.pr("----------------------------------------------------")
                    self.pr("\n已开启快速查找.\n")
                else:
                    self.state=STATE.REFRESHING
                    tic=time.time()
                    self.pr(f"------------------课程总数：{len(self.search_table)}------------------")
                    self.search()#查找
                    time.sleep(self.frequency)#刷新延迟
                    toc=time.time()
                    self.refresh_speed=toc-tic     
            except:
                self.pr("[ERROR]*检测到系统错误*   时间："+self.gettime())

                if self.email_reminder: 
                    self.sendemails('ERROR','错误： 检测到刷新过程中的系统异常        \n目前刷新次数：'+str(self.refresh_count)+'\n系统正在尝试重启...')
                if self.state not in (STATE.RESTARTING,STATE.STOPPED):
                    self.pe(ERROR.REFRESH_ERROR)
                    while True:time.sleep(1)
            else:
                self.browser.refresh()#刷新
                self.pr("\n系统时间:  "+self.gettime()+"  刷新次数： "+str(self.refresh_count)+"次\n")
                self.refresh_count+=1
                if self.refresh_count%1000==0 and self.email_reminder:#工作报告
                    self.sendemails('REPORT','例行报告： 系统正常运行中\n目前刷新次数：'+str(self.refresh_count)+"次")



    #主函数
    def main(self):

        try:
            self.pr("调用浏览器驱动...")
            #进入开发者模式，隐藏测试标记
            chrome_options = ChromeOptions()
            prefs = {"": ""}
            prefs["credentials_enable_service"] = False
            prefs["profile.password_manager_enabled"] = False
            chrome_options.add_experimental_option("prefs", prefs) #取消保存密码
            chrome_options.add_experimental_option('useAutomationExtension', False)  # 取消chrome受自动控制提示
            chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])  # 取消chrome受自动控制提示


            if self.driver_choice==DRIVER.CHROME:
                self.browser = Chrome(self.driverpath,options=chrome_options)#生成一个webdriver对象，同时启动浏览器驱动与浏览器本身
            elif self.driver_choice==DRIVER.EDGE:
                self.browser = Edge(self.driverpath)#生成一个webdriver对象，同时启动浏览器驱动与浏览器本身
            elif self.driver_choice==DRIVER.FIREFOX:
                self.browser = Firefox(self.driverpath)#生成一个webdriver对象，同时启动浏览器驱动与浏览器本身
            elif self.driver_choice==DRIVER.IE:
                self.browser = Ie(self.driverpath)#生成一个webdriver对象，同时启动浏览器驱动与浏览器本身

            self.browser.implicitly_wait(10)#隐式等待，每隔半秒查询一次，最多持续10s
            

        except:
            self.pe(ERROR.DRIVER_ERROR)
            while True:time.sleep(1)

        self.connect()

        self.login()

        if self.login_method==LM.PORTAL:
            self.jump_to_elective()

        self.jump_to_by_election()

        self.refresh()