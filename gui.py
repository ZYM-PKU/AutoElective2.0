#本文件定义可视化界面与交互行为

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\Code\python\AutoElective\qt\login.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

import os
import sys
import time
import shelve

from PyQt5.uic import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *



from constant import *
from AutoElec import *
from threading import Thread
from thread_control import stop_thread

PATH = os.path.dirname(__file__)


# 全局变量声明：
#######info#######
targets = []  # 选课目标
user_id = ""  # 学号
user_password = ""  # 密码
driver_choice = DRIVER.CHROME #浏览器驱动选择（默认chrome）
user_driver = ""  # 浏览器驱动地址
#######choices######
sound_reminder = SR.NONE  # 声音提醒
email_reminder = False  # 邮件提醒
login_method = LM.PORTAL  # 登录方式
refresh_frequency = 2  # 刷新频率
icr_permitted = False  # 启用验证码识别
icr_method = IM.CNN  #识别方法

#激活码
activition_keys=[]


class MySignal(QObject):
    '''前后端信号传递'''
    print_text = pyqtSignal(str)
    error_message = pyqtSignal(ERROR)
    show_image = pyqtSignal(str)


class Loginwindow(QWidget):
    '''登录界面'''
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(PATH, "qt/ui/login.ui"), self)  # 加载UI文件
        self.continued=False #是否继续加载主页面
        self.infoinit()  # 初始化用户信息
        self.startbutton.clicked.connect(self.submit)
        self.checkBox_4.stateChanged.connect(self.password_change)
        self.DriverChoice.buttonToggled.connect(self.driver_change)

    def infoinit(self):
        global targets,user_driver,driver_choice
        try:
            with shelve.open(os.path.join(PATH, "qt/save/studentinfo")) as s:
                self.lineEdit.setText(s['id'])
                self.lineEdit_2.setText(s['password'])
                self.lineEdit_3.setText(s['driver'])
                targets = s['targets']
                for i, target in enumerate(targets):
                    item = QTableWidgetItem()
                    text=target[0]+'-'
                    for it in target[1]:
                        text+=str(it)+'/'
                    item.setText(text[:-1])
                    self.etable.setItem(i, 0, item)
            if self.lineEdit.text() and self.lineEdit_2.text() and self.lineEdit_3.text():
                self.checkBox.setChecked(True)
        except:
            pass
        driver_choice = DRIVER.CHROME
        user_driver=os.path.join(PATH,'webdriver\chromedriver.exe')
        self.lineEdit_3.setText(user_driver)
        
        

    def closeEvent(self, event):
        """重写窗口关闭相应方法，保证主窗口被人为关闭时自动停止所有线程，结束主线程"""
        if not self.continued: sys.exit(0)

    def qualify(self):
        '''身份验证函数'''
        while True:
            text, okPressed = QInputDialog.getText(self, "Activition Key:","输入激活密钥：", QLineEdit.Normal, "")
            if okPressed and text != '':
                if text in activition_keys:
                    break

    def submit(self):
        # 获取选课信息
        global targets
        targets.clear()
        for i in range(6):
            try:
                target = self.etable.item(i, 0).text()
                target_item=target.split('-')
                target_class=target_item[0].replace(' ','')
                target_ids=[]
                if len(target_item)>1:
                    for it in target_item[1].split('/'):
                        try:
                            target_ids.append(int(it))
                        except:
                            continue
                if target_class:
                    targets.append([target_class,target_ids])
            except:
                continue
        #获取用户信息
        global user_id,user_password
        user_id =self.lineEdit.text()
        user_password =self.lineEdit_2.text()

        # 表单验证
        if len(user_id) != 10:
            if not user_id:
                QMessageBox.warning(self, '警告', '请填写学号！')
            else:
                QMessageBox.critical(self, '错误', '学号填写有误！')
            return
        elif not user_password:
            QMessageBox.warning(self, '警告', '请填写密码！')
            return
        elif not user_driver:
            QMessageBox.warning(self, '警告', '请填写浏览器驱动路径！')
            return

        if not targets:
            QMessageBox.warning(self, '警告', '请设置至少一个选课目标！')
            return




        # 获取设置
        global sound_reminder
        if self.comboBox.currentText() == '不提醒':
            sound_reminder = SR.NONE
        elif self.comboBox.currentText() == '任何时候':
            sound_reminder = SR.ANYTIME
        elif '合适的时候' in self.comboBox.currentText():
            sound_reminder = SR.APPROPRIATE



        global login_method
        try:
            if self.LoginMethod.checkedButton().text() == '选课网':
                login_method = LM.ELECTIVE
            elif self.LoginMethod.checkedButton().text() == '门户':
                login_method = LM.PORTAL
        except:
            login_method = LM.ELECTIVE

        global email_reminder, icr_permitted
        if self.checkBox_2.isChecked():
            email_reminder = True
        else:
            email_reminder = False
        if self.checkBox_3.isChecked():
            icr_permitted = True
        else:
            icr_permitted = False

        global refresh_frequency
        refresh_frequency = self.spinBox.value()


        # 保存信息
        if self.checkBox.isChecked():
            self.saveinfo()
        else:
            with shelve.open(os.path.join(PATH, "qt/save/studentinfo")) as s:
                s['id'] = s['password'] = ""
                s['targets'] = []

        #身份验证
        #self.qualify()

        # 窗口跳转
        self.mainwindow = Mainwindow()
        self.mainwindow.show()
        self.continued=True
        self.close()

    def password_change(self):
        if self.checkBox_4.isChecked():
            self.lineEdit_2.setEchoMode(QLineEdit.EchoMode(0))
        else:
            self.lineEdit_2.setEchoMode(QLineEdit.EchoMode(2))

    def driver_change(self):
        global driver_choice,user_driver

        if self.DriverChoice.checkedButton().text() == 'Chrome':
            driver_choice = DRIVER.CHROME
            user_driver=os.path.join(PATH,'webdriver\chromedriver.exe')
        elif self.DriverChoice.checkedButton().text() == 'Edge':
            driver_choice = DRIVER.EDGE
            user_driver=os.path.join(PATH,'webdriver\edgedriver.exe')
        elif self.DriverChoice.checkedButton().text() == 'Firefox':
            driver_choice = DRIVER.FIREFOX
            user_driver=os.path.join(PATH,'webdriver\\firefoxdriver.exe')
        elif self.DriverChoice.checkedButton().text() == 'IE':
            driver_choice = DRIVER.IE
            user_driver=os.path.join(PATH,'webdriver\iedriver.exe')
        self.lineEdit_3.setText(user_driver)


    def saveinfo(self):
        with shelve.open(os.path.join(PATH, "qt/save/studentinfo")) as s:
            s['id'] = self.lineEdit.text()
            s['password'] = self.lineEdit_2.text()
            s['driver'] = self.lineEdit_3.text()
            s['targets'] = targets



class Mainwindow(QMainWindow):
    '''主界面'''
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(PATH, "qt/ui/mainwindow.ui"), self)  # 加载UI文件

        #初始化选课工具  
        self.ms = MySignal()#前后台信号传输
        self.ET = Electool(self,targets,user_id,user_password,driver_choice,user_driver,sound_reminder,email_reminder,login_method,refresh_frequency,icr_permitted,icr_method,self.ms)

        #初始化界面
        self.infoinit()
        self.comboBox.currentIndexChanged.connect(self.change_method)
        self.ms.print_text.connect(self.printinfo)
        self.ms.error_message.connect(self.error_handler)
        self.ms.show_image.connect(self.show_image)
        self.restartbutton.clicked.connect(self.restart)
        self.stopbutton.clicked.connect(self.stop)


        #界面线程，控制界面变化
        self.window_thread=Thread(target=self.window_refresh)
        self.window_thread.setDaemon(True)
        self.window_thread.start()


        #主线程
        self.mainthread=Thread(target=self.ET.run)
        self.mainthread.setDaemon(True)
        self.mainthread.start()


    def closeEvent(self, event):
        """重写窗口关闭相应方法，保证主窗口被人为关闭时自动停止所有线程，结束主线程"""
        reply = QMessageBox.question(self, 'EXIT', '确认退出吗？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.terminate_thread()
            except:
                pass
            sys.exit(0)
        else:
            event.ignore()




    def infoinit(self):
        global targets
        for i, target in enumerate(targets):
            item = QTableWidgetItem()
            text=target[0]+'-'
            for it in target[1]:
                text+=str(it)+'/'
            item.setText(text[:-1])
            self.etable.setItem(i, 0, item)
        
        self.ET.state=STATE.LOADING


    def change_method(self):
        global icr_method
        if self.comboBox.currentText() == "cnn method":
            icr_method = IM.CNN
            self.ET.icr_method=IM.CNN
            self.piclabel.setPixmap(QPixmap(os.path.join(PATH, "qt/pics/PyTorch-logo.jpg")))
        elif self.comboBox.currentText() == "tesseract-OCR":
            icr_method = IM.OCR
            self.ET.icr_method=IM.OCR
            self.piclabel.setPixmap(QPixmap(os.path.join(PATH, "qt/pics/ocr.jpg")))


    def printinfo(self, text):
        '''在文本输出框打印当前线程'''
        if self.ET.state not in (STATE.STOPPED,STATE.RESTARTING):
            self.infobox.append(text)
            self.infobox.ensureCursorVisible()

    def error_handler(self,e):
        '''错误处理'''
            
        if e==ERROR.EMAIL_ERROR:
            msg_box = QMessageBox(QMessageBox.Warning, '警告', '邮箱信息错误或不完整！已关闭邮件提醒功能。')
            msg_box.exec_()

        elif e==ERROR.DRIVER_ERROR:
            self.ET.state=STATE.ERROR
            msg_box = QMessageBox(QMessageBox.Warning, '错误', '浏览器驱动出错！请检查驱动地址。')
            msg_box.exec_()
            sys.exit(0)
        elif e==ERROR.PASSWORD_ERROR:
            self.ET.state=STATE.ERROR
            msg_box = QMessageBox(QMessageBox.Warning, '错误', '学号或密码填写错误，请检查你的输入。')
            msg_box.exec_()
            sys.exit(0)
        else:
            self.ET.state=STATE.ERROR
            self.restart_thread()
    
    def show_image(self,path):
        '''显示验证码图片'''
        self.codeimg.setPixmap(QPixmap(path))

    def window_refresh(self):
        '''窗口线程'''
        while(1):
            #时间栏
            time.sleep(0.1)#2020.9.27 添加时间延迟，控制窗口刷新速率为10Hz，防止过于密集的刷新占用大量cpu计算力

            self.timelabel.setText(self.ET.gettime())
            if self.ET.state==STATE.REFRESHING:
                #速率栏
                self.frequencylabel.setText(f"{round(self.ET.refresh_speed,3)}s  (+{refresh_frequency}s)")
                #次数统计栏
                self.countlabel.setText(f"{self.ET.refresh_count}次")


            #状态栏
            if self.ET.state==STATE.LOADING:self.statelabel.setText("正在启动...")
            elif self.ET.state==STATE.INITIALIZING:self.statelabel.setText("初始化...")
            elif self.ET.state==STATE.CONNECTING:self.statelabel.setText("尝试连接...")
            elif self.ET.state==STATE.LOGINING:self.statelabel.setText("正在登录...")
            elif self.ET.state==STATE.JUMPING:self.statelabel.setText("正在跳转...")
            elif self.ET.state==STATE.EXAMINING:self.statelabel.setText("初始化课程检索...")
            elif self.ET.state==STATE.REFRESHING:self.statelabel.setText("自动刷新监控中...")
            elif self.ET.state==STATE.SNATCHING:self.statelabel.setText("正在自动抢课...")
            elif self.ET.state==STATE.ERROR:self.statelabel.setText("系统异常")
            elif self.ET.state==STATE.RESTARTING:self.statelabel.setText("正在尝试重启...")
            elif self.ET.state==STATE.STOPPED:self.statelabel.setText("系统中断")


    #重启进程
    def restart_thread(self):
        self.ET.state=STATE.RESTARTING
        self.infobox.append("\n######尝试重启进程...######")
        self.infobox.ensureCursorVisible()
        try:
            self.ET.browser.quit()
        except:
            pass
        try:
            stop_thread(self.mainthread)
        except:
            pass

        self.mainthread=Thread(target=self.ET.run)
        self.mainthread.setDaemon(True)
        self.mainthread.start()


    #停止进程
    def terminate_thread(self):
        self.ET.state=STATE.STOPPED

        self.infobox.append("\n######进程已终止.######")
        self.infobox.ensureCursorVisible()
        try:
            self.ET.browser.quit()
        except:
            pass
        try:
            stop_thread(self.mainthread)
        except:
            pass



    def restart(self):
        self.restart_thread()
        self.stopbutton.setEnabled(True)

    def stop(self):
        self.terminate_thread()
        self.stopbutton.setEnabled(False)



def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(QIcon(os.path.join(PATH, "qt/pics/peking.png")))
    lw = Loginwindow()
    lw.show()
    sys.exit(app.exec_())
