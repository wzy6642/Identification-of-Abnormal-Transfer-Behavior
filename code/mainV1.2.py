# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 11:07:34 2020
完整版
@author: zy wu.
"""
import numpy as np
import datetime
TEST = 0
NUM_ITERS = 6


def LoadData():
    with open("../Data/test_data.txt", "r") as f:
        data = f.read()
    data = data.split('\n')[:-1]
    data = [i.split(',') for i in data]
    data = [[int(i[0]), int(i[1]), int(i[2])] for i in data]
    return data


def Root(data):
    source = [i[0] for i in data]
    target = [i[1] for i in data]
    # link_root = [i for i in source if i not in target]
    link_root = list(set(source))
    return link_root, source, target


def Link_Matrix(source, target):
    print("Build Matrix")
    link_matrix = np.zeros((max([max(source), max(target)])+1, max([max(source), max(target)])+1), dtype=np.bool)
    for i in range(len(source)):
        link_matrix[source[i]][target[i]]=1
    return link_matrix
        

def One_Link(first_link, link_matrix):
    # 初始化
    Headers = []
    Targets = []
    header = [first_link[1]]
    ## 存储奠基
    # Links.append(first_link)
    ## 递推模型
    # 循环次数限制
    __iters = 0
    while __iters<NUM_ITERS:
        Sub_Targets = []
        # 累加器
        __iters += 1
        # 层间连接
        for sub_header in header:
            if sub_header==-1:
                target = [-1]
            else:
                link = np.array(link_matrix[sub_header,:])
                target = list(np.argwhere(link==1)[:,-1])
            # 没有下级连接置为-1
            if len(target)==0:
                Sub_Targets.append([-1])
            else:
                Sub_Targets.append(target)
        Targets.append(Sub_Targets)
        header = sum(Targets[-1],[])
        Headers.append(header)
    Headers.insert(0, [first_link[1]])   
    Headers = Headers[:-1]
    ## 计算结果存储部分
    results = np.zeros((len(header),NUM_ITERS+2), dtype=np.uint16)
    results[:,-1] = header
    Length = []
    for i in range(NUM_ITERS):
        Sub_Length = []
        for j in Targets[NUM_ITERS-i-1]:
            Sub_Length.append(len(j))
        Length.append(Sub_Length)
    All_Length = []
    for i in range(len(Length)):
        if i==0:
            All_Length.append(Length[0])
        else:
            Sub_Record = []
            temp = Length[i]
            temp2 = All_Length[i-1]
            temp = np.cumsum(temp)
            for j in range(len(temp)):
                if j==0:
                    Sub_Record.append(sum(temp2[:temp[j]]))
                elif j==len(temp):
                    Sub_Record.append(sum(temp2[temp[j]:]))
                else:
                    Sub_Record.append(sum(temp2[temp[j-1]:temp[j]]))
            All_Length.append(Sub_Record)
    for i in range(len(All_Length)):
        temp = Headers[len(All_Length)-i-1]
        number = All_Length[i]
        record_ = []
        for j in range(len(temp)):
            record_.append([temp[j]]*number[j])
        record_ = sum(record_,[])
        results[:,len(All_Length)-i] = record_
    results[:,0] = [first_link[0]]*len(header)
    return results.tolist() 



def Flatting(all_record):
    other_record = []
    """
    for record in all_record:
        if len(record) > 1:
            for k in range(len(record)):
                other_record.append([record[k]])
    """
    other_record += [[record[k]] for record in all_record for k in range(len(record)) if len(record)>1]
    all_record = all_record+other_record
    return all_record

    
def Concat_Final(concat):
    final_record = []
    for i in concat:
        if np.sum(np.array(i)==i[0]) >= 2:
            final_record.append(i)
    final_record2 = []
    for i in final_record:
        temp = np.argwhere(np.array(i)==i[0])[:2]
        temp2 = i[temp[0][0]:temp[1][0]]
        if 3<= len(temp2) <=7:
            final_record2.append(temp2)
    return final_record2

    
def Save_Result(final_record2):
    final_record2.sort()
    final_record2 = sorted(final_record2, key = lambda i:len(i), reverse=False)  
    file = open('result.txt','w')
    file.write(str(len(final_record2))+'\n')
    for i in final_record2:   
        file.write(str(i).replace(" ","")[1:-1]+'\n')
        
        
if __name__ == '__main__':
    starttime = datetime.datetime.now()
    data = LoadData()
    link_root, source, target = Root(data)
    link_matrix = Link_Matrix(source, target)
    print("Build Links")
    if TEST:
        all_record = []
        root = link_root[0]
        # 奠基
        first_link = np.array(link_matrix[root,:])
        first_link = np.argwhere(first_link==1)[:,-1]
        for header in first_link:
            Link = One_Link([root, header], link_matrix)
            all_record.append(Link)
    else:
        all_record = []
        for root in link_root:
            # 奠基
            first_link = np.array(link_matrix[root,:])
            first_link = np.argwhere(first_link==1)[:,-1]
            for header in first_link:
                Link = One_Link([root, header], link_matrix)
                all_record.append(Link)
    all_record = Flatting(all_record)
    # 剔除多余数据
    all_record = [i for i in all_record if len(i)==1]
    # 寻找可能解
    potential = [i for i in all_record if len(set(i[0]))<len(i[0])]
    del link_matrix
    # 处理-1
    potential_neg = [i[0] for i in potential if -1 in i[0]]
    potential_pos = [i[0] for i in potential if -1 not in i[0]]
    potential_neg = [i[:i.index(-1)] for i in potential_neg]
    potential_neg = [i for i in potential_neg if len(set(i))<len(i)]
    potential = potential_pos+potential_neg
    final_record = Concat_Final(potential)
    del potential, potential_neg, potential_pos
    # final_record = [str(i) for i in final_record]
    # final_record = list(set(final_record))
    # final_record = list(set([tuple(t) for t in final_record]))
    final_record_sort = list(set([tuple(sorted(t)) for t in final_record]))
    final_record.sort()
    final_record = sorted(final_record, key = lambda i:len(i), reverse=False)  
    final = []
    for i in final_record:
        temp = tuple(sorted(i))
        if temp in final_record_sort:
            final_record_sort.remove(temp)
            final.append(i)
    final = [i for i in final if len(set(i))==len(i)]
    # final_record = [i for i in final_record if tuple(sorted(i)) in final_record_sort]
    Save_Result(final)
    endtime = datetime.datetime.now()
    print("Using Time: {}".format(endtime-starttime))
    