import os
import re
import smtplib
import sys
import time
from email.mime.text import MIMEText
from email.utils import formataddr

import feedparser
import requests

import wget
import ssl
import datetime


requests.packages.urllib3.disable_warnings()


ok_code = [200, 201, 202, 203, 204, 205, 206]

# 邮箱域名过滤列表
blackhole_list = ["cnr.cn", "cyberpolice.cn", "gov.cn", "samr.gov.cn", "12321.cn"
                  "miit.gov.cn", "chinatcc.gov.cn"]



def write_log(content, level="INFO"):
    date_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    update_log = f"[{date_str}] [{level}] {content}\n"
    print(update_log)
    with open(f'./log/{time.strftime("%Y-%m", time.localtime(time.time()))}-update.log', 'a', encoding="utf-8") as f:
        f.write(update_log)


def gbk_trans_utf8(file_path):
    with open(file_path, 'r', encoding='gbk') as f:
        content = f.read()
    with open(file_path, 'w', encoding='utf8') as f:
        f.write(content)

def replase_4_reg(file_path):
    with open(file_path, 'r', encoding='utf8') as f:
        content = f.read()
    content = re.sub(r'\?', '', content, count=0, flags=0)
    content = re.sub(r' ([\d]),', '\\1,', content, count=0, flags=0)
    content = re.sub(r' ([\d])\n', '\\1\n', content, count=0, flags=0)
    with open(file_path, 'w', encoding='utf8') as f:
        f.write(content)

def get_subscribe_url():
    dirs = './subscribe/base-subscribe'
    if not os.path.exists(dirs):
        os.makedirs(dirs)
    log_dir = "./log"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    rss = feedparser.parse('https://www.cfmem.com/feeds/posts/default?alt=rss')
    entries = rss.get("entries")
    if not entries:
        write_log("更新失败！无法拉取原网站内容", "ERROR")
        return
    update_list = []
    summary = entries[0].get("summary")
    if not summary:
        write_log("暂时没有可用的订阅更新", "WARN")
        return
    v2ray_list = re.findall(r"v2ray订阅链接：(.*?)</span>", summary)
    # 获取普通订阅链接
    if any(v2ray_list):
        v2ray_url = v2ray_list[-1].replace('amp;', '')
        v2ray_req = requests.request("GET", v2ray_url, verify=False)
        v2ray_code = v2ray_req.status_code
        if v2ray_code not in ok_code:
            write_log(f"获取 v2ray 订阅失败：{v2ray_url} - {v2ray_code}", "WARN")
        else:
            update_list.append(f"v2ray: {v2ray_code}")
            with open(dirs + '/v2ray.txt', 'w', encoding="utf-8") as f:
                f.write(v2ray_req.text)
    clash_list = re.findall(r"clash订阅链接：(.*?)</span>", summary)
    # 获取clash订阅链接
    if any(clash_list):
        clash_url = clash_list[-1].replace('amp;', '')
        clash_req = requests.request("GET", clash_url, verify=False)
        clash_code = clash_req.status_code
        if clash_code not in ok_code:
            write_log(f"获取 clash 订阅失败：{clash_url} - {clash_code}", "WARN")
        else:
            update_list.append(f"clash: {clash_code}")
            with open(dirs + '/clash.yml', 'w', encoding="utf-8") as f:
                clash_content = clash_req.content.decode("utf-8")
                f.write(clash_content)
    if update_list:
        file_pat = re.compile(r"v2ray\.txt|clash\.yml")
        if file_pat.search(os.popen("git status").read()):
            write_log(f"更新成功：{update_list}", "INFO")
        else:
            write_log(f"订阅暂未更新", "WARN")
    else:
        write_log(f"未能获取新的更新内容", "WARN")


def get_open_runner_url():
    dirs = './subscribe/openRunner'
    if not os.path.exists(dirs):
        os.makedirs(dirs)
    log_dir = "./log"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    dt = datetime.date.today()

    urlv2 = 'https://free.datiya.com/uploads/'+dt.strftime('%Y%m%d')+'-v2ray.txt'
    urlclash = 'https://free.datiya.com/uploads/'+dt.strftime('%Y%m%d')+'-clash.yaml'
    print(urlv2)
    print(urlclash)
    v2 = requests.get(urlv2)
    clash = requests.get(urlclash)
    with open(f'./subscribe/openRunner/v2ray.txt','wb') as v2f:
      v2f.write(v2.content)
      v2f.close
  
    with open(f'./subscribe/openRunner/clash.yml','wb') as clashf:
      clashf.write(clash.content)
      clashf.close
      gbk_trans_utf8(f'./subscribe/openRunner/clash.yml')
      replase_4_reg(f'./subscribe/openRunner/clash.yml')

#def get_


def main():
    get_subscribe_url()
    get_open_runner_url()
    #merge_all_files()


# 主函数入口
if __name__ == '__main__':
    main()
