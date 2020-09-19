#本文件执行为自动选课主程序



import os
import sys
import time
import argparse
import selenium
import inspect
import ctypes



from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select#选择框处理
from selenium.webdriver.common.action_chains import ActionChains#精细动作


from datetime import datetime
from options import *

import ctypes#报警提示
import smtplib#发送email
from email.mime.text import MIMEText
from threading import Thread


PATH = os.path.dirname(__file__)

def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")
 
def stop_thread(thread):
    '''to kill a running thread'''
    _async_raise(thread.ident, SystemExit)




class Electool():
    '''自动选课功能类'''
    def __init__(self,window,targets,studentid,password,driverpath,sound_reminder,email_reminder,login_method,frequency,icr_permitted,icr_method,ms):
        self.window=window
        self.targets = targets
        self.studentid = studentid
        self.password = password
        self.driverpath = driverpath
        self.sound_reminder = sound_reminder
        self.email_reminder =email_reminder
        self.login_method = login_method
        self.frequency = frequency
        self.icr_permitted = icr_permitted
        self.icr_method = icr_method
        self.ms=ms
        self.state=STATE.INITIALIZING
        self.player = ctypes.windll.kernel32
        self.closed=False
        self.mainthread=Thread()
        self.control_thread=Thread()
    

    def run(self):
        self.pr("########################################")
        self.pr("----------------------------------------")
        self.pr("  北京大学学生自动刷课提醒系统   v2.1.0")
        self.pr("           版本号：v2.1.0")
        self.pr("            开发者：YM-Z")
        self.pr("----------------------------------------")
        self.pr("########################################")
        self.pr()
        self.pr("欢迎使用！")
        self.pr()
        self.pr("系统时间："+self.gettime())
        self.pr("系统正在启动，请稍候...\n")

        if self.email_reminder:
            self.emailinit()
            self.sendemails('INITIALIZATION','事件提醒：   系统成功启动或重启')
        

        #进程处理

        #主进程
        self.mainthread=Thread(target=self.main)
        self.mainthread.setDaemon(True)
        self.mainthread.start()

        self.control_thread=Thread(target=self.control)
        self.control_thread.setDaemon(True)
        self.control_thread.start()




    def pr(self,text="\n"):
        '''发送字符串信号'''
        self.ms.print_text.emit(text)

    def pe(self,e):
        '''发送错误信息'''
        self.ms.error_message.emit(e)

    def control(self):
        '''控制线程'''
        while(1):
            if self.state==STATE.RESTARTING and  not self.closed:
                self.restart_thread()
                self.state=STATE.INITIALIZING

    #重启进程
    def restart_thread(self):
        self.closed=False
        self.window.infobox.append("\n######当前进程崩溃，尝试重启进程...######")
        self.window.infobox.ensureCursorVisible()
        try:
            stop_thread(self.mainthread)
        except:
            pass

        try:
            self.browser.quit()
            #del self.browser
        except:
            pass
        #del self.mainthread
        
        self.mainthread=Thread(target=self.main)
        self.mainthread.start()
        #python = sys.executable
        #os.execl(python, python, * sys.argv)
    
    #停止进程
    def terminate_thread(self):
        self.state=STATE.STOPPED
        self.closed=True
        self.window.infobox.append("\n######进程已终止.######")
        self.window.infobox.ensureCursorVisible()
        try:
            stop_thread(self.mainthread)
        except:
            pass
        try:
            self.browser.quit()
            #del self.browser
        except:
            pass

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
            self.pe(ERROR.EMAIL_ERROR)

    #发送邮件提醒
    def sendemails(self,subject,contains):
        if self.state==STATE.STOPPED:return#停止刷新，退出进程
        
        mail = MIMEText('#学生补退选自动刷新提示系统 - v2.1.0# \n'+'系统时间：'+self.gettime()+'\n'+contains)
        mail['Subject'] = subject
        mail['From'] = self.username_send 
        mail['To'] = self.username_send
        smtp = smtplib.SMTP(self.mailserver,port=25) 
        smtp.login(self.username_send,self.email_password) 
        smtp.sendmail(self.username_send,self.username_send,mail.as_string())
        smtp.close()
        self.pr ('email sended.')


    #报警函数
    def reminder(self,target,occupied,total):
        #email提醒模块
        if self.email_reminder:
            self.sendemails('SUCCESS','Member Found!        '+target+':  '+str(occupied)+'/'+str(total))

        tic=time.time()
        #声音提醒模块(响铃30s)
        if self.sound_reminder==SR.ANYTIME or (self.sound_reminder==SR.APPROPRIATE and datetime.now().hour>=7):
            self.pr("有机会！")
            self.player.Beep(1000,3000)
            while(True):
                player.Beep(1500,1000)#设置声音提醒（频率，持续时长（ms））
                toc=time.time()
                if toc-tic>=30: return


    #连接到服务器
    def connect(self):
        
        self.state=STATE.CONNECTING
        self.pr("尝试连接到服务器...\n")

        URL_1="https://portal.pku.edu.cn/"
        URL_2="https://elective.pku.edu.cn/"
        #直接进入身份验证系统

        while(True):
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
                self.pr("*检测到网络错误*   时间："+self.gettime())
                self.pr('尝试重新加载...\n')
                

                self.login_method=LM.PORTAL if self.login_method==LM.ELECTIVE else LM.ELECTIVE
                self.state=STATE.RESTARTING
                while(1):time.sleep(1)

    #自动登录
    def login(self):

        self.state=STATE.LOGINING
        self.pr("尝试登录...\n")
        while(True):
            try:
                #获取并点击“登录”按钮
                self.pr("抓取账户接口...")
                #选择网页元素，返回一个WebElement对象
                usernameinput=self.browser.find_element_by_id("user_name")
                #id是一个网页元素相对唯一的属性，通过id选择元素是最常用的方式
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

                    self.pr("*检测到网络延迟*   时间："+self.gettime())
                    self.pr('尝试重新加载...\n')

                    self.login_method=LM.PORTAL if self.login_method==LM.ELECTIVE else LM.ELECTIVE
                    self.state=STATE.RESTARTING
                    while 1:time.sleep(1)


    #进入选课界面
    def jump_to_elective(self):

        time.sleep(1)
        self.state=STATE.JUMPING


        #获取并点击“选课”按钮
        while(True):
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
                            self.pr("*检测到网络错误*   时间："+self.gettime())
                            self.pr('尝试重新加载...\n')

                            self.login_method=LM.PORTAL if self.login_method==LM.ELECTIVE else LM.ELECTIVE
                            self.state=STATE.RESTARTING
                            while 1:time.sleep(1)

            except:
                if self.state not in (STATE.RESTARTING,STATE.STOPPED):
                    self.pr("载入失败")
                    self.pr("*检测到网络错误*   时间："+self.gettime())
                    self.pr('尝试重新加载...\n')
                    

                    if self.login_method==LM.PORTAL: self.login_method=LM.ELECTIVE 
                    self.state=STATE.RESTARTING
                    while 1:time.sleep(1)


    #进入‘补退选/补选’界面
    def jump_to_by_election(self):
        
        self.state=STATE.JUMPING

        #获取并点击“补退选/补选”按钮
        while(True):
            try:
                add_drop_button=self.browser.find_element_by_link_text('补退选')#根据链接标签文本选择元素（只能选择链接）
                self.pr("加载完成\n")
                add_drop_button.click()
                self.pr("尝试跳转...")
                self.pr("尝试进入‘补退选’界面...")
                if self.browser.title=="系统异常":
                    self.pr("失败，尝试进入‘补选’界面...")
                    add_button=self.browser.find_element_by_link_text('补  选')#补选中间有两个空格
                    add_button.click()
                if self.browser.title=="系统异常":
                    if self.state not in (STATE.RESTARTING,STATE.STOPPED):

                        self.pr("\n错误，无法进入补选/补退选界面...")
                        self.pr("*检测到网络错误*   时间："+self.gettime())
                        self.pr('尝试重新加载...\n')

                        self.state=STATE.RESTARTING
                        while 1:time.sleep(1)
                
                return
            except:

                if self.state not in (STATE.RESTARTING,STATE.STOPPED):

                    self.pr("载入失败")
                    self.pr("*检测到网络错误*   时间："+self.gettime())
                    self.pr('尝试重新加载...\n')
                    
                    self.login_method=LM.PORTAL if self.login_method==LM.ELECTIVE else LM.ELECTIVE
                    self.state=STATE.RESTARTING
                    while 1:time.sleep(1)



    #自动抢课（核心代码）
    def snatch(self,target):
        self.state=STATE.SNATCHING

        ######填写验证码######
        pass
        #####################
        
        row=self.browser.find_element_by_xpath("//span[text()='"+target+"']/../../..")#找到目标课程所在列表行
        add_button=row.find_element_by_xpath("./td[last()]//span")#找到补选按钮
        add_button.click()

        self.browser.switch_to.alert.accept()#点击弹出框的确定



    #检测名额部分（核心代码）
    def examine(self):

        for target in target_info:#遍历所有目标课程

            row=self.browser.find_element_by_xpath("//span[text()='"+target+"']/../../..")#找到目标课程所在列表行

            status=row.find_element_by_xpath("./td[last()-1]/span")#找到状态栏

            occupied,total=int(status.text.split('/')[0]),int(status.text.split('/')[1])#解析名额情况

            self.pr("课程: "+target+"        目前情况: "+str(occupied)+"/"+str(total))

            if occupied>=total or occupied==0 : 
                continue#出现满员或者错误的情况就继续搜索下一个目标
            else : 
                self.snatch(target)#抢夺课程
                self.reminder(target,occupied,total)#发送通知
                break#重新加载窗口

    #循环刷新部分
    def refresh(self):
        
        self.state=STATE.REFRESHING
        self.pr("开始循环刷新...")
        count=1#刷新次数
        while(True):

            try:
                examine()#检查        
            except:
                self.pr("*检测到系统错误*   时间："+self.gettime())
                self.pr('尝试重新加载...\n')

                if self.email_reminder: 
                    self.sendemails('ERROR','错误： 检测到刷新过程中的系统异常        \n目前刷新次数：'+str(count)+'\n系统正在尝试重启...')

                self.state=STATE.RESTARTING
                while(1):time.sleep(1)
            else:
                self.browser.refresh()#刷新
                self.pr("系统时间:  "+self.gettime()+"  刷新次数： "+str(count)+"次")
                time.sleep(self.frequency)#刷新延迟
                count+=1
                if count%10000==0 and self.email_reminder:#工作报告
                    self.sendemails('REPORT','例行报告： 系统正常运行中  \n目前刷新次数：'+str(count))



    #主函数
    def main(self):


        try:
            #进入开发者模式，隐藏测试标记
            #options = ChromeOptions()
            #options.add_experimental_option('excludeSwitches', ['enable-automation'])
            self.pr("调用浏览器驱动...")
            self.browser = Chrome(self.driverpath)#生成一个webdriver对象，同时启动浏览器驱动与浏览器本身
            #使用“chromedrive”连接并操纵chrome浏览器
            self.browser.implicitly_wait(10)#隐式等待，每隔半秒查询一次，最多持续10s
            #AC=ActionChains(browser)#初始化动作族

        except:
            self.pe(ERROR.DRIVER_ERROR)
            #print("error")

        self.connect()

        self.login()

        if self.login_method==LM.PORTAL:
            self.jump_to_elective()

        self.jump_to_by_election()

        self.refresh()




