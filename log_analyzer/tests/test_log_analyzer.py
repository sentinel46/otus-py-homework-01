#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import log_analyzer
import re
import unittest


class TestLogAnalyzer(unittest.TestCase):

    def test_update_config(self):
        file_name = "./config.cfg"
        file_config = {"param1": "value1", "param2": "2"}
        with open(file_name, "w") as config_file:
            json.dump(file_config, config_file)

        config = {"param1": "test", "param2": "test"}
        config = log_analyzer.update_config(file_name, config)
        self.assertEqual(file_config, config)
        os.remove("./config.cfg")

    def test_find_last_log_file(self):
        # last file is plane
        file_names = ["./nginx-access-ui.log-20101010",    "./nginx-access-ui.log-20101015",
                      "./nginx-access-ui.log-20101016",    "./nginx-access-ui.log-20101009.gz",
                      "./nginx-access-ui.log-20101011.gz", "./nginx-access-ui.log-20101012.gz",
                      "./nginx-access-ui.log-20101018.7z", "./nginx-access-ui.log-20101016.zip",
                      "./nginx-access-ui.log-20101017.rar"]
        for file_name in file_names:
            open(file_name, "w").close()

        pattern = re.compile(".*nginx-access-ui\.log-(?P<date>\d{8})(\.gz)?$")
        log_file_name, timestamp = log_analyzer.find_last_log_file(pattern)
        self.assertEqual(log_file_name, "./nginx-access-ui.log-20101016")
        self.assertEqual(timestamp, "20101016")

        # last file is gz
        gz_file = "./nginx-access-ui.log-20101017.gz"
        open(gz_file, "w").close()

        log_file_name, timestamp = log_analyzer.find_last_log_file(pattern)
        self.assertEqual(log_file_name, gz_file)
        self.assertEqual(timestamp, "20101017")

        # without any files
        for file_name in file_names:
            os.remove(file_name)
        os.remove(gz_file)

        result = log_analyzer.find_last_log_file(pattern)
        self.assertIsNone(result)

    def test_parse_log_file(self):
        file_name = "test.log"
        with open(file_name, "w") as log:
            log.write("""1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/25019354 HTTP/1.1" 200 927 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-2190034393-4708-9752759" "dc7161be3" 0.390
1.99.174.176 3b81f63526fa8  - [29/Jun/2017:03:50:22 +0300] "GET /api/1/photogenic_banners/list/?server_name=WIN7RB4 HTTP/1.1" 200 12 "-" "Python-urllib/2.7" "-" "1498697422-32900793-4708-9752770" "-" 0.133
1.169.137.128 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/16852664 HTTP/1.1" 200 19415 "-" "Slotovod" "-" "1498697422-2118016444-4708-9752769" "712e90144abee9" 0.199
1.199.4.96 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/slot/4705/groups HTTP/1.1" 200 2613 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-3800516057-4708-9752745" "2a828197ae235b0b3cb" 0.704
1.202.56.176 -  - [29/Jun/2017:09:48:16 +0300] "0" 400 166 "-" "-" "-" "-" "-" 0.005
1.168.65.96 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/internal/banner/24294027/info HTTP/1.1" 200 407 "-" "-" "-" "1498697422-2539198130-4709-9928846" "89f7f1be37d" 0.146
1.169.137.128 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/group/1769230/banners HTTP/1.1" 200 1020 "-" "Configovod" "-" "1498697422-2118016444-4708-9752747" "712e90144abee9" 0.628
1.194.135.240 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/group/7786679/statistic/sites/?date_type=day&date_from=2017-06-28&date_to=2017-06-28 HTTP/1.1" 200 22 "-" "python-requests/2.13.0" "-" "1498697422-3979856266-4708-9752772" "8a7741a54297568b" 0.067
1.169.137.128 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/1717161 HTTP/1.1" 200 2116 "-" "Slotovod" "-" "1498697422-2118016444-4708-9752771" "712e90144abee9" 0.138
1.166.85.48 -  - [29/Jun/2017:03:50:22 +0300] "GET /export/appinstall_raw/2017-06-29/ HTTP/1.0" 200 28358 "-" "Mozilla/5.0 (Windows; U; Windows NT 6.0; ru; rv:1.9.0.12) Gecko/2009070611 Firefox/3.0.12 (.NET CLR 3.5.30729)" "-" "-" "-" 0.003
1.199.4.96 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/slot/4822/groups HTTP/1.1" 200 22 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-3800516057-4708-9752773" "2a828197ae235b0b3cb" 0.157""")

        pattern = re.compile(
            "(?P<remote_addr>.+)\s+(?P<remote_user>.+)\s+(?P<http_x_real_ip>.+)\s+\[(?P<time_local>.+)\]\s+" \
            "\"[A-Z]{1,} (?P<request>.+) .*\"\s+(?P<status>.+)\s+(?P<body_bytes_send>.+)\s+" \
            "\"(?P<http_referer>.+)\"\s+\"(?P<http_user_agent>.+)\"\s+\"(?P<http_x_forwarded_for>.+)\"\s+" \
            "\"(?P<http_X_REQUEST_ID>.+)\"\s+\"(?P<http_X_RB_USER>.+)\"\s+(?P<request_time>.+)")

        url_stats, info = log_analyzer.parse_log_file(pattern, file_name, 0.1)
        self.assertEqual(info["total"], 11)
        self.assertEqual(info["succeed"], 10)
        self.assertEqual(info["total_time"], 2.565)

        # out of ERROR_RATE
        with open(file_name, "w+") as log:
            log.write("""1.202.56.176 -  - [29/Jun/2017:09:48:16 +0300] "0" 400 166 "-" "-" "-" "-" "-" 0.005""")

        result = log_analyzer.parse_log_file(pattern, file_name, 0.1)
        self.assertIsNone(result)

        os.remove(file_name)


if __name__ == "__main__":
    unittest.main()
