#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gevent
from gevent import monkey;
import timelib

monkey.patch_all()
from gevent.queue import JoinableQueue
from gevent.pool import Group
from gevent import Timeout
import sys
import json
import requests
from datetime import datetime
import MySQLdb
import traceback
import Logger

reload(sys)
sys.setdefaultencoding('utf8')

proxies = {
    'http': '127.0.0.1:8087'
}

PROXY_IP = '127.0.0.1'

headers = {
    'X-Forwarded-For': '%s, 127.0.0.1, 192.168.0.1' % PROXY_IP,
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.43 Safari/536.11'
}

#session = requests.session(headers=headers,proxies=proxies)
session = requests.session()

#################
HTTP_PREFIX = 'http://api.pgysocial.com/apiproxy/weibo/'
USER_SHOW = '2/users/show.json'
BI_FOLLOWERS = '2/friendships/friends/bilateral/ids.json'
FRIENDS = '2/friendships/friends/ids.json'
FRIENDS_INFO = '2/friendships/friends/ids.json'
FOLLOWERS_INFO = '2/friendships/followers.json'
TAGS = '2/tags.json'
USER_TIMELINE = '2/statuses/user_timeline.json'
COMMENTS_TIMELINE = '2/comments/show.json'
REPOST_TIMELINE = '2/statuses/repost_timeline.json'
#################
WEIBO_COMMENTS_PAGE_SIZE = 5
WEIBO_REPOSTS_PAGE_SIZE = 50
WEIBO_PAGE_SIZE = 20
FRIENDS_PAGE_SIZE = 5000
FOLLOWERS_PAGE_SIZE = 200
TAGS_PAGE_SIZE = 100
GREENLET_COUNT = 1
MAX_WAIT_TIME = 20000  # 20 seconds
SLEEP_TIME = 360

IS_NEED_COMMENTS_REPOSTS = 0
#################
users_fetch_queue = JoinableQueue()
comments_fetch_queue = JoinableQueue()
reposts_fetch_queue = JoinableQueue()
statuses_fetch_queue = JoinableQueue()

statuses = [] # store all user's status
comments = [] # store all status' comments
reposts = [] # store all status' repostes

#################
#TAGS
TAGS_INSERT_SQL = "insert ignore into `xio`.`tb_xweibo_user_tags`(`tid`, `uid`, `tag`) values (%s, %s, %s)"
#FRIENDSHIP
FRIENDS_INSERT_SQL = "insert ignore into `xio`.`tb_xweibo_friendship`(`uid`, `fid`) values (%s, %s)"
#WEIBO
WEIBO_INSERT_SQL = "insert ignore into `xio`.`tb_xweibo_info`(`wid`, `uid`, `text`, `source`, `created_at`, `comments`, `rt`, `retweeted_status_id`) values (%s , %s, %s, %s, %s, %s, %s, %s) ";
USER_INSERT_SQL = "insert ignore into `xio`.`tb_xweibo_user_info`(`uid`, `screen_name`, `name`, `province`, `city`, `location`, `description`, `profile_image_url`, `domain`, `gender`, `followers_count`, `friends_count`, `statuses_count`, `favourites_count`, `created_at`,  `verified`, `verified_type`, `verified_reason`, `bi_followers_count`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
FOLLOWERS_INSERT_SQL = "insert ignore into `xio`.`tb_xweibo_followers_info`(`uid`, `screen_name`, `name`, `province`, `city`, `location`, `description`, `profile_image_url`, `domain`, `gender`, `followers_count`, `friends_count`, `statuses_count`, `favourites_count`, `created_at`,  `verified`, `verified_type`, `verified_reason`, `bi_followers_count`, `follow_who`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
#COMMENTS
COMMENTS_WEIBO_INSERT_SQL = "insert ignore into `xio`.`tb_xweibo_comments_info`(`wid`, `uid`, `text`, `source`, `created_at`, `commented_status_id`) values (%s , %s, %s, %s, %s, %s) "
COMMENTS_USER_INSERT_SQL = "insert ignore into `xio`.`tb_xweibo_comments_user_info`(`uid`, `screen_name`, `name`, `province`, `city`, `location`, `description`, `profile_image_url`, `domain`, `gender`, `followers_count`, `friends_count`, `statuses_count`, `favourites_count`, `created_at`,  `verified`, `verified_type`, `verified_reason`, `bi_followers_count`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
#REPOSTS
REPOSTS_WEIBO_INSERT_SQL = "insert ignore into `xio`.`tb_xweibo_reposts_info`(`wid`, `uid`, `text`, `source`, `created_at`, `retweeted_status_id`) values (%s , %s, %s, %s, %s, %s) "
REPOSTS_USER_INSERT_SQL = "insert ignore into `xio`.`tb_xweibo_reposts_user_info`(`uid`, `screen_name`, `name`, `province`, `city`, `location`, `description`, `profile_image_url`, `domain`, `gender`, `followers_count`, `friends_count`, `statuses_count`, `favourites_count`, `created_at`,  `verified`, `verified_type`, `verified_reason`, `bi_followers_count`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

#################
task_group = Group()
# db = MySQLdb.connect(host='localhost', user='root', passwd='299792458', db='xio', charset='utf8')
db = MySQLdb.connect(host='localhost', user='root', passwd='299792458', db='xio', charset='utf8')
cursor = db.cursor(MySQLdb.cursors.DictCursor)
logger = Logger.getLogger("微博分析")


def _http_call(url):
    global session
    if session is None:
        session = requests.session()
    try:
        resp = session.get(url)
        resp.encoding = 'UTF-8'
        body = resp.text
        # print body
        return json.loads(body)
    except Exception:
        logger.error(traceback.format_exc())


def analyze():
    while not users_fetch_queue.empty():
        IS_NEED_REFETCH = False
        logger.info('系统剩余任务总数： ' + str(users_fetch_queue.qsize()))
        try:
            wait_time = Timeout(MAX_WAIT_TIME)
            wait_time.start()
            uid = users_fetch_queue.get()
            print 'UID: ' + str(uid)
            url = '%s%s?%s' % (HTTP_PREFIX, USER_SHOW, 'uid=%s' % uid)
            print url
            user = _http_call(url)
            #    url = '%s%s%s%s' % (HTTP_PREFIX, BI_FOLLOWERS, 'uid=%s&count=2000' % uid)
            #    bi_followers = _http_call(url)
            # url = '%s%s?%s' % (HTTP_PREFIX, TAGS, 'uid=%s&count=%d' % (uid, TAGS_PAGE_SIZE))
            #
            # tagset = _http_call(url)
            statuses_count = user.get('statuses_count')
            print '**************************************'
            print '名称 %s' % user.get('name')
            # print '微博数 %d' % statuses_count
            # print '互粉数 %d' % user.get('bi_followers_count')
            # print '粉丝数 %d' % user.get('followers_count')
            # print '关注数 %d' % user.get('friends_count')
            # print tagset
            # for item in tagset:
            #     for k, v in item.items():
            #         if k == 'weight':
            #             continue
            #         cursor.execute(TAGS_INSERT_SQL, (k, uid, v))
            #         break

            #FRIENDSHIP
            friendship_crawler(uid)
            # uids = followers_crawler(uid)
            # followers_tags_crawler(uids)


            # analyze status
            #            pages = statuses_count / WEIBO_PAGE_SIZE + 1

            # pages = 50
            # status_task_group = Group()
            # for _ in xrange(GREENLET_COUNT):
            #     status_task_group.spawn(statuses_crawler)
            #
            # for page in xrange(1, pages + 1):
            #     url = '%s%s?%s' % (
            #         HTTP_PREFIX, USER_TIMELINE, 'uid=%s&count=%d&page=%d&feature=1' % (uid, WEIBO_PAGE_SIZE, page))
            #     statuses_fetch_queue.put(url)
            #
            # status_task_group.join() #waiting for fetch complete
            #
            # #    print '账户微博抓取完毕，共 ' + str(len(statuses)) + ' 条'
            # gevent.sleep(0.0)

            if IS_NEED_COMMENTS_REPOSTS:
                print '抓取评论转发！'
                for _ in xrange(GREENLET_COUNT):
                    task_group.spawn(comments_crawler)
                    task_group.spawn(reposts_crawler)

                for status in statuses:
                    id = status.get('id')
                    print 'status_id: ' + str(id)
                    comments_count = status.get('comments_count')
                    reposts_count = status.get('reposts_count')

                    comments_pages = (comments_count / WEIBO_COMMENTS_PAGE_SIZE) + 1
                    reposts_pages = (reposts_count / WEIBO_REPOSTS_PAGE_SIZE) + 1

                    #generate a fetch url and put it into the task queue
                    for page in xrange(1, comments_pages + 1):
                        url = '%s%s?%s' % (
                            HTTP_PREFIX, COMMENTS_TIMELINE,
                            'id=%s&count=%d&page=%d' % (id, WEIBO_COMMENTS_PAGE_SIZE, page))
                        comments_fetch_queue.put(url)
                    for page in xrange(1, reposts_pages + 1):
                        url = '%s%s?%s' % (
                            HTTP_PREFIX, REPOST_TIMELINE,
                            'id=%s&count=%d&page=%d' % (id, WEIBO_REPOSTS_PAGE_SIZE, page))
                        reposts_fetch_queue.put(url)

                task_group.join() #waiting for fetch complete
        except Timeout as t:
            if t is wait_time:
                IS_NEED_REFETCH = True
        except Exception:
            logger.error(traceback.format_exc())
            logger.error(user)
            if user.get('error_code') is None:
                IS_NEED_REFETCH = True
        finally:
            if not IS_NEED_REFETCH:
                wait_time.cancel()
                users_fetch_queue.task_done()
            else:
                logger.info('抓取失败，重新进入队列！')
                users_fetch_queue.put(uid)


def friendship_crawler(uid):
    try:
        url = '%s%s?%s' % (HTTP_PREFIX, FRIENDS, 'uid=%s&count=%d' % (uid, FRIENDS_PAGE_SIZE))
        #    print url
        friends = _http_call(url)
        friends_ids = friends['ids']
        logger.info('用户关注数量： ' + str(len(friends_ids)))
        for friend_id in friends_ids:
            cursor.execute(FRIENDS_INSERT_SQL, (uid, friend_id))
    except Exception:
        logger.error(traceback.format_exc())


'''
(`uid`, `screen_name`, `name`, `province`, `city`, `location`, `description`, `profile_image_url`, `domain`, `gender`, `followers_count`, `friends_count`, `statuses_count`, `favourites_count`, `created_at`,  `verified`, `verified_type`, `verified_reason`, `bi_followers_count`, 'follow_who')
'''


def followers_crawler(uid):
    try:
        uids = []
        for i in xrange(500):
            url = '%s%s?%s' % (
            HTTP_PREFIX, FOLLOWERS_INFO, 'uid=%s&count=%d&cursor=%d' % (uid, FOLLOWERS_PAGE_SIZE, i * 200))
            #    print url
            resp = _http_call(url)
            followers = resp.get('users', None)
            if followers:
                logger.info('用户粉丝数量： ' + str(len(followers)))
                for follower in followers:
                    user_params = (follower['id'],
                                   follower['screen_name'],
                                   follower['name'],
                                   follower['province'],
                                   follower['city'],
                                   follower['location'],
                                   follower['description'],
                                   follower['profile_image_url'],
                                   follower['domain'],
                                   follower['gender'],
                                   follower['followers_count'],
                                   follower['friends_count'],
                                   follower['statuses_count'],
                                   follower['favourites_count'],
                                   timelib.strtodatetime(follower['created_at']),
                                   1 if follower['verified'] else 0,
                                   follower['verified_type'],
                                   follower['verified_reason'],
                                   follower['bi_followers_count'],
                                   uid
                    )
                    uids.append(follower['id'])
                    cursor.execute(FOLLOWERS_INSERT_SQL, user_params)
            else:
                break
        return uids
    except Exception:
        logger.error(traceback.format_exc())


def followers_tags_crawler(uids):
    for uid in uids:
        url = '%s%s?%s' % (HTTP_PREFIX, TAGS, 'uid=%s&count=%d' % (uid, TAGS_PAGE_SIZE))
        tagset = _http_call(url)
        logger.info('抓取粉丝标签： ' + str(uid))
        for item in tagset:
            for k, v in item.items():
                print k, v
                if k == 'weight':
                    break
                cursor.execute(TAGS_INSERT_SQL, (k, uid, v))


def statuses_crawler():
    '''
    greenlet status crawler
    '''
    global statuses
    while not statuses_fetch_queue.empty():
        IS_NEED_REFETCH = False #when timeout or errors occur,put the url back into the task queue and the make sure the task is not set to done!
        try:
            wait_time = Timeout(MAX_WAIT_TIME)
            wait_time.start()
            url = statuses_fetch_queue.get()
            gevent.sleep(0.0)
            time_line = _http_call(url)
            for status in time_line['statuses']:
                weibo_created_at = datetime.strptime(status.get('created_at'), '%a %b %d %H:%M:%S +0800 %Y')
                user_created_at = datetime.strptime(status.get('user').get('created_at'), '%a %b %d %H:%M:%S +0800 %Y')
                retweeted_status_id = -1

                if status.get('retweeted_status') is not None:
                    retweeted_status = status['retweeted_status']
                    retweeted_weibo_created_at = datetime.strptime(retweeted_status.get('created_at'),
                                                                   '%a %b %d %H:%M:%S +0800 %Y')
                    retweeted_user_created_at = datetime.strptime(retweeted_status.get('user').get('created_at'),
                                                                  '%a %b %d %H:%M:%S +0800 %Y')
                    retweeted_status_id = retweeted_status['id']
                    retweeted_weibo_params = (
                        retweeted_status_id, retweeted_status['user']['id'], retweeted_status['text'], status['source'],
                        retweeted_weibo_created_at, retweeted_status['comments_count'],
                        retweeted_status['reposts_count'],
                        -1)
                    retweeted_user_params = (retweeted_status['user']['id'], retweeted_status['user']['screen_name'],
                                             retweeted_status['user']['name'], retweeted_status['user']['province'],
                                             retweeted_status['user']['city'], retweeted_status['user']['location'],
                                             retweeted_status['user']['description'],
                                             retweeted_status['user']['profile_image_url'],
                                             retweeted_status['user']['domain'], retweeted_status['user']['gender'],
                                             retweeted_status['user']['followers_count'],
                                             retweeted_status['user']['friends_count'],
                                             retweeted_status['user']['retweeted_statuses_count'],
                                             retweeted_status['user']['favourites_count'], retweeted_user_created_at,
                                             retweeted_status['user']['verified'],
                                             retweeted_status['user']['verified_type'],
                                             retweeted_status['user']['verified_reason'],
                                             retweeted_status['user']['bi_followers_count'] )
                    cursor.execute(WEIBO_INSERT_SQL, retweeted_weibo_params)
                    cursor.execute(USER_INSERT_SQL, retweeted_user_params)

                weibo_params = (status['id'], status['user']['id'], status['text'], status['source'], weibo_created_at,
                                status['comments_count'], status['reposts_count'], retweeted_status_id)
                user_params = (
                    status['user']['id'], status['user']['screen_name'], status['user']['name'],
                    status['user']['province'],
                    status['user']['city'], status['user']['location'], status['user']['description'],
                    status['user']['profile_image_url'], status['user']['domain'], status['user']['gender'],
                    status['user']['followers_count'], status['user']['friends_count'], status['user']['statuses_count']
                    ,
                    status['user']['favourites_count'], user_created_at, status['user']['verified'],
                    status['user']['verified_type'], status['user']['verified_reason'],
                    status['user']['bi_followers_count'] )
                cursor.execute(WEIBO_INSERT_SQL, weibo_params)
                cursor.execute(USER_INSERT_SQL, user_params)

                statuses.append(status)
        except Timeout as t:
            if t is wait_time:
            #                print '处理超时，等待重新抓取!'
                #put timeout url back into the task queue
                IS_NEED_REFETCH = True
                logger.error('超时！')
        except Exception:
            logger.error(traceback.format_exc())
            logger.error(time_line)
            if time_line.get('error_code') is not None:
                logger.info('IP超限，先休息一会儿。。。')
                IS_NEED_REFETCH = True
                gevent.sleep(SLEEP_TIME)
        finally:
            wait_time.cancel()
            if IS_NEED_REFETCH is not True:
                statuses_fetch_queue.task_done()
            #                print url + ' 抓取完成 --- 微博'
            else:
                statuses_fetch_queue.put(url)

#                print url + ' 抓取失败 --- 微博'

def comments_crawler():
    '''
    greenlet comments crawler
    '''
    while not comments_fetch_queue.empty():
        IS_NEED_REFETCH = False #when timeout or errors occur,put the url back into the task queue and the make sure the task is not set to done!
        try:
            wait_time = Timeout(MAX_WAIT_TIME)
            wait_time.start()
            url = comments_fetch_queue.get()
            gevent.sleep(0.0)
            comments_time = _http_call(url)
            for status in comments_time['comments']:
                if not status.get('deleted'):
                    weibo_created_at = datetime.strptime(status.get('created_at'), '%a %b %d %H:%M:%S +0800 %Y')
                    user_created_at = datetime.strptime(status.get('user').get('created_at'),
                                                        '%a %b %d %H:%M:%S +0800 %Y')
                    comments_status_id = -1

                    if status.get('status') is not None:
                        comments_status = status['status']
                        comments_status_id = comments_status['id']

                    weibo_params = (
                        status['id'], status['user']['id'], status['text'], status['source'], weibo_created_at,
                        comments_status_id)
                    user_params = (
                        status['user']['id'], status['user']['screen_name'], status['user']['name'],
                        status['user']['province'],
                        status['user']['city'], status['user']['location'], status['user']['description'],
                        status['user']['profile_image_url'], status['user']['domain'], status['user']['gender'],
                        status['user']['followers_count'], status['user']['friends_count'],
                        status['user']['statuses_count'],
                        status['user']['favourites_count'], user_created_at, status['user']['verified'],
                        status['user']['verified_type'], status['user']['verified_reason'],
                        status['user']['bi_followers_count'] )
                    cursor.execute(COMMENTS_WEIBO_INSERT_SQL, weibo_params)
                    cursor.execute(COMMENTS_USER_INSERT_SQL, user_params)

        except Timeout as t:
            if t is wait_time:
            #                print '处理超时，等待重新抓取!'
                #put timeout url back into the task queue
                IS_NEED_REFETCH = True
        except Exception:
            IS_NEED_REFETCH = True
            logger.error(traceback.format_exc())
        finally:
            wait_time.cancel()
            if IS_NEED_REFETCH is not True:
                comments_fetch_queue.task_done()
            #                print url + ' 抓取完成 --- 评论'
            else:
                comments_fetch_queue.put(url)

#                print url + ' 抓取失败 --- 评论'

def reposts_crawler():
    '''
    greenlet reposts crawler
    '''
    while not reposts_fetch_queue.empty():
        IS_NEED_REFETCH = False #when timeout or errors occur,put the url back into the task queue and the make sure the task is not set to done!
        try:
            wait_time = Timeout(MAX_WAIT_TIME)
            wait_time.start()
            url = reposts_fetch_queue.get()
            gevent.sleep(0.0)
            reposts_time = _http_call(url)
            for status in reposts_time['reposts']:
                if not status.get('deleted'):
                    weibo_created_at = datetime.strptime(status.get('created_at'), '%a %b %d %H:%M:%S +0800 %Y')
                    user_created_at = datetime.strptime(status.get('user').get('created_at'),
                                                        '%a %b %d %H:%M:%S +0800 %Y')
                    reposts_status_id = -1

                    if status.get('retweeted_status') is not None:
                        reposts_status = status['retweeted_status']
                        reposts_status_id = reposts_status['id']

                    weibo_params = (
                        status['id'], status['user']['id'], status['text'], status['source'], weibo_created_at,
                        reposts_status_id)
                    user_params = (
                        status['user']['id'], status['user']['screen_name'], status['user']['name'],
                        status['user']['province'],
                        status['user']['city'], status['user']['location'], status['user']['description'],
                        status['user']['profile_image_url'], status['user']['domain'], status['user']['gender'],
                        status['user']['followers_count'], status['user']['friends_count'],
                        status['user']['statuses_count']
                        ,
                        status['user']['favourites_count'], user_created_at, status['user']['verified'],
                        status['user']['verified_type'], status['user']['verified_reason'],
                        status['user']['bi_followers_count'] )
                    cursor.execute(REPOSTS_WEIBO_INSERT_SQL, weibo_params)
                    cursor.execute(REPOSTS_USER_INSERT_SQL, user_params)
        except Timeout as t:
            if t is wait_time:
            #                print '处理超时，等待重新抓取!'
                #put timeout url back into the task queue
                IS_NEED_REFETCH = True
        except Exception as e:
            IS_NEED_REFETCH = True
            logger.error(traceback.format_exc())
        finally:
            wait_time.cancel()
            if IS_NEED_REFETCH is not True:
                reposts_fetch_queue.task_done()
            #                print url + ' 抓取完成 --- 转发'
            else:
                reposts_fetch_queue.put(url)
                print status
                print url + ' 抓取失败 --- 转发'


def _main():
    user_crawler_group = Group()

    for _ in xrange(GREENLET_COUNT):
        user_crawler_group.spawn(analyze)

    with open('ids.txt') as FILE:
        for line in FILE:
            id = line.strip()
            #            cursor.execute('SELECT COUNT(1) as total_count FROM tb_xweibo_user_info WHERE uid = %s' % id)
            #            result = cursor.fetchone()
            #            if not result['total_count']:
            users_fetch_queue.put(id)
    user_crawler_group.join()


if __name__ == '__main__':
#    main(sys.argv)
    _main()