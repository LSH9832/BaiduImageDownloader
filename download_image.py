import requests
import json
import os

from time import time, sleep
from glob import glob


class BaiduImageDownloader:

    keyword = "dog"
    image_num = 30
    save_path = "D:/ImageSpider"

    start_url = 'https://image.baidu.com/search/acjson?'
    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
    }

    param = {
        'tn': 'resultjson_com',
        'logid': ' 7517080705015306512',
        'ipn': 'rj',
        'ct': '201326592',
        'is': '',
        'fp': 'result',
        'queryWord': keyword,
        'cl': '2',
        'lm': '-1',
        'ie': 'utf-8',
        'oe': 'utf-8',
        'adpicid': '',
        'st': '',
        'z': '',
        'ic': '',
        'hd': '',
        'latest': '',
        'copyright': '',
        'word': keyword,
        's': '',
        'se': '',
        'tab': '',
        'width': '',
        'height': '',
        'face': '',
        'istype': '',
        'qc': '',
        'nc': '1',
        'fr': '',
        'expermode': '',
        'force': '',
        'cg': 'star',
        'pn': 1,
        'rn': '30',
        'gsm': '1e',
    }

    def __init__(self, keyword="dog", image_num=30, save_path="./images", max_rate=3, resume=True):
        self.keyword = keyword
        self.param["queryWord"] = keyword
        self.param["word"] = keyword
        self.image_num = image_num
        self.max_rate = max_rate
        self.resume = resume
        self.save_path = save_path

    def start(self):
        dist_dir = os.path.join(self.save_path, self.keyword)
        os.makedirs(dist_dir, exist_ok=1)
        exist_image_num = len(glob(os.path.join(dist_dir, "*.jpg")))
        start_time = last_time = time()
        now_image_num = 0

        while now_image_num < self.image_num:

            image_urls = []
            self.param["pn"] = now_image_num + exist_image_num if self.resume else 0
            try_time = 5
            success = False
            while try_time > 0:
                try:
                    print("Keyword: %s" % self.keyword)
                    print("request for image url... ", end="")
                    response = requests.get(url=self.start_url, headers=self.header, params=self.param)
                    success = True
                    print("success.\n")
                    break
                except:
                    if try_time > 0:
                        print("network error")
                        try_time -= 1
                        sleep(1)
            if not success:
                print("please check your network")
                exit(-1)
            response.encoding = 'utf-8'
            response = response.text
            data_s = json.loads(response.replace("\\\"", "'").replace("\\", "/"))
            a = data_s["data"]

            for i in range(len(a) - 1):
                data = a[i].get("thumbURL", "not exist")
                image_urls.append(data)

            for image_src in image_urls:
                try_time = 5
                success = False
                image_data = None
                while try_time > 0:
                    try:

                        # rate control
                        while time() - last_time <= 1. / self.max_rate:
                            pass
                        last_time = time()

                        image_data = requests.get(url=image_src, headers=self.header).content
                        now_image_num += 1
                        success = True if image_data is not None else False
                        break
                    except:
                        if try_time > 0:
                            print("network error, wait for 1 sec and start try (rest time: ")
                            try_time -= 1
                            sleep(1)
                if success and image_data is not None:

                    image_name = "%s.jpg" % str(now_image_num + exist_image_num).zfill(8)
                    image_path = os.path.join(dist_dir, image_name)
                    with open(image_path, 'wb') as f:  # 保存数据
                        f.write(image_data)
                        print("\r%s/%s: Image saved to %s" % (str(now_image_num).zfill(len(str(self.image_num))),
                                                              str(self.image_num),
                                                              os.path.abspath(image_path).replace("\\", "/")), end="")
                        f.close()

                if now_image_num >= self.image_num:
                    print("\n\nDownloading finished. Time cost: %.2fs" % (time() - start_time))
                    break


if __name__ == '__main__':

    import argparse

    def create_args():
        parser = argparse.ArgumentParser("Image Downloader")
        parser.add_argument("-k", "--keyword", type=str, default="哈士奇", help="input your keyword here")
        parser.add_argument("-n", "--number", type=int, default=10, help="input downloading image number here.")
        parser.add_argument("-p", "--path", type=str, default="./images", help="root dir for saving images")
        parser.add_argument("-r", "--rate", type=int, default=3, help="input downloading rate here(images per second).")
        parser.add_argument("--reset", action="store_true", help="network image searching index "
                                                                 "start from 0 rather than from "
                                                                 "image number of this keyword you have downloaded + 1")
        return parser.parse_args()

    args = create_args()
    downloader = BaiduImageDownloader(
        keyword=args.keyword,
        image_num=args.number,
        max_rate=args.rate,
        resume=not args.reset
    )

    downloader.start()
