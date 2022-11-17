# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 10:23:13 2022

@author: 92853
"""
from utils.getSeniorName import getSeniorName as gSN
from utils.matchSeniorDate import matchSeniorDate as mSD
from utils.provinceDelta import provinceDelta as proDelta
import datetime
import time
import pandas as pd

if __name__ == '__main__':
    
    ##初始化三个大类函数
    #获取上级文件名称
    gSN=gSN()
    #获取上级文件发布时间
    mSD=mSD()
    #计算响应时间
    proDelta=proDelta()
    
    ##part1: 用于获取Follow上级文件的省级政策、Follow的上级文件的名称、上级文件颁布的时间
    '''
    #读取国家级文件，这部分是确定的（之后放入data中）
    data=[]
    nation_Name=['部门规章;部门规范性文件','部门规章;部门规章','行政法规;国务院规范性文件','行政法规;行政法规']
    for name in nation_Name:
        data.append(pd.read_excel('data/国家级文件/'+name+'.xlsx'))
    data=pd.concat(data,axis=0)
    data.reset_index(drop=True,inplace=True)
    title=data[['Title']]
    date=data[['IssueDate']]
    data=pd.concat([title,date],axis=1)
    del date,title
    

    #获得上级文件发布的时间后，将数据输出
    for i in range(1,11):
        #确定选取哪一部分Follow上级的省级文件，可选：All、Name、Context
        where_Var='Context'
        #读取省级文件
        data_Province=pd.read_excel('data/地方规范性文件_follow/地方规范性文件_省级'+str(i)+'follow.xlsx')
        #文件的名称
        path='省级文件_'+str(i)+'_follow'
        #获取上级文件的名称和发布时间
        docSenior=mSD.matchFinal(data,data_Province,gSN,path,where_Select=where_Var)
        #储存数据
        docSenior.to_excel('data/省级文件/'+where_Var+'/'+path+'.xlsx',index=False)
    ''' 
    
    ##part2：用于输出各个省份每年对上级文件的平均响应时间    
    #获得上级文件发布的时间后，将数据输出
    start=datetime.datetime.strptime('2000.01.01', "%Y.%m.%d")
    pathList=['All','Name','Context']
    for path in pathList:
        startSpecial=time.time()
        print('正在处理范围为: '+path+'的数据')
        data=proDelta.getProFollow(path)
        proDelta.cacaulte(data,start,path)
        endSpecial=time.time()
        print('处理结束，用时'+str(round(endSpecial-startSpecial,2))+'秒')