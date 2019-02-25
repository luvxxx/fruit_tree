import argparse
import pipeline_v2 as pipeline
import sys

def cmd_arguments():
  parser = argparse.ArgumentParser(description='''
  functions:
  operate DIVA pipeline.
  ''', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument('--video_lst_file',dest='video_lst_file', type=str,  help='''
  the path of video list, in this file each line is the relative path of the video to the video_dir. 
  That is, video_file_path = os.path.join(video_dir, ${line})
  ''')
  # parser.add_argument('--out_dir',dest='out_dir', type=str, help='''
  # the root directory of outputs: 
  # ''')
  parser.register('type', 'bool', str2bool)
  parser.add_argument('--test', dest='test', type='bool', default=True, help='''enable for testing''')
  args = parser.parse_args()
  return args

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    if v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def do_job(args):
  if args.test:
    pipeline.testing(args.video_lst_file)
  else:
    pipeline.main(args.video_lst_file)

def main():
  args = cmd_arguments()
  do_job(args)
  sys.exit()

if __name__ == '__main__':
  main()