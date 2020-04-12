# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 11:07:34 2020
深度搜索+随机游走+多线程
@author: zy wu.
"""
import numpy as np
import multiprocessing
import random
import datetime
TEST = 0
NUM_ITERS = 100


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
    link_matrix = np.zeros((max([max(source), max(target)])+1, max([max(source), max(target)])+1), dtype=np.bool)
    for i in range(len(source)):
        link_matrix[source[i]][target[i]]=1
    return link_matrix
        

def One_Link(first_link, link_matrix):
    # 初始化
    Headers = []
    Targets = []
    header = [first_link[1]]
    # var_link_matrix = deepcopy(link_matrix)
    Headers.insert(0, [first_link[1]])  
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
        # for sub_header in header:
        sub_header = Headers[__iters-1][0]
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
        if len(header)>1:
            seed = random.randint(0, len(header)-1)
            # seed = 0
            # 断开连接
            # var_link_matrix[Headers[__iters-1][0]][header[seed]] = 0
        else:
            seed = 0
        Headers.append([header[seed]])
    Headers = Headers[:-1]
    ## 计算结果存储部分
    results = np.zeros((len(header),NUM_ITERS+2), dtype=np.int16)
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
    for record in all_record:
        if len(record) > 1:
            for k in range(len(record)):
                other_record.append([record[k]])
    all_record = all_record+other_record
    return all_record

    
def Concat_Final(concat):
    # [i for i in list(set(concat[0])) if np.sum(np.array(concat[0])==i) >= 2]
    final_record = []
    for i in concat:
        iter_num = [j for j in list(set(i)) if np.sum(np.array(i)==j) >= 2]
        for k in iter_num:
            temp = np.argwhere(np.array(i)==k)[:,-1]
            for m in range(len(temp)-1):
                temp2 = i[temp[m]:temp[m+1]]
                if 3<= len(temp2) <=7:
                    final_record.append(temp2)
    return final_record

    
def Save_Result(final_record2):
    final_record2.sort()
    final_record2 = sorted(final_record2, key = lambda i:len(i), reverse=False)  
    file = open('result.txt','w')
    file.write(str(len(final_record2))+'\n')
    for i in final_record2:   
        file.write(str(i).replace(" ","")[1:-1]+'\n')
        
    
def Multi_Process(root, link_matrix):
    first_link = np.array(link_matrix[root,:])
    first_link = np.argwhere(first_link==1)[:,-1]
    for header in first_link:
        Link = One_Link([root, header], link_matrix)
        return Link[0]


def Multi_Processes(roots, link_matrix):
    return [Multi_Process(root, link_matrix) for root in roots]


if __name__ == '__main__':
    starttime = datetime.datetime.now()
    cores = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=cores)
    data = LoadData()
    link_root, source, target = Root(data)
    del data
    link_matrix = Link_Matrix(source, target)
    del source, target
    if TEST:
        all_record = []
        root = link_root[358]
        # 奠基
        first_link = np.array(link_matrix[root,:])
        first_link = np.argwhere(first_link==1)[:,-1]
        for header in first_link:
            Link = One_Link([root, header], link_matrix)
            all_record.append(Link)
    else:
        all_record = []
        link_roots = [link_root[i: i+len(link_root)//cores] for i in range(0, len(link_root), len(link_root)//cores)]
        li = []
        for i in range(len(link_roots)):
            res = pool.apply_async(Multi_Processes, args=(link_roots[i], link_matrix))
            li.append(res)
        pool.close()
        pool.join()
        del link_matrix, link_root, link_roots
        for i in li:
            all_record.append(i.get())
        # all_record = [Multi_Process(root, link_matrix) for root in link_root]
    all_record = Flatting(all_record)
    # 剔除多余数据
    all_record = [i for i in all_record if len(i)==1]
    # 寻找可能解
    potential = [i for i in all_record if len(set(i[0]))<len(i[0])]
    del all_record
    # 处理-1
    potential_neg = [i[0] for i in potential if -1 in i[0]]
    potential_pos = [i[0] for i in potential if -1 not in i[0]]
    potential_neg = [i[:i.index(-1)] for i in potential_neg]
    potential_neg = [i for i in potential_neg if len(set(i))<len(i)]
    potential = potential_pos+potential_neg
    del potential_neg, potential_pos
    final_record = Concat_Final(potential)
    # final_record = [str(i) for i in final_record]
    # final_record = list(set(final_record))
    final_record_sort = list(set([tuple(sorted(t)) for t in final_record]))
    final_record.sort()
    final_record = sorted(final_record, key = lambda i:len(i), reverse=False)  
    # final_record_sort = list(set([tuple(t) for t in final_record]))
    final = []
    for i in final_record:
        temp = tuple(sorted(i))
        if temp in final_record_sort:
            final_record_sort.remove(temp)
            final.append(i)
    final = [i for i in final if len(set(i))==len(i)]
    Save_Result(final)
    endtime = datetime.datetime.now()
    print(endtime-starttime)
