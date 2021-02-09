
# -*- coding: utf-8 -*-
from requests import Session
import re
import os
import sys
import json
import time

class Douyin_API:



    HEADERS= {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'upgrade-insecure-requests': '1',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
        }
    Max_Tring=100

    def __init__(self):
        self.req=Session()

    #获取用户Sec_Id,后续都会用到
    def get_sec_uid(self, url):
        rep= self.req.get(url, headers=self.HEADERS,allow_redirects=False)
        if rep.status_code==302:
            loc=rep.headers['location']
            sec_uid = re.search(r'sec_uid=.*?\&', loc).group(0)
            print(sec_uid)
            return sec_uid[8:-1]
        return None
        
    #获取用户信息，直接保存到json，返回用户作品数量，便于校验是否已经完全下载    
    def get_user_info(self,sec_uid,share_url=''):
        url='https://www.iesdouyin.com/web/api/v2/user/info/?sec_uid='+sec_uid
        rep= self.req.get(url, headers=self.HEADERS,allow_redirects=False)
        aweme_count=0
        if rep.status_code==200:
            js=json.loads(rep.text)
            if 'user_info'in js: 
                js_author=[]
                if os.path.exists('data/list_author.json'):    
                    js_author=json.load(open('data/list_author.json','r',encoding='utf-8'))
                author_filter=list(filter(lambda x: x['author_uid'] == js['user_info']['uid'], js_author))                 
                if 'aweme_count' in js['user_info']:
                    aweme_count=js['user_info']['aweme_count']
                if len(author_filter)==0:
                    js_author.append({
                            'share_url':share_url,
                            'author_uid': js['user_info']['uid'],
                            'author_sec_uid': sec_uid, 
                            'nickname': js['user_info']['nickname'],
                            'author_unique_id': js['user_info']['unique_id'],
                            'aweme_count':aweme_count,
                            'firstfinished':0
                        })
                    json.dump(js_author,open('data/list_author.json','w',encoding='utf-8'),ensure_ascii=False, indent=4)

        return aweme_count
    #获取本次存储的用户清单
    def get_user_info_local(self): 
        if os.path.exists('data/list_author.json'):    
            js_author=json.load(open('data/list_author.json','r',encoding='utf-8'))
            return js_author
        return []

    #根据vid获取用户的信息
    def get_user_info_by_uid(self,uid):
        js_author=[]
        nickname=''
        if os.path.exists('data/list_author.json'):    
            js_author=json.load(open('data/list_author.json','r',encoding='utf-8'))
        for au in js_author:
            if au['author_uid']==uid:
                nickname=au['nickname']
                break
        return nickname    


        
    #根据视频id转换实际播放地址
    def get_video_url_by_vid(self,vid):
        url='https://aweme.snssdk.com/aweme/v1/playwm/?video_id={0}&ratio=720p&line=0'
        url='https://aweme.snssdk.com/aweme/v1/play/?video_id={0}&ratio=720p&line=0'
        url=url.format(vid)
        rep= self.req.get(url, headers=self.HEADERS,allow_redirects=False)
        if rep.status_code==302:
            loc=rep.headers['location']
            return loc
        return None
        


    
    #根据secid下载服务器上的所有视频
    def get_video_list_by_secid(self,sec_uid):
        max_cursor = 0
        has_more = True  
        total_count = 0
        firstfinished=0        
        #判断当前是否已经存储了服务器上的所有视频
        now_count=0
        remote_count=self.get_user_info(sec_uid)  
        if os.path.exists('data/list_video.json'):
            js_video=json.load(open('data/list_video.json','r',encoding='utf-8'))
            now_count=len(list(filter(lambda x: x['author_sec_uid'] == sec_uid, js_video)))
            
        if os.path.exists('data/list_author.json'):    
            js_author=json.load(open('data/list_author.json','r',encoding='utf-8'))
        for au in js_author:
            if au['author_sec_uid']==sec_uid:
                firstfinished=au['firstfinished']
                break
                
        while has_more and remote_count>now_count:
            nickname, video_list, max_cursor, has_more = self.get_video_list_once(sec_uid, max_cursor)
            page_count = len(video_list)
            total_count = total_count + page_count
            #print('{0}视频下载中 本页共有{1}个作品 累计{2}个作品 翻页标识:{3} 是否还有更多内容:{4}\r'.format(sec_uid,page_count, total_count, max_cursor, has_more))
            hasSaved,now_count=self.save_video_list(video_list)
            
            if hasSaved==1 and firstfinished==1:
                break
        for au in js_author:
            if au['author_sec_uid']==sec_uid:
                au['firstfinished']=1
                au['aweme_count']=now_count
                break
        json.dump(js_author,open('data/list_author.json','w',encoding='utf-8'),ensure_ascii=False, indent=4)
     

    #获取直播热榜用户清单

    def get_hotsearch_user(self):
        url='https://webcast.amemv.com/webcast/ranklist/hot/'
        para={
                'device_platform': 'android',
                'version_name': '13.2.0',
                'version_code': '130200',
                'aid': '1128'
            } 
        rep=self.req.get(url, params=para)
        #print(rep.text)
        js=json.loads(rep.text)
        if 'data' in js and 'ranks' in js['data']:
            for rk in js['data']['ranks']:
                if 'label' not in rk or rk['label'] not in ('舞蹈','美食','音乐'):
                    continue
                if 'user'in rk and 'sec_uid' in rk['user']:
                    self.get_user_info(rk['user']['sec_uid'])
    #获取热门榜单视频
    def get_hotsearch_video(self):
        url='https://www.iesdouyin.com/web/api/v2/hotsearch/billboard/aweme/'
        rep=self.req.get(url,headers=self.HEADERS)
        js=json.loads(rep.text)
        video_list=[]
        if 'aweme_list' in js:
            for aweme in js['aweme_list']:
                if 'aweme_info'in aweme and 'aweme_id' in aweme['aweme_info'] and 'video' in aweme['aweme_info']:
                    v={
                        'desc':aweme['aweme_info']['desc'],
                        'url': aweme['aweme_info']['video']['play_addr']['url_list'][0],
                        'aweme_id':aweme['aweme_info']['aweme_id'],
                        'vid':aweme['aweme_info']['video']['vid'],
                        'cover_uri':aweme['aweme_info']['video']['dynamic_cover']['uri'],
                        'cover_url':aweme['aweme_info']['video']['dynamic_cover']['url_list'][0] if len(aweme['aweme_info']['video']['dynamic_cover']['url_list'])>0 else None,
                        'author_uid':aweme['aweme_info']['author']['uid'],
                        'author_sec_uid':'',
                        'author_unique_id':'',
                        'nickname' : aweme['aweme_info']['author']['nickname'] if re.sub(r'[\/:*?"<>|]', '', aweme['aweme_info']['author']['nickname']) else None,
                        'played':0
                    }
                    video_list.append(v)
            self.save_video_list(video_list)
        
    #获取用户的某一页视频清单
    def get_video_list_once(self, sec_uid, max_cursor):
        user_url_prefix = 'https://www.iesdouyin.com/web/api/v2/aweme/post/?sec_uid={0}&max_cursor={1}&count=2000'
 
        i = 0
        result = []
        has_more = False
        while result == []:
            i = i + 1
            #sys.stdout.write('---解析视频链接中 正在第 {} 次尝试...\r'.format(str(i)))
            #sys.stdout.flush()

            user_url = user_url_prefix.format(sec_uid, max_cursor)
            response = self.req.get(user_url,headers=self.HEADERS)
            html = json.loads(response.text)


            if len(html['aweme_list'])>0:
               
                #with open ("video_list.txt",'w',encoding='utf-8') as f:
                #    json.dump(html,f,ensure_ascii=False, indent=4)
                max_cursor = html['max_cursor']
                has_more = bool(html['has_more'])
                result = html['aweme_list']
            if i>self.Max_Tring:
                break
        # print(result)
        nickname = None
        video_list = []
        for item in result:
            if nickname is None:
                nickname = item['author']['nickname'] if re.sub(r'[\/:*?"<>|]', '', item['author']['nickname']) else None
 
            video_list.append({
                'desc': re.sub(r'[\/:*?"<>|]', '', item['desc']) if item['desc'] else '无标题' + str(int(time.time())),
                'url': item['video']['play_addr']['url_list'][0],
                'aweme_id':item['aweme_id'],
                'vid':item['video']['vid'],
                'cover_uri':item['video']['dynamic_cover']['uri'],
                'cover_url':item['video']['dynamic_cover']['url_list'][0] if len(item['video']['dynamic_cover']['url_list'])>0 else None,
                'author_uid':item['author']['uid'],
                'author_sec_uid':item['author']['sec_uid'],
                'author_unique_id':item['author']['unique_id'],
                'nickname' : item['author']['nickname'] if re.sub(r'[\/:*?"<>|]', '', item['author']['nickname']) else None,
                'played':0
            })
        #print(video_list)        
        return nickname, video_list, max_cursor, has_more
        
        
        
    #将视频信息保存到json文件    
    def save_video_list(self,video_list):
        js_video=[]
        js_author=[]
        hasSaved=0
        sec_uid=''
        
        if not os.path.exists('data'):
            os.makedirs('data')
        if os.path.exists('data/list_video.json'):
            js_video=json.load(open('data/list_video.json','r',encoding='utf-8'))
        if os.path.exists('data/list_author.json'):
            js_author=json.load(open('data/list_author.json','r',encoding='utf-8'))
        for v in video_list:
            aweme_id=v['aweme_id']
            sec_uid=v['author_sec_uid']
            awe_filter=list(filter(lambda x: x['aweme_id'] == aweme_id, js_video))
            if len(awe_filter)==0:
                js_video.append({
                    'desc': v['desc'],
                    #'url':  v['url'],
                    'aweme_id': v['aweme_id'],
                    'vid': v['vid'],
                    'cover_uri': v['cover_uri'],
                    'cover_url': v['cover_url'],
                    'author_uid': v['author_uid'],
                    'author_sec_uid': v['author_sec_uid'], 
                    'played':0
                })  
            else:
                hasSaved=1
            author_filter=list(filter(lambda x: x['author_uid'] == v['author_uid'], js_author))
            if  len(author_filter)==0 and v['author_sec_uid']!='':
                js_author.append({
                    'author_uid': v['author_uid'],
                    'author_sec_uid': v['author_sec_uid'], 
                    'nickname': v['nickname'],
                    'author_unique_id': v['author_unique_id'],
                    'firstfinished':0
                })
        now_count=len(list(filter(lambda x: x['author_sec_uid'] == sec_uid, js_video)))
        js_video.sort(key=lambda k: k['aweme_id'], reverse=True)
        json.dump(js_video,open('data/list_video.json','w',encoding='utf-8'),ensure_ascii=False, indent=4)
        json.dump(js_author,open('data/list_author.json','w',encoding='utf-8'),ensure_ascii=False, indent=4)
        return hasSaved,now_count 

    #获取要展示的视频列表
    def get_video_list_local(self,index,page_count,author_uid):
        js_video=[]       
        if os.path.exists('data/list_video.json'):
            js_video=json.load(open('data/list_video.json','r',encoding='utf-8'))
        js_video.sort(key=lambda k: k['aweme_id'], reverse=True)
        if author_uid!='':
            js_video=list(filter(lambda x: x['author_uid'] == author_uid, js_video))
        s_index=index*page_count
        e_index=(index+1)*page_count
        if len(js_video)<e_index:
            s_index=len(js_video)-page_count if len(js_video)>page_count else 0
            e_index=len(js_video)
        return js_video[s_index:e_index]
    
    #获取下一个视频的播放地址
    #direction方向，0代表初始化，1代表向下，-1代表向上
    def get_next_video_local(self,nowvid,direction=1):
        
        js_video=[]
        vid=''
        url=''
        author_uid=''
        author_nickname=''
        v_date=''
        if os.path.exists('data/list_video.json'):
            js_video=json.load(open('data/list_video.json','r',encoding='utf-8'))
        #js_video.sort(key=lambda k: k['aweme_id'], reverse=True)
        for r in range(0,len(js_video)):
            v=js_video[r]
            
            if direction==0:
                if v['played']==0:
                    vid=v['vid']
                    url=self.get_video_url_by_vid(v['vid'])
                    author_uid=v['author_uid']
                    author_nickname=self.get_user_info_by_uid(v['author_uid'])
                    v_date=self.get_date_from_cover(v['cover_uri'])
                    break
            elif v['vid']==nowvid:
                if direction==1:
                    for i in range(r+1,len(js_video)):
                        if js_video[i]['played']==0:  
                            v=js_video[i]
                            vid=v['vid']
                            url=self.get_video_url_by_vid(v['vid'])
                            author_uid=v['author_uid']
                            author_nickname=self.get_user_info_by_uid(v['author_uid'])
                            v_date=self.get_date_from_cover(v['cover_uri'])
                            break
                             
                elif direction==-1:
                    for i in range(r-1,len(js_video),-1): 
                            v=js_video[i]
                            vid=v['vid']
                            url=self.get_video_url_by_vid(v['vid'])
                            author_uid=v['author_uid']
                            author_nickname=self.get_user_info_by_uid(v['author_uid'])
                            v_date=self.get_date_from_cover(v['cover_uri'])
                            break
        if vid=='' and len(js_video)>0:
                   v=js_video[0]
                   vid=v['vid']
                   url=self.get_video_url_by_vid(v['vid'])
                   author_uid=v['author_uid']
                   author_nickname=self.get_user_info_by_uid(v['author_uid'])
                   v_date=self.get_date_from_cover(v['cover_uri'])        
            
        return  vid,url,author_uid,author_nickname,v_date
    
    #下载封面用于展示
    def down_cover(self,cover_uri,cover_url):
    
        if not os.path.exists('cache'):
            os.makedirs('cache')
        rep=self.req.get(cover_url, headers=self.HEADERS)
        with open('cache/'+cover_uri.replace('/','_')+'.jpg','wb') as f:
            f.write(rep.content)
    #下载无水印的视频
    def down_video(self,aweme_id):
        jx_url  = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids='+aweme_id    #官方接口
        js = json.loads(self.req.get(url = jx_url,headers=headers).text)
        video_url = str(js['item_list'][0]['video']['play_addr']['url_list'][0]).replace('playwm','play')   #去水印后链接
        
    #更新播放清单状态，对于已经播放过的置为1        
    def update_play_status(self,vid):
        js_video=[]       
        if os.path.exists('data/list_video.json'):
            js_video=json.load(open('data/list_video.json','r',encoding='utf-8'))
        for v in js_video:
            if v['vid']==vid:
                v['played']=1
                break
        json.dump(js_video,open('data/list_video.json','w',encoding='utf-8'),ensure_ascii=False, indent=4)  
        
    #更新用户本地保存的视频链接数量
    def update_user_aweme_count(self):
        js_author=[]
        js_video=[] 
        if os.path.exists('data/list_author.json'):    
            js_author=json.load(open('data/list_author.json','r',encoding='utf-8'))
        if os.path.exists('data/list_video.json'):
            js_video=json.load(open('data/list_video.json','r',encoding='utf-8'))
        for au in js_author:
            now_count=len(list(filter(lambda x: x['author_sec_uid'] == au['author_sec_uid'], js_video)))
            au['aweme_count']=now_count
        json.dump(js_author,open('data/list_author.json','w',encoding='utf-8'),ensure_ascii=False, indent=4)  
    
    #清理用户视频，不在用户列表中的视频均被删除
    def clean_video_without_user(self):
        js_author=[]
        js_video=[] 
        js_video_new=[]
        if os.path.exists('data/list_author.json'):    
            js_author=json.load(open('data/list_author.json','r',encoding='utf-8'))
        if os.path.exists('data/list_video.json'):
            js_video=json.load(open('data/list_video.json','r',encoding='utf-8'))
        au_list=[]
        for au in js_author:
            au_list.append(au['author_uid'])
        for v in js_video:
            if v['author_sec_uid'] =='' or v['author_uid'] in au_list:
                js_video_new.append(v)

        json.dump(js_video_new,open('data/list_video.json','w',encoding='utf-8'),ensure_ascii=False, indent=4)              
    def write_log(self,mesg):
        with open('Douyin.log','a',encoding='utf-8') as f:
            f.write(mesg)
    def get_resource_path(self,relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)
    def get_date_from_cover(self,cover_uri):
        try:
            timeStamp=cover_uri[cover_uri.find('_')+1:]
            timeArray = time.localtime(timeStamp)
            otherStyleTime = time.strftime("%Y%m%d", timeArray)
            return otherStyleTime
        except Exception as e:
            return time.strftime("%Y%m%d", time.localtime())
if __name__ == '__main__':
    d=Douyin_API()
    user_url='MS4wLjABAAAA6cLFP6uL4NmSxtnd9miQb-9S6GweLvikkmvKKFUT74A'
    d.get_hotsearch_user()
    #d.get_list_by_uid('786859763961483')
