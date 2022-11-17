# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 19:03:09 2022

@author: 92853
"""
import pandas as pd
import math
from utils.getSeniorName import getSeniorName as gSN
import sys 
import time
import datetime

class matchSeniorDate():
    '''
    用于匹配省级文件和follow的上级文件的颁布时间
    dateFormat：数据日期格式统一化
    matchDate：匹配省级文件和上级文件的颁布时间
    isShorten：在匹配过程中需要使用到的一个函数，帮助查看省级文件在描述上级文件时是否使用了缩写
    故，使用函数应为dateFormat--matchDate
    '''
    def __init__(self):
        
        self.workContext='处理数据格式进行LDA分析'
        
        
    def isShorten(self,name,date,data_nation):
        '''
        帮助判断是否进行了缩写
        :param name str 需要判断的省级follow文件的上级
        :param date date 省级文件发布的时间
        :param data_nation dataframe 限定了日期的国家级文件的数据
        :return date_Append date/float 如果是缩写了就输出日期，否则输出nan
        '''            
        #先假设其没有缩写，之后进行缩写判断
        date_Append=math.nan
        #判断缩写，要遍历所有国家级文件
        for i in range(0,data_nation.shape[0]):
            doc=data_nation['Title'].iloc[i]            
            #name和doc重复字的个数
            num=0
            for word in name:
                if word in doc:
                    num=num+1
            #重复大于90%就认为是缩写了，因此找到这个文件的日期位置输出，退出循环
            if -num/max(len(name),1)<=-0.90:
                date_Append=data_nation['IssueDate'].iloc[i]
                break
            
        return date_Append
        
    def matchDate(self,data,docSenior):
        '''
        匹配上级文件颁布时间和省级文件
        :param data dataframe 国家级文件的数据
        :param docSenior dataframe 省级文件数据
        :return date list  省级follow文件对应国家级文件颁布时间
        '''

        ##获得省级文件的名称，并把书名号格式进行了统一
        name_Follow=docSenior['上级文件名称'].tolist()
        date_Follow=docSenior['IssueDate'].tolist()
        name_Province=[]
        for name in name_Follow:
            name_1=name.replace('〈','《')
            name_2=name_1.replace('〉','》')
            name_3=name_2.replace('＜','《')
            name_4=name_3.replace('＞','》')
            name_5=name_4.replace('<','《')
            name_6=name_5.replace('>','》')
            name_Province.append(name_6)
        del name,name_1,name_2,name_3,name_4,name_5,name_6
        
        ##找到省级文件对应的国家级文件对应的位置，并获取日期
        date=[]
        start=time.time()
        delta=datetime.datetime.strptime('2008.01.01', "%Y.%m.%d").date()-datetime.datetime.strptime('2005.01.01', "%Y.%m.%d").date()
        #遍历省级文件
        for i in range(0,len(name_Province)):
            name=name_Province[i]
            date_Province=date_Follow[i]
            #在一定的时间范围内，获取国家级文件的名字和日期
            data_nation=data[(data['IssueDate']<=date_Province) & (data['IssueDate']+delta>=date_Province)] 
            name_Nation=data_nation.Title.tolist()
            date_Nation=data_nation.IssueDate.tolist()
            #如果可以直接在这些国家级文件中找到省级文件follow的内容
            if name in name_Nation:
                pos=name_Nation.index(name)
                date.append(date_Nation[pos])
            #如果name不在name_Nation中，可能是确实不存在或者进行了缩写，使用另一个函数进行判断
            else:
                date_Append=self.isShorten(name, date_Province, data_nation)
                date.append(date_Append)
            #每工作1000条数据输出一下
            if i%1000==0 and i>0:
                end=time.time()
                print('已处理1000条数据,耗时:'+str(round(end-start,2))+'秒')
                start=time.time()
                
        return date
    
    def dateFormat(self,data):
        '''
        将str格式的日期数据处理为可以比较的datetime格式
        :param data dataframe 需要处理的数据
        :return data dataframe 修改好的数据
        '''
        data=data.copy()
        date=[]
        #这里有一个问题，部分数据不是xxxx.xx.xx的格式，故用上一个数据进行填充
        for i in range(0,data.shape[0]):
            date_1=data['IssueDate'].iloc[i]
            if len(date_1)==10:
                date.append(datetime.datetime.strptime(date_1, "%Y.%m.%d").date())
            else:
                date.append(date[i-1])
        #删除原日期数据，修改日期数据格式，合并其他数据和日期数据
        data.drop(['IssueDate'],axis=1,inplace=True)
        date=pd.DataFrame(date,columns=(['IssueDate']))
        data=pd.concat([data,date],axis=1)
        
        return data
    
    def matchFinal(self,data,data_Province,gSN,path,where_Select='All'):
        '''
        整合函数
        :param data dataframe 国家级政策文件
        :param data_Province dataframe 省级政策文件
        :param gSN getSeniorName_Module 自定义函数,用于获取上级文件的名字
        :path str 保存文件的名称
        :param where_Select str 默认为"All"指所有follow上级文件的省级政策，"Name":从名字中follow,"Context":从内容中Follow
        :return docSenior dataframe 上级文件发布的时间等数据的整合
        '''
        #找到有follow上级文件的省级政策
        if where_Select=='All':
            data_Follow=data_Province[data_Province['follow']!=0]
        elif   where_Select=='Name':
            data_Follow=data_Province[data_Province['follow']==1]
        elif   where_Select=='Context':
            data_Follow=data_Province[data_Province['follow']==0.5]
        else:
            print('没有正确选择升级政策follow上级的位置')
        #注意要把index修改一下
        data_Follow.reset_index(inplace=True,drop=True)  
        
        start=time.time()
        print('正在处理'+path)
        ##根据省级文件的内容获取上级文件的名称
        #先初步获取文件名称
        name_List=gSN.nameListGet(data_Follow)
        #筛选文件名称
        document_List=gSN.selectName(name_List)
        #合并文件名称
        docSenior=gSN.getSeniorName(data_Follow,document_List) 
        del data_Province,data_Follow,name_List,document_List

        ##匹配省级文件和上级文件的颁布时间
        #修改日期格式
        mSD=matchSeniorDate()
        data=mSD.dateFormat(data)
        docSenior=mSD.dateFormat(docSenior)
        
        #对日期进行匹配
        dateSenior=mSD.matchDate(data,docSenior) 
        #合并数据
        dateSenior=pd.DataFrame(dateSenior,columns=(['上级文件发布时间']))
        docSenior=pd.concat([docSenior,dateSenior],axis=1)
        
        end=time.time()
        print('处理'+path+'结束，耗时:'+str(round(end-start,2))+'秒')

        return  docSenior       

if __name__ == '__main__':

    #读取国家级文件，这部分是确定的（之后放入data中）
    data=[]
    nation_Name=['部门规章;部门规范性文件','部门规章;部门规章','行政法规;国务院规范性文件','行政法规;行政法规']
    for name in nation_Name:
        data.append(pd.read_excel('../data/国家级文件/'+name+'.xlsx'))
    data=pd.concat(data,axis=0)
    data.reset_index(drop=True,inplace=True)
    title=data[['Title']]
    date=data[['IssueDate']]
    data=pd.concat([title,date],axis=1)
    del date,title
    
    gSN=gSN()
    mSD=matchSeniorDate()
    #
    for i in range(4,11):
        data_Province=pd.read_excel('../data/地方规范性文件_follow/地方规范性文件_省级'+str(i)+'follow.xlsx')
        path='省级文件_'+str(i)+'follow'
        mSD.matchFinal(data,data_Province,gSN,path)
   

    
 
    