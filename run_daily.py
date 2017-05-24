#!/usr/local/bin/python3.5
import scheduled
# 注意：插入的群聊必须在部署后手动在群内发一次信息，否则搜索不到对应群
groups = ['A', '20170424']

for i in groups:
	scheduled.run(i)
