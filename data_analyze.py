#本文件用于分析训练效果

import os
import shelve
import matplotlib.pyplot as plt

PATH = os.path.dirname(__file__)


loss_list=[]
iter_list=[]
with shelve.open(os.path.join(PATH,'loss/lossdata')) as d:
    loss_list=d['loss']
    iter_list=d['iter']

plt.title('Loss function descent')
plt.plot(iter_list,loss_list)
plt.show()