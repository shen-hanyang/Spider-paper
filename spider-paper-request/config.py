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
        parser.add_argument('--conference', type=str, default='NeurIPS')
        parser.add_argument('--year', type=str, default='2024')
        parser.add_argument('--level', type=str, default='poster')
        parser.add_argument('--url', type=str, default=f"https://api2.openreview.net/notes?content.venue=")
        
        # Time
        parser.add_argument('--start_time', type=int, default=5)
        parser.add_argument('--stop_time', type=int, default=10)
        parser.add_argument('--timeout', type=int, default=20)
        
        # Data Save
        parser.add_argument('--save_json', type=str, default='./data/')
        parser.add_argument('--save_pics', type=str, default='./data/')
                
        args = parser.parse_args()
        
        # Pre-Process
        args.save_json = args.save_json + args.conference + '/' + args.year + '/' + args.level + '/' + args.level + '.json'
        args.save_informations = args.save_informations + args.conference + '/' + args.year + '/' + args.level + '/' + args.level + '_informations.csv'
        args.save_pics = args.save_pics + args.conference + '/' + args.year + '/' + args.level + '/assets/'

        args.url = 'https://api2.openreview.net/notes?content.venue=MM2023%20Poster&details=replyCount%2Cpresentation&domain=acmmm.org%2FACMMM%2F2023%2FConference&limit=1000&offset=0'
        # args.url = 'https://api2.openreview.net/notes?content.venue=ICML%202022%20OralPoster&details=replyCount%2Cpresentation&domain=ICML.cc%2F2023%2FConference&invitation=ICML.cc%2F2023%2FConference%2F-%2FSubmission&limit=1000&offset=0'
        # args.url = 'https://api.openreview.net/notes?content.venue=NeurIPS+2021+Spotlight&details=replyCount&offset=0&limit=1000&invitation=NeurIPS.cc%2F2021%2FConference%2F-%2FBlind_Submission'
        # args.url = 'https://api.openreview.net/notes?content.venue=NeurIPS+2022+Accept&details=replyCount&offset=0&limit=1000&invitation=NeurIPS.cc%2F2022%2FConference%2F-%2FBlind_Submission'
        # args.url = 'https://api.openreview.net/notes?content.venue=ICLR+2023+Poster&details=replyCount&offset=0&limit=1000&invitation=ICLR.cc%2F2023%2FConference%2F-%2FBlind_Submission'
        # args.url = 'https://api.openreview.net/notes?content.venue=ICLR+2023+poster&details=replyCount&offset=0&limit=1000&invitation=ICLR.cc%2F2023%2FConference%2F-%2FBlind_Submission'
        os.makedirs(args.save_pics, exist_ok=True)

        return args