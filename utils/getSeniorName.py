# -*- coding: utf-8 -*-
"""
Created on Fri Nov  4 15:32:24 2022

@author: 92853
"""
import pandas as pd
from bs4 import BeautifulSoup
import re
import math
import numpy as np
class getSeniorName():
    '''
    用于获取一个Follow文件中每条政策follow的上级文件名称
    逻辑链条：strGetName(从文本中筛选上级文件）--nameListGet(将文本整理成list)--selectName(进一步筛选)--getSeniorName（筛选、整合、删除）
    故，使用函数应为nameListGet--selectName--getSeniorName
    '''
    def __init__(self):
        self.workContext='处理数据格式进行LDA分析'
        
    def strGetName(self,txt):
        '''
        获得上级文件的名字(粗略获得)
        :param txt str 文本格式
        :return name str 上级文件的名字
        '''
        #首先正则化处理HTML的格式
        soup=BeautifulSoup(txt,'html.parser') #具有容错功能
        text=soup.get_text()
        #处理一部分处理不掉的格式
        text.replace('\ue7fd','')
        #result_list=text.split('\\n')
        result_list = re.split('n|。',text)
        #按句子获取上级文件的名字
        name=math.nan
        for context in result_list:
            if (("《" in context and "》" in context) and
                ("（" in context and "）" in context) and 
                ("号" in context)):
                    start=context.index("《")
                    end=context.rindex("）")
                    name=context[start:end+1]

                    break
                
            elif (("《" in context and "》" in context) and
                ("(" in context and ")" in context)  and 
                ("号" in context)):
                    start=context.index("《")
                    end=context.rindex(")")
                    name=context[start:end+1]

                    break

        return name
    
    def nameListGet(self,data_Follow):
        '''
        生成name_List 作为获得文本数据的下一步的相关步骤
        :param data_Follow dataframe 有follow的数据
        :return name_List list 法律文件的上级文件名称列表
        '''
        data_Follow=data_Follow.copy()
        name_List=[]
        for i in range(0,data_Follow.shape[0]):
            context=data_Follow["AllText"].iloc[i]
            name=self.strGetName(context)
            name_List.append(name)
        
        return name_List
    
    def selectName(self,name_List):
        '''
        进一步筛选名字，方法是找到"》（"或"》("的位置，之后从"》"的位置倒着找"《",从"("的位置正着找")"
        :param name_List list 上级文件名字粗略的list
        :return document_List list 经过进一步筛选的上级文件的list 
        '''
        document_List=[]
        for name in name_List:
            if isinstance (name,str):
                if name.find("》（") !=-1:
                    position=name.find("》（")
                    start=name.rfind("《",0,position)
                    end=name.find("）",position)
                    document=name[start:end+1]
                elif name.find("》(") !=-1:
                    position=name.find("》(")
                    start=name.rfind("《",0,position)
                    end=name.find(")",position)
                    document=name[start:end+1]
                else:
                    document=math.nan
            else:
                document=math.nan
            
            document_List.append(document)
        
        return document_List
    
    def getSeniorName(self,data_Follow,document_List):
        '''
        在document_List的基础上，直接获取文件名称，并与文件合并
        :param data_Follow dataframe 跟随上级文件的文件数据
        :param document_List list 文件名称
        :return document_Senior dataframe合并之后的由上级文件的follow名单
        '''
        #进行第一步，处理获得文件名字
        document_Senior=[]
        for document in document_List:
            if isinstance (document,str):
                start=document.find("《")
                end=document.find("》")
                document_Name=document[start+1:end]
                document_Senior.append(document_Name)
            else:
                document_Senior.append(document)
        #进行第二步，合并文件
        data_Follow=data_Follow.copy()
        document_Senior=pd.DataFrame(document_Senior,columns=['上级文件名称'])        
        document_Senior=pd.concat([data_Follow,document_Senior],axis=1) 
        #第三步，删除没有得到上级文件名称的行
        document_Senior.dropna(subset = ['上级文件名称'],inplace=True)
        document_Senior.reset_index(inplace=True,drop=True)
        
        return document_Senior
    

        
if __name__ == '__main__':
    gSN=getSeniorName()
    data=pd.read_excel('../data/地方规范性文件_follow/地方规范性文件_省级'+str(3)+'follow.xlsx')
    data_Follow=data[data['follow']!=0]
    data_Follow.reset_index(inplace=True,drop=True)
    del data
    
    #先初步获取文件名称
    name_List=gSN.nameListGet(data_Follow)
    #筛选文件名称
    document_List=gSN.selectName(name_List)
    #合并文件名称
    document_Senior=gSN.getSeniorName(data_Follow,document_List)             

