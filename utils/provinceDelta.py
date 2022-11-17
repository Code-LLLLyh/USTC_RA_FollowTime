# -*- coding: utf-8 -*-
"""
Created on Wed Nov  9 10:24:52 2022

@author: 92853
"""
import pandas as pd
import datetime
     
class provinceDelta():
    '''
    用于计算省级文件follow上级的时间差
    '''
    def __init__(self):
        self.workContext='处理数据格式进行LDA分析'
        
    
    def cacaulte(self,data,start,path):
        '''
        用于计算响应时间的函数,之后整理成 时间（年）-各省（响应时间）的平面数据储存
        :param data dataframe follow上级文件的省级政策文件
        :param start datetime 确定开始的政策时间年份
        :param path str 储存地址的指标
        '''
        #整理省级文件的重要数据形成dataframe
        data=data.copy()
        data_Province=data[data['IssueDate']>=start]
        data_Province=data_Province[['id','Title','IssueDate','上级文件发布时间','省']]
        del data
        
        #计算响应时间并入上述dataframe
        delta=data_Province['IssueDate']-data_Province['上级文件发布时间']
        data=pd.concat([data_Province,delta],axis=1)
        co=data_Province.columns.tolist()
        co.append('响应时间')
        data.columns=co
        del co,data_Province,delta
        
        #计算每年各省follow上级的政策的响应时间
        data_Add=pd.DataFrame()
        province=data['省'].unique().tolist()
        for i in range(2000,2020):
            start_Year=datetime.datetime.strptime(str(i)+'.01.01', "%Y.%m.%d")
            end_Year=datetime.datetime.strptime(str(i+1)+'.01.01', "%Y.%m.%d")
            data_AddPro=pd.DataFrame({'年份':i},index=[0])
            for pro in province:
                data_Caculate=data[(data['省']==pro) & (data['IssueDate']>=start_Year) &(data['IssueDate']<end_Year)]
                value=data_Caculate['响应时间'].mean()
                data_AddPro=pd.concat([data_AddPro,pd.DataFrame({pro:value},index=[0])],axis=1)
            data_Add=pd.concat([data_Add,data_AddPro])
        #修改    
        data_Add.reset_index(inplace=True,drop=True)
        #储存数据
        data_Add.to_excel('data/省级文件/'+path+'/响应时间.xlsx',index=False)
        
    def getProFollow(self,path):
        '''
        用于获取follow上级政策的省级文件
        :param path str 储存地址的指标
        :return data dataframe follow上级文件的省级政策文件
        '''
        data=[]
        for i in range(1,11):
            data.append(pd.read_excel('data/省级文件/'+path+'/省级文件_'+str(i)+'_follow.xlsx'))
        data=pd.concat(data)
        data.reset_index(drop=True,inplace=True)
        data.dropna(axis=0,how='any',subset=['上级文件发布时间'],inplace=True)
        
        return data
    
if __name__ == '__main__':
    proD=provinceDelta()
    
    path='All'
    data=proD.getProFollow(path)
    
    start=datetime.datetime.strptime('2000.01.01', "%Y.%m.%d")
    proD.cacaulte(data,start,path)

