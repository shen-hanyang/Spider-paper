import argparse
import os

class Config():
    def __init__(self):
        args = self.__get_config()
        for key in args.__dict__:
            setattr(self, key, args.__dict__[key])
        
    def __get_config(self):
        parser = argparse.ArgumentParser(description='Data Config')
        
        # Data Source
        parser.add_argument('--conference', type=str, default='ICLR')
        parser.add_argument('--year', type=str, default='2024')
        parser.add_argument('--level', type=str, default='poster')
        parser.add_argument('--url', type=str, default=f'https://openreview.net/group?id=ICLR.cc/2024/Conference#tab-accept-')
        parser.add_argument('--executable_path', type=str, default='./driver/msedgedriver.exe')
        parser.add_argument('--_from', type=int, default=0)
        parser.add_argument('--num_browsers',type=int, default=5)
        parser.add_argument('--browser', type=str, default='edge')
        parser.add_argument('--check', type=int, default=1)
        
        # Time
        parser.add_argument('--wait_time', type=int, default=20)
        parser.add_argument('--timeout', type=int, default=20)
        
        # Data Save
        parser.add_argument('--save_urls', type=str, default='./data/')
        parser.add_argument('--save_informations', type=str, default='./data/')
        parser.add_argument('--save_pics', type=str, default='./data/')
        parser.add_argument('--no_get', type=str, default='./data/')
                
        args = parser.parse_args()
        
        # Pre-Process
        args.url = args.url + args.level
        args.save_urls = args.save_urls + args.conference + '/' + args.year + '/' + args.level + '/' + args.level + '_urls.txt'
        args.save_informations = args.save_informations + args.conference + '/' + args.year + '/' + args.level + '/' + args.level + '_informations.csv'
        args.save_pics = args.save_pics + args.conference + '/' + args.year + '/' + args.level + '/assets/'
        args.no_get = args.no_get + args.conference + '/' + args.year + '/' + args.level + '/' + args.level + '_no_get.txt'

        os.makedirs(os.path.dirname(args.save_urls), exist_ok=True)
        os.makedirs(os.path.dirname(args.no_get), exist_ok=True)
        os.makedirs(args.save_pics, exist_ok=True)
        
        return args