# -*- coding: utf-8 -*-
# @Author: 刘威
# @Date:   2020-03-16 12:37:21
# @Last Modified by:   刘威
# @Last Modified time: 2020-03-18 14:24:49
import os
import pandas as pd
path=r'C:\Users\Desktop\CIPS-DataCollect'
a=range(0,10)
result=pd.DataFrame()
mm=10000
for i in a:
	for j in range(1,11):
		for k in range(2,3):
			filename=str(i)+'-'+str(j)+' value'+str(k)+'.txt'
			with open(filename) as f:
				file=f.readline().split(' ')
				# mm=min(mm,len(file))
				# print(mm)
				result[str(i)+'-'+str(j)+'-value-'+str(k)]=file[:201]
result.to_csv('result.csv')

