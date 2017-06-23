"""

Usage:
  query_data_from_perfherder.py [--query-signatures] [--interval=<str>] [--keyword=<str>] [--browser-type=<str>] [--platform=<str>] [--suite-name=<str>] [--begin-date=<str>] [--end-date=<str>]
  query_data_from_perfherder.py (-h | --help)

Options:
  -h --help                 Show this screen.
  --query-signatures        Query signatures
  --interval=<str>          Query interval default is last 14 days [default: i]
  --keyword=<str>           Query by app name [default: all]
  --browser-type=<str>      Query by browser type [default: all]
  --platform=<str>          Query by platform [default: all]
  --suite-name=<str>        Query by suite name [default: all]
  --begin-date=<str>        Query by begin date [default: all]
  --end-date=<str>          Query by end date [default: all]
"""
import os
import json
import copy
import time
import urllib2
from docopt import docopt
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import plotly.plotly as py
import plotly.graph_objs as go

DEFAULT_QUERY_OPTION = "all"
DEFAULT_HASAL_SIGNATURES = "hasal_perfherder_signatures.json"
DEFAULT_HASAL_FRAMEWORK_NO = 9
DEFAULT_PERFHERDER_PRODUCTION_URL = "https://treeherder.mozilla.org"
DEFAULT_PERFHERDER_STAGE_URL = "https://treeherder.allizom.org"
PROJECT_NAME_MOZILLA_CENTRAL = "mozilla-central"
API_URL_QUERY_SIGNATURE_LIST = "%s/api/project/%s/performance/signatures/?format=json&framework=%s"
API_URL_QUERY_DATA = "%s/api/project/%s/performance/data/?format=json&framework=%s&interval=%s&signatures=%s"

MAX_MACHINE = 2
MAX_BROWSER = 2
MAX_SUITE = 20
MAX_DATE = 40

machine_table = {'windows8-64':0, 'windows10-64':1}
browser_table = {'firefox': 0,'chrome':1}
suite_table = {
    "amazon_ail_hover_related_product_thumbnail Median" : 0,
    "amazon_ail_select_search_suggestion Median" : 1,
    "amazon_ail_type_in_search_field Median" : 2,
    "facebook_ail_click_open_chat_tab_emoji Median" : 3,
    "facebook_ail_click_open_chat_tab Median" : 4,
    "facebook_ail_click_close_chat_tab Median" : 5,
    "facebook_ail_click_photo_viewer_right_arrow Median" : 6,
    "facebook_ail_scroll_home_1_txt Median" : 7,
    "facebook_ail_type_comment_1_txt Median" : 8,
    "facebook_ail_type_composerbox_1_txt Median" : 9,
    "facebook_ail_type_message_1_txt Median" : 10,
    "gmail_ail_compose_new_mail_via_keyboard Median" : 11,
    "gmail_ail_open_mail Median" : 12,
    "gmail_ail_reply_mail Median" : 13,
    "gmail_ail_type_in_reply_field Median" : 14,
    "gsearch_ail_select_image_cat Median" : 15,
    "gsearch_ail_select_search_suggestion Median" : 16,
    "gsearch_ail_type_searchbox Median" : 17,
    "youtube_ail_select_search_suggestion Median" : 18,
    "youtube_ail_type_in_search_field Median" : 19
}
date_table = {
    "2017-01-19":0,
    "2017-02-02":1,
    "2017-02-16":2,
    "2017-03-02":3,
    "2017-03-16":4,
    "2017-03-30":5,
    "2017-04-13":6,
    "2017-04-27":7,
    "2017-05-11":8,
    "2017-05-25":9,
    "2017-06-01":10,
    "2017-06-02":11,
    "2017-06-03":12,
    "2017-06-04":13,
    "2017-06-05":14,
    "2017-06-06":15,
    "2017-06-07":16,
    "2017-06-08":17,
    "2017-06-09":18,
    "2017-06-10":19,
    "2017-06-11":20,
    "2017-06-12":21,
    "2017-06-13":22,
    "2017-06-14":23,
    "2017-06-15":24,
    "2017-06-16":25,
    "2017-06-17":26,
    "2017-06-18":27,
    "2017-06-19":28,
    "2017-06-20":29,
    "2017-06-21":30,
    "2017-06-22":31,
    "2017-06-23":32,
    "2017-06-24":33,
    "2017-06-25":34,
    "2017-06-26":35,
    "2017-06-27":36,
    "2017-06-28":37,
    "2017-06-29":38,
    "2017-06-30":39
}

date_table_array = [
    "2017/01/19",
    "2017/02/02",
    "2017/02/16",
    "2017/03/02",
    "2017/03/16",
    "2017/03/30",
    "2017/04/13",
    "2017/04/27",
    "2017/05/11",
    "2017/05/25",
    "2017/06/01",
    "2017/06/02",
    "2017/06/03",
    "2017/06/04",
    "2017/06/05",
    "2017/06/06",
    "2017/06/07",
    "2017/06/08",
    "2017/06/09",
    "2017/06/10",
    "2017/06/11",
    "2017/06/12",
    "2017/06/13",
    "2017/06/14",
    "2017/06/15",
    "2017/06/16",
    "2017/06/17",
    "2017/06/18",
    "2017/06/19",
    "2017/06/20",
    "2017/06/21",
    "2017/06/22",
    "2017/06/23",
    "2017/06/24",
    "2017/06/25",
    "2017/06/26",
    "2017/06/27",
    "2017/06/28",
    "2017/06/29",
    "2017/06/30"
]

suite_table_array = [
    "amazon_ail_hover_related_product_thumbnail Median",
    "amazon_ail_select_search_suggestion Median",
    "amazon_ail_type_in_search_field Median",
    "facebook_ail_click_open_chat_tab_emoji Median",
    "facebook_ail_click_open_chat_tab Median",
    "facebook_ail_click_close_chat_tab Median",
    "facebook_ail_click_photo_viewer_right_arrow Median",
    "facebook_ail_scroll_home_1_txt Median",
    "facebook_ail_type_comment_1_txt Median",
    "facebook_ail_type_composerbox_1_txt Median",
    "facebook_ail_type_message_1_txt Median",
    "gmail_ail_compose_new_mail_via_keyboard Median",
    "gmail_ail_open_mail Median",
    "gmail_ail_reply_mail Median",
    "gmail_ail_type_in_reply_field Median",
    "gsearch_ail_select_image_cat Median",
    "gsearch_ail_select_search_suggestion Median",
    "gsearch_ail_type_searchbox Median",
    "youtube_ail_select_search_suggestion Median",
    "youtube_ail_type_in_search_field Median"
]

myColorscale = [
        [0, 'rgb(255, 255, 255)'],
        [6, 'rgb(0, 0, 255)'],
        [7, 'rgb(0, 0, 128)']
    ],

class QueryData(object):
    def __init__(self):
        self.total_count_table = np.zeros((MAX_MACHINE,MAX_BROWSER,MAX_SUITE,MAX_DATE), dtype=np.int)

    # def plot_data(self):
    #     a = self.total_count_table[machine_table[self.mp], browser_table[self.br],:,:]
    #     print a.shape
    #     plt.imshow(a, cmap='hot', interpolation='nearest')
    #     plt.show()

    def plot_data(self):
        mp_list = ['windows8-64', 'windows10-64']
        br = 'firefox'

        for mp in mp_list:
            data = [
                go.Heatmap(
                    z=self.total_count_table[machine_table[mp], browser_table[br],:,:],
                    x=date_table_array,
                    y=suite_table_array,
                    colorscale='Electric',
                )
            ]

            layout = go.Layout(
                title='Hasal Count {} {}'.format(mp,br),
                xaxis = dict(ticks='', nticks=36),
                yaxis = dict(ticks='' )
            )

            fig = go.Figure(data=data, layout=layout)
            py.plot(fig, filename='hasal-heatmap-{}-{}'.format(mp,br))

    def count_data(self, input_json, signature_data, b_date, e_date):
        b_timestamp = 0.0
        e_timestamp = 0.0
        try:
            if b_date != DEFAULT_QUERY_OPTION:
                b_date_obj = datetime.strptime(b_date, '%Y-%m-%d')
                b_timestamp = time.mktime(b_date_obj.timetuple())
            if e_date != DEFAULT_QUERY_OPTION:
                e_date_obj = datetime.strptime(e_date, '%Y-%m-%d')
                e_timestamp = time.mktime(e_date_obj.timetuple())
        except ValueError:
            print "Incorrect data format, should be YYYY-MM-DD!!, the begin_date and end_date filter will be ignored!"
        for sig in input_json:
            for data in input_json[sig]:
                _s = signature_data['signature_data'][sig]['suite_name']
                _b = signature_data['signature_data'][sig]['browser_type']
                _m = signature_data['signature_data'][sig]['machine_platform']
                _dt = datetime.fromtimestamp(data['push_timestamp']).strftime("%Y-%m-%d")
                _da = data['value']

                if b_timestamp != 0.0:
                    if e_timestamp != 0.0:
                        if b_timestamp <= data['push_timestamp'] <= e_timestamp:
                            if _s in suite_table.keys() and _dt in date_table.keys():
                                self.total_count_table[machine_table[_m]][browser_table[_b]][suite_table[_s]][date_table[_dt]] += 1
                    else:
                        if b_timestamp <= data['push_timestamp']:
                            if b_timestamp <= data['push_timestamp'] <= e_timestamp:
                                if _s in suite_table.keys() and _dt in date_table.keys():
                                    self.total_count_table[machine_table[_m]][browser_table[_b]][suite_table[_s]][date_table[_dt]] += 1
                else:
                    if e_timestamp != 0.0:
                        if data['push_timestamp'] <= e_timestamp:
                            if _s in suite_table.keys() and _dt in date_table.keys():
                                self.total_count_table[machine_table[_m]][browser_table[_b]][suite_table[_s]][date_table[_dt]] += 1

                    else:
                        if _s in suite_table.keys() and _dt in date_table.keys():
                            self.total_count_table[machine_table[_m]][browser_table[_b]][suite_table[_s]][date_table[_dt]] += 1


    def send_url_data(self, url_str):
        DEFAULT_URL_HEADER = {'User-Agent': "Hasal Query Perfherder Tool"}
        request_obj = urllib2.Request(url_str, headers=DEFAULT_URL_HEADER)
        try:
            response_obj = urllib2.urlopen(request_obj)
        except Exception as e:
            print "Send post data failed, error message [%s]" % e.message
            return None
        if response_obj.getcode() == 200:
            return response_obj
        else:
            print "response status code is [%d]" % response_obj.getcode()
            return None

    def query_signatures(self):
        url_str = API_URL_QUERY_SIGNATURE_LIST % (DEFAULT_PERFHERDER_PRODUCTION_URL, PROJECT_NAME_MOZILLA_CENTRAL, str(DEFAULT_HASAL_FRAMEWORK_NO))
        return_result = {'signature_data': {}, 'suite_list': [], 'browser_type_list': [], 'machine_platform_list': []}
        json_obj = None
        query_obj = self.send_url_data(url_str)
        if query_obj:
            json_obj = json.loads(query_obj.read())
        if json_obj:
            for revision in json_obj.keys():
                if 'test' not in json_obj[revision] and 'parent_signature' not in json_obj[revision] and 'has_subtests' in json_obj[revision]:
                    suite_name = json_obj[revision]['suite'].strip()
                    browser_type = json_obj[revision]['extra_options'][0].strip()
                    machine_platform = json_obj[revision]['machine_platform'].strip()
                    return_result['signature_data'][revision] = {'suite_name': suite_name,
                                                                 'browser_type': browser_type,
                                                                 'machine_platform': machine_platform}
                    if suite_name not in return_result['suite_list']:
                        return_result['suite_list'].append(suite_name)
                    if browser_type not in return_result['browser_type_list']:
                        return_result['browser_type_list'].append(browser_type)
                    if machine_platform not in return_result['machine_platform_list']:
                        return_result['machine_platform_list'].append(machine_platform)
            with open(DEFAULT_HASAL_SIGNATURES, "w+") as fh:
                json.dump(return_result, fh)
        return return_result

    def get_signature_list(self, signature_data, input_keyword, input_btype, input_platform, input_suite_name):

        if input_btype != DEFAULT_QUERY_OPTION:
            btype_sig_list = [sig for sig, data in signature_data['signature_data'].items() if
                              data.get('browser_type').lower() == input_btype]
            if len(btype_sig_list) == 0:
                print "The current input browser type [%s] is not in support list [%s]" % (input_btype, signature_data['browser_type_list'])
                return None
        else:
            btype_sig_list = copy.deepcopy(signature_data['signature_data'].keys())

        if input_platform != DEFAULT_QUERY_OPTION:
            platform_sig_list = [sig for sig, data in signature_data['signature_data'].items() if
                                 data.get('machine_platform').lower() == input_platform]
            if len(platform_sig_list) == 0:
                print "The current input platform [%s] is not in support list [%s]" % (input_platform, signature_data['machine_platform_list'])
                return None
        else:
            platform_sig_list = copy.deepcopy(signature_data['signature_data'].keys())

        if input_suite_name != DEFAULT_QUERY_OPTION:
            suite_sig_list = [sig for sig, data in signature_data['signature_data'].items() if
                              data.get('suite_name').lower() == input_suite_name]
            if len(suite_sig_list) == 0:
                print "The current input suite [%s] is not in support list [%s]" % (input_suite_name, signature_data['suite_list'])
                return None
        else:
            suite_sig_list = copy.deepcopy(signature_data['signature_data'].keys())

        if input_keyword != DEFAULT_QUERY_OPTION:
            suite_list = [suite_name.lower() for suite_name in signature_data['suite_list'] if input_keyword in suite_name.lower()]
            keyword_sig_list = [sig for sig, data in signature_data['signature_data'].items() if data.get('suite_name').lower() in suite_list]
        else:
            keyword_sig_list = copy.deepcopy(signature_data['signature_data'].keys())

        return list(set(btype_sig_list) & set(platform_sig_list) & set(suite_sig_list) & set(keyword_sig_list))

    def print_data(self, input_json, signature_data, b_date, e_date):
        b_timestamp = 0.0
        e_timestamp = 0.0
        try:
            if b_date != DEFAULT_QUERY_OPTION:
                b_date_obj = datetime.strptime(b_date, '%Y-%m-%d')
                b_timestamp = time.mktime(b_date_obj.timetuple())
            if e_date != DEFAULT_QUERY_OPTION:
                e_date_obj = datetime.strptime(e_date, '%Y-%m-%d')
                e_timestamp = time.mktime(e_date_obj.timetuple())
        except ValueError:
            print "Incorrect data format, should be YYYY-MM-DD!!, the begin_date and end_date filter will be ignored!"
        for sig in input_json:
            for data in input_json[sig]:
                if b_timestamp != 0.0:
                    if e_timestamp != 0.0:
                        if b_timestamp <= data['push_timestamp'] <= e_timestamp:
                            print '{:50s} {:10s} {:20s} {:30s}  {:20f}'.format(
                                signature_data['signature_data'][sig]['suite_name'],
                                signature_data['signature_data'][sig]['browser_type'],
                                signature_data['signature_data'][sig]['machine_platform'],
                                datetime.fromtimestamp(data['push_timestamp']).strftime("%Y-%m-%d %H-%M-%S-%f"),
                                data['value'])
                    else:
                        if b_timestamp <= data['push_timestamp']:
                            print '{:50s} {:10s} {:20s} {:30s}  {:20f}'.format(
                                signature_data['signature_data'][sig]['suite_name'],
                                signature_data['signature_data'][sig]['browser_type'],
                                signature_data['signature_data'][sig]['machine_platform'],
                                datetime.fromtimestamp(data['push_timestamp']).strftime("%Y-%m-%d %H-%M-%S-%f"),
                                data['value'])
                else:
                    if e_timestamp != 0.0:
                        if data['push_timestamp'] <= e_timestamp:
                            print '{:50s} {:10s} {:20s} {:30s}  {:20f}'.format(
                                signature_data['signature_data'][sig]['suite_name'],
                                signature_data['signature_data'][sig]['browser_type'],
                                signature_data['signature_data'][sig]['machine_platform'],
                                datetime.fromtimestamp(data['push_timestamp']).strftime("%Y-%m-%d %H-%M-%S-%f"),
                                data['value'])
                    else:
                        print '{:50s} {:10s} {:20s} {:30s}  {:20f}'.format(
                            signature_data['signature_data'][sig]['suite_name'],
                            signature_data['signature_data'][sig]['browser_type'],
                            signature_data['signature_data'][sig]['machine_platform'],
                            datetime.fromtimestamp(data['push_timestamp']).strftime("%Y-%m-%d %H-%M-%S-%f"),
                            data['value'])

    def query_data(self, query_interval, query_keyword, query_btype, query_platform, query_suite_name, query_begin_date, query_end_date):
        if not os.path.exists(DEFAULT_HASAL_SIGNATURES):
            signature_data = self.query_signatures()
        else:
            with open(DEFAULT_HASAL_SIGNATURES) as fh:
                signature_data = json.load(fh)

        signature_list = self.get_signature_list(signature_data, query_keyword.lower().strip(),
                                                 query_btype.lower().strip(), query_platform.lower().strip(),
                                                 query_suite_name.lower().strip())
        for signature in signature_list:
            url_str = API_URL_QUERY_DATA % (DEFAULT_PERFHERDER_PRODUCTION_URL, PROJECT_NAME_MOZILLA_CENTRAL, str(DEFAULT_HASAL_FRAMEWORK_NO), str(query_interval), signature)
            query_obj = self.send_url_data(url_str)
            if query_obj:
                json_obj = json.loads(query_obj.read())
                # self.print_data(json_obj, signature_data, query_begin_date.strip(), query_end_date.strip())
                self.count_data(json_obj, signature_data, query_begin_date.strip(), query_end_date.strip())

def main():

    arguments = docopt(__doc__)
    query_data_obj = QueryData()
    if arguments['--query-signatures']:
        query_data_obj.query_signatures()
    else:
        query_data_obj.query_data(arguments['--interval'], arguments['--keyword'], arguments['--browser-type'],
                                  arguments['--platform'], arguments['--suite-name'], arguments['--begin-date'], arguments['--end-date'])
        query_data_obj.plot_data()

if __name__ == '__main__':
    main()