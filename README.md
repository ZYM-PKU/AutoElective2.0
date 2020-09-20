# AutoElective2.0
<font color=#999AAA >基于Web自动化测试与卷积神经网络自主开发的可视化选课应用
</font>



# 前言

&emsp;本项目基于selenium<sup id="a1">[1](#f1)</sup>Web应用程序测试，使用Pytorch<sup id="a2">[2](#f2)</sup>框架下定义的卷积神经网络识别验证码，并利用Chrome浏览器进行自动化刷课操作。

&emsp;本项目适用于北京大学选课网，提供可视化的人机交互界面，致力于为北京大学本科生在补退选/补选阶段选到心仪课程提供新的解决方案。

# 使用方法

## 1.环境配置
*首先要保证shell运行在项目根目录下，且已经安装Chrome浏览器。
### (1)安装[python3](https://www.python.org/)
### (2)安装[Pytorch](https://pytorch.org/)
推荐选项：

- `PyTorch Build`:  Stable (1.6.0)
- `Your OS`: Windows
- `Package`: Conda
- `Language`: Python
- `CUDA`: None（有N卡的可以选择对应的CUDA版本）
### (3)安装对应版本的[Chrome浏览器驱动](http://chromedriver.storage.googleapis.com/index.html)
请在Chrome设置的关于Chrome中查询浏览器版本号。
### (4)安装第三方依赖库
```
pip install -r requirement.txt
```


## 2.运行程序
输入指令：
```
python gui.py
```
该指令会打开一个初始化界面：
![img](./show/gui.png)

按照界面提示填写学号与密码，并在浏览器驱动一栏中填入下载好的驱动地址（绝对路径）。然后在右侧按照意愿顺序填写课程名称并进行一些设置后点击“开始”即可自动刷课。

# 结构与原理
## 1.项目主体结构
```
./AutoElective2.0/
├── envs       // 运行环境与配置文件
├── model            // 训练好的模型
├── paper             // 参考文献
├── qt            // 界面相关文件
├── show            // 图文材料
├── website            // 官网源代码
├── AutoElective.py         // 主程序
├── cnn.py    //定义卷积神经网络
├── constant.py         // 定义常量
├── data_analyze.py    // 模型分析
├── generate.py          // 验证码生成器（已废弃）
├── gui.py         //启动界面
├── LoginAttack.py            //自动标签数据集获取
├── options.py             //定义枚举
├── pretreatment.py           //图片预处理（降噪、二值化、上采样等）
├── test.py               //模型测试
├── thread_test.py            //多线程处理
├── train.py               //模型训练
└── transfer.py            //向量字符转换
```

## 2.运行逻辑

![img](./show/structrue.png)
&emsp;项目主界面文件gui.py利用Pyqt库生成可交互界面，并实例化一个定义在AutoElective.py中的Electool对象，该对象能够利用selenium与浏览器驱动模仿人类进行自动登录，点击，读取信息，刷新等一系列操作。Electool通过不断刷新网页嗅探可能出现的空余选课名额，发现名额后立刻识别验证码进行抢课。如果抢到课程，程序会以邮件或声音的方式提醒用户，否则将继续进行刷课。

&emsp;验证码的识别：利用pretreatment.py对图片进行预处理（降噪、二值化、上采样等），再使用model中训练好的卷积神经网络模型结合cnn.py进行识别处理，将得到四位响应结果填入框内。

&emsp;多线程处理：交互界面的线程与刷课线程互相独立，两者之间通过signal（信号）进行信息传递。即前台向后台发送指令，后台将运行情况反馈到前台并进行显示。这种处理方式保证了程序能够稳定运行。



## 3.模型训练
### (1)训练集的获取
&emsp;北京大学门户登录入口提供随机生成的四位验证码，我们只要通过连续的get请求下载图片即可获得大量原始验证码数据。然而，想要获得准确无误的标签数据集却没有那么容易。采用人工的方式不仅费时费力，而且准确性与数据量也无法保证。

![img](./show/ocr.png)

&emsp;那么如何在短时间内快速生成大量带有标签的数据呢？其实，我们可以利用网页后端服务器本身就带有比对验证功能，换句话说，可以“化敌为友”，利用服务器本身为我们的原始数据“打标签”。于是，基于OCR<sup id="a3">[3](#f3)</sup>与服务器的后端逻辑，我们不难设计出自动产生准确标签数据集的程序。

&emsp;具体实现方法如下：

&emsp;&emsp;(1)通过模拟用户操作的方式下载登录入口提供的验证码图片

&emsp;&emsp;(2)将验证码图片作预处理，并交由成熟的OCR系统进行字符识别

&emsp;&emsp;(3)将识别结果回填网页并提交表单

&emsp;&emsp;(4)若得到服务器的正确反馈则按照识别结果给图片打上标签，否则删除该图片

&emsp;&emsp;(5)刷新页面

&emsp;不断重复上述过程，理论上我们就可以得到一个有足够数据量的完美标签数据集了。在实践过程中，OCR的识别精度大约在55%，因此会有一半左右的图片会被废弃掉，留下一半完全正确标注的图片，整体效率较高。

### (2)神经网络的训练
&emsp;虽然OCR的方式已经有55%的识别准确度，但这显然还不够。为了进一步提高精度，我们选择使用当下比较流行的卷积神经网络方法进行识别。

&emsp;本项目使用的神经网络结构为3个卷积层+3个全连接层，并搭配一定程度的dropout防止过拟合（具体参考cnn.py）。该神经网络能够将特定大小的四位验证码图片映射成一个长向量，该长向量经过特定方式的翻译转换（transfer）后可以得到四位字符响应，此即识别结果。

&emsp;训练时将数据集（10000+数据量，已经过预处理）以64个为一个batch进行打包并随机抽样，经过200000次迭代后观察到loss曲线收敛，从而得到最终的训练结果，保存为pth文件。

&emsp;通过不断调节超参数，并经过多次训练，最终得到的效果最好的模型在测试数据集上的识别精度为92.53%。
![img](./show/model_result.png)





- - -

<b id="f1">1</b> Selenium是一个用于Web应用程序测试的工具。Selenium测试直接运行在浏览器中，就像真正的用户在操作一样。支持的浏览器包括IE（7, 8, 9, 10, 11），Mozilla Firefox，Safari，Google Chrome，Opera等。这个工具的主要功能包括：测试与浏览器的兼容性——测试你的应用程序看是否能够很好得工作在不同浏览器和操作系统之上。测试系统功能——创建回归测试检验软件功能和用户需求。支持自动录制动作和自动生成 .Net、Java、Perl等不同语言的测试脚本。 [↩](#a1)

<b id="f2">2</b> PyTorch是一个开源的Python机器学习库，基于Torch，用于自然语言处理等应用程序。2017年1月，由Facebook人工智能研究院（FAIR）基于Torch推出了PyTorch。它是一个基于Python的可续计算包，提供两个高级功能：1、具有强大的GPU加速的张量计算（如NumPy）。2、包含自动求导系统的的深度神经网络。 [↩](#a2)

<b id="f3">3</b> OCR （Optical Character Recognition，光学字符识别）是指电子设备（例如扫描仪或数码相机）检查纸上打印的字符，通过检测暗、亮的模式确定其形状，然后用字符识别方法将形状翻译成计算机文字的过程；即，针对印刷体字符，采用光学的方式将纸质文档中的文字转换成为黑白点阵的图像文件，并通过识别软件将图像中的文字转换成文本格式，供文字处理软件进一步编辑加工的技术。如何除错或利用辅助信息提高识别正确率，是OCR最重要的课题，ICR（Intelligent Character Recognition）的名词也因此而产生。衡量一个OCR系统性能好坏的主要指标有：拒识率、误识率、识别速度、用户界面的友好性，产品的稳定性，易用性及可行性等。 [↩](#a3)
