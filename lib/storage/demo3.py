# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/12/30 下午1:22
# @Author : lipeng
# @Email : 523038391@qq.com
# @File : demo3.py
# @Project : wecharmer
import json
import time

import requests


users=["admin","liuhll","lanchong","shixiaogang","shiliqun","xuhaojie","louye","xiangliufang","qianzhengchao","loushanshan","meitingxia","zhangyue","yangqi","zhuliqin","tianxueqi","shaosinan","wanglongquan","lailianfei","jiyaiqian","xumiaomiao","yinshushan","yangsien","quanfang","loubeiying","chenxinyao","yutingting","zhuhuifang","liuxiaoyu","zhangqiyuan","dujingjing","liyanming","guanxiaohong","zhanxiaoqing","zhouliyun","sunwen","huhuan","shiqiuling","chenxiaozheng","guolvye","jiangyan","zhouhongbo","minniannian","jiangyang","zhaoxueting","gangmingxin","huokunping","cuinianming","chenlin","wangrencui","caihuan","zhanmengyao","caisu","wangwanting","feibi","huwaizubaoxiaozhanghao","yuhua","wulianxiang","zhangxindi","licong","zengluxiang","emingli","qinyihang","zhangshuaishuai","weitingting","wangfang","liaoliqing","zhangdi","baotingting","liuwenfang","ningyanping","xiongjie","tangyiwen","guoyingying","xieyanghui","xuwei","tangli","chenlili","lijin","helingjun","liuyuxuan","xuda","shichengyu","liuxiaonan","xiongpengcheng","xiexingxing","zhongwanyu","chenfangting","wangzhaohui","tongrujin","panrenwei","mengyuan","shiqichen","suwan","shenluzan","zhangxingyuan","qiumeifang","lvhaomiao","lixinyi","tongshengbo","hanjiaojiao","wangqiong","chencanxing","wudanqi","chenzehua","weibingfan","zhangpeiwen","wangmengyao","huoyaiqiong","tangbiao","chenkeyun","ouyangbin","yuqiaohui","wangxiaozhi","hujun","xuesisen","hejiandong","xiekai","huangzixin","zhouying","hongmin","zhouzhenyu","hujianhui","wangling","zhangfuzhou","jiangshan","xuliyan","guojunnan","lingyibo","qiaochun","yaoshanying","tangqingqing","luopengcheng","haiqimeng","zhaoyunyang","wanghongqin","pinghuan","liyufeng","yesuqin","zhiyanru","shencaihong","zhangchenkai","peishaofei","zhashuangjie","zoufuping","gehuaiqiao","chenwangen","zhangjing","huhaiyan","dongqianqian","xueliqiong","renliqing","huangyaohua","hanjunhui","jiaben","qirongxiang","zhouxingchen","changyufei","wufan","xiangzheng","wangbowen","liujunnan","hejingyi","liaoliangbing","lichao","wangsimin","hemingzhu","zoujunyu","lizuo","tianneirisu","zhangkenuo","rayma","alecding","emory","hongjujian","jiangshengbo","renxiaoyu","yuki","wanghong","yangjipeng","jijie","wujianfei","zhulingjin","yangrusong","zhuweifeng","yangxiaomin","lixiaozhen","chenqianwen","zhouxiaoxia","xujiancheng","zhouchi","chenshimin","longjun","linyuanyuan","zhangping","zenghuimin","zhuxiayong","jinpei","fengjiangling","baoxiangyun","maruili","wanghui","liuxuewei","yuyihong","Shirley","hululu","shenqingbo","quguangyue","huangchen","chenyong","xiaoxia","oujinnian","xuyuan","zhangqianwen","job","wzqt","fengmeihan","hzds","hzds1","tzhj","guoqing","xiaoping","wangshuo","linshali","ajlb","wuhongjun","chenyutao","chenxinru","ajxh","zhangluyi","luyuhang","zhangzhenqiang","cxhy","nblx","zjhy","zjmx","kkxx","wczz","nyx","zjqd","jlhw","hnby","shly","gzydm","jylr","jxlm","bln","clml","szfxn","wjkt","szkl","sxtax","hnhy","zjlt","shnh","shym","sddr","jxlc","lbbb","zsqc","jxpb","qzyf","hzwk","chwyy","fshc","ywms","lhjy","gzks","zhouqiaoting","yanxiaojun","yuqianchun","sushenghong","lhzx","zjgy","jcxx","kongyoujun","wangxinjing","yupingping","zhujun","maoliping","czhw","123","snzj","hzlb","hzlj","hzrd","dlm","rxd","sjzwf","txsks","dhyl","zjmc","zjkp","kpww","dingshiyu","yangmin","guangrong","zxwj","jhgm","pfdq","ljgm","bygm","obgm","xyld","ktby","yhbl","lihui","chenbinnan","jsxx","ajmy","jiangsanmao","zhaolanying","songbince","luaiqin","qiaolu","tangbirong","chaiwenjian","yuling","dszzh","ymzzh","xiongxiaoming","sdds","hzln","shizhuyu","chenpeng","pjqz","yyjf","hanqin","huangbuwei","zhangping1","loulibo","caizhimei","tangguanming","luwenqing","zhuyun","limingjun","yubilian","fzjx","xujingyang","gcceshi","guanzhengxin","pengkaifeng","wangxiaohua","qihaiqiang","tanglei","maruiyi","sunyumeng","sunyumeng","lishengyang","liling","zhonglijun","dgkc","ajhq","shihaiying","zhoujunyan","lmjk","xuxiaolong","czlx","xhm","zzds","adf","wangshiyou","louxiaoli","liwanjun","wangdongli","FZCLC","xinmeng","wangbin","nbmh","fzceshi","yfzzh","dengwang","yuxiaoyu","yanlingling","chengjieru","lffs","wangchong","kphw","huyingying","chenzhipeng","dlcm","jxkr","yxjf","xiaowenpan","zenghanglei","sdsh","wycz","likeying","luningning","wangqian","sjgy","wangsiwei","ssmz","limengxing","weizhaolu","liujiaxin","xuqiaoting","yujing","zhangyuehan","yangjing","hmqs","yyfs","lczzh","pengwanqing","chenweijian","wanglingling","tongcong","yangyinli","pyld","tanyanlu","jiangfumin","liangcaixing","xujinhua","qiuyili","RANCHO","liuzhenxian","tanjing","luorui","jiqiong","xujiamin","lcjk","wangyaning","yaoyifen","lipeng","xiongting","dfbz","xjbz","bjjyt","chamengdan","yugaohan","zhangrenxuan","huangfeng","zhaotiantian","pengmiaoxia","guowenjing","gaoyongen","zhuyongqiang","lijuan","shenminglei","test","kupu","yuxingxing","zhangyaoyu","zhugeshuntu","yangyijing","zhouliang","jiangyuyan","gengzhimin","lishihao","chenyafang","fenghuayu","qiuchengjuan","mjt","huangpingping","nbmy","hzyx","hxfs","liangfalin","chenjianyong","ylljf","mjn","yanfan","jianchongyang","lvsinuo","panhaiyun","luxinyuan","yangxiuqin","zhangpingwen","heenhui","dckj","wuchenxi","yanghuiting","liuke","chenfabing","xutenglong","jyfs","pjjh","yuanminjuan","meiling","nbqz","shixiaojian","zhangxinwei","hanweijun","smjj","ajbj","wanglebing","xyfzp","wanhaichuan","liuyongchao","zhugenlei","chenweifang","chenziyi","wangzhihong","xuyeru","wangjie","yangjunyao","zangchen","hxzzh","dgqh","lushuaishuai","qiufeifei","oufangjie","dyygm","liyunke","yaominghua","zhouyaoyao","ramy","dmjj","aszn","yfzn","syjj","glgd","jszn","dysy","wyhw","yfxx","ksxx","machengxiao","pengzhi","chenjiahao","weipeng","caoxinyu","tanziyu","zhaozhiwei","hyxx","dingzuohao","duantingrui","syfz","hankebing","fangbo","wangkaiqian","ajwl","ajzb","gaoguiyou","mxhw","ylgy","liuquanhai","linhuiying","gaochao","lihushan","zhengyuanqin","wangtao","mbsy","dqjj","songmenghui","tuidan","ltfs","mayezhu","kpgm","lvlingjie","wangxiao","yubangwei","fanglinling","wanghaijie","lijianan","zhangyujie","wangfeifen","heling","xuanran","tianhaiyuan","yrjj","wangguoqing","klkfs","hsyy","wangshiya","lwjtd","liuchunlin","zhujiao","xuluqiang","zhangwei","yuhaitao","zhenghaoyang","hjfs","yjhjj","shuxiaofang","huazhiwen","liruijie","sunjing","bnmny","wangqinglang","zhangyongshun","hujie","Daniel","zhenghuang","yhfz","zhangxinchi","klsgm","swsy","hqb","liwanting","xujinwei","hxzzh2","zhuyucui","zhuyihui","fuyingying","lumenglan","xiangyuqi","guoyingying3","hfjp","lushengkai","renxiaoyu6061","jiangshengbo6061","zhuchenchen","wanghaochen","linchao","wangmeng","huangyue","lvshenying","weijingshan","gaoshimin","zhangwanchun","chenmenglu","chaipengfei","hanweijun6061","shuwenyai","liuyongchao6061","dengyangming","liujie","fangchen","xukai","chenmingyong","lizengmei","liuyihang","chenhaidi","wangxinyu","jiaoxixi","xieshanshan","xuyuyue","bishenglei","linwenxin","maxinru","luningning6061","jack","feikaiguo","wangdaiye","huanghaihui","zhangkai","xuxiaolong6061","liangcaixing6061","pengjianjun","rita","tanglei6061","jasonwang","liuqiong","liuke6061","amy","wushixun","chenzhe","zhangying","yqfs","fangyutong","xuyichen","ajzy","tangjiayu","zhengying","shenqi","maping","anhuilin","wujun","sunweihao","qiuzexin","liandinghua","luxiaowei","liwenbo","wangxiaojie","wanxin","yeziyin","zoulifang","linjinjin","zhangkaijie","chenwan","shenxinran","huyao","kpgmrb","kpgmbs","lanlan","wuyuemeng","lxwj","lhly","sgqs","dongsi","xichange","miaojiaojiao","gaofei","zhangyidan","huijiangang","hzba","ceshi","yuziqiu","liuzhangyu"]
newusers=[]


for user in users :
    # 登录
    url = "https://erp.wecharmer.com/proxy/account/login"

    payload = {
        "tenantName": "Wecharmer.Hero",
        "account": user,
        "password": "Aa123456!"
    }
    resp = requests.post(url=url, json=payload)
    us=json.loads(resp.text)
    print(us)
    time.sleep(1)

    if us["code"]== "Success" :
        newusers.append(user)


print(newusers)






