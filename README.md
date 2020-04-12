# 异常转账行为识别
基于深度搜索和随机游走的有向图遍历算法

## 运行环境
python==3.6.4<br>
numpy==1.16.4

## 问题重述
通过金融风控的资金流水分析，可有效识别循环转账，辅助公安挖掘洗钱组织，帮助银行预防信用卡诈骗。基于给定的资金流水，检测并输出指定约束条件的所有循环转账。

## 数据详情
输入为包含资金流水的[文本文件](https://github.com/wzy6642/Identification-of-Abnormal-Transfer-Behavior/blob/master/Data/test_data.txt)，每一行代表一次资金交易记录，包含本端账号ID, 对端账号ID, 转账金额，用逗号隔开。举例如下，其中第一行1,2,100表示ID为1的账户给ID为2的账户转账100元：
<br>1,2,100<br>
1,3,100

## 输出结果
第一行输出：满足限制条件下的循环转账个数。第二行开始：输出所有满足限制条件的循环转账路径详情。

## 解决方案
1. 创建布尔型连接矩阵（利用Scipy.sparse创建稀疏矩阵更加节省内存），S代表资金源头，T代表转账目标，0代表没有转账，1代表发生转账：

<div align=center><img src="https://github.com/wzy6642/Identification-of-Abnormal-Transfer-Behavior/blob/master/img/存储.JPG" alt="存储"/></div>

2. 遍历资金源头的每一个客户，并指定其一级连接方式，例如：1->2->…我们就从2处开始分析。当分析完这个情况时，我们再分析1的其它可能连接情况。其中，每一级连接的目标都可以通过其对应行向量中为1的值对应的列索引得到。并把每一次连接的头部与尾部用列表保存下来，例如：

<div align=center><img src="https://github.com/wzy6642/Identification-of-Abnormal-Transfer-Behavior/blob/master/img/头尾.JPG" alt="头尾"/></div>

3. 通过头部列表与尾部列表构建连接方式，这里逆用杨辉三角解决问题：我们从最后一层构建个数连接关系，我们将源头数字转换为字符串格式，并与下图中的数值进行相乘。

<div align=center><img src="https://github.com/wzy6642/Identification-of-Abnormal-Transfer-Behavior/blob/master/img/连接.JPG" alt="连接"/></div>

4. 计算得到转账关系矩阵：

<div align=center><img src="https://github.com/wzy6642/Identification-of-Abnormal-Transfer-Behavior/blob/master/img/结果.JPG" alt="结果"/></div>

## 结果分析
我们从上述连接关系中寻找循环部分便为循环转账用户，具体结果见[文档](https://github.com/wzy6642/Identification-of-Abnormal-Transfer-Behavior/blob/master/code/result.txt)<br>
对于6000用户的数据集上述方法耗时1.26秒。具体代码参见[mainV1.2.py](https://github.com/wzy6642/Identification-of-Abnormal-Transfer-Behavior/blob/master/code/mainV1.2.py)<br>
对于大型数据集，我们可以采用随机游走的方式得到完整的循环转账用户，核心算法和上述过程一致，为了加快搜索可以在程序中引入多线程，具体代码参见[mainV1.3.py](https://github.com/wzy6642/Identification-of-Abnormal-Transfer-Behavior/blob/master/code/mainV1.3.py)
