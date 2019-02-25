# parameters
import os
import sys
import time
from Dockermodel import Dockermodel
from Guavalogger import Guavalogger
## all dockermodel yaml
import config.config_yaml
dockermodels, conf = config.config_yaml.init()

## log
conf_log = conf.get('log')
timestamp = str(int(time.time()))
conf_log['DB_CONFIG']['dbname'] = conf_log.get('DB_CONFIG').get(
    'dbname', 'unkown_pipeline') + '_' + timestamp
conf_log['FILE_CONFIG']['directory'] = conf_log.get('FILE_CONFIG').get(
    'directory', 'unkown_pipeline') + '_' + timestamp

## log for process-log
PROC_CONFIG = conf_log['PROC_CONFIG']
URL = PROC_CONFIG.get('URL')
del PROC_CONFIG

## dockermodels &  pipeline [only sequence-pipeline for now]
models = {}
prepipeline = conf.get('pipeline').get('preprocess')
for dm_name in prepipeline:
    models[dm_name] = Dockermodel(dockermodels.get(dm_name), conf_log)
del dm_name

pipename = conf.get('pipeline').get('name')
pipeline = conf.get('pipeline').get('sequence')
for dm_name in pipeline:
    models[dm_name] = Dockermodel(dockermodels.get(dm_name), conf_log)
del dm_name

## directory, e.g. DATA_DIR = dirs.get('DATA_DIR')
conf_dirs = conf.get('directory')

## parallel initialization
PLL = conf.get('parallel')
GPUS = {v: False for v in conf.get('nvida_docker').get('NV_GPU')}
WORKER_NUM = PLL.get('WORKER_NUM')
real_WORKER_NUM = min(len(GPUS), WORKER_NUM)
is_parallel = conf.get('pipeline').get('parallel')

## docker-image-hub
REG_HOST = conf.get('registry')

## test
TEST = PLL.get('test')

## all dockermodels script
from config.dockermodels import *

# ------------------ ------------------ ------------------ ------------------ 

def init_models():
    '''pull model from private registry if not exist'''
    for model in models:
        if not model.exist():
            model.pull(REG_HOST)
    for pmodel in premodels:
        if not pmodel.exist():
            pmodel.pull(REG_HOST)
    return True


def init_dir():
    '''init local log dir'''
    current_path = os.path.split(os.path.realpath(__file__))[0]
    checkdir(os.sep.join([current_path, conf_log['FILE_CONFIG']['directory']]), 'pre_out_dir', 0)


def checkdir(ext_frames_dir, type_str, verbose=0):
    if not os.path.exists(ext_frames_dir):
        if verbose:
            sys.stderr.write("INIT: mkdir %r:%r\n" % (type_str, ext_frames_dir))
        os.makedirs(ext_frames_dir)
        return 1
    return 2


def creat_logger(vid, mid, config):
    '''create new logger only for  project'''
    if not vid: vid = ''
    info = {'vid': vid, 'mid': mid}
    key = str(vid) + '_' + str(mid)

    # root = logging.getLogger()
    # map(root.removeHandler, root.handlers[:])
    # map(root.removeFilter, root.filters[:])
    if config.get('FLAG') == 'FILE':
        logfile = key + '.log'
        DATA_DIR = conf_dirs.get('DATA_DIR')
        config.get('FILE_CONFIG').update({'filename': logfile})
        config.get('FILE_CONFIG').update({'name': 'log_'+key})
        init_dir()
        logger = Guavalogger(config)
    elif config.get('FLAG') == 'DB':
        # update to VID + MID
        vidmid = key.replace('.', '_')
        config.get('DB_CONFIG').update({'name': 'log_'+ key})
        config.get('DB_CONFIG').update({'collection': vidmid})
        logger = Guavalogger(config)
    return logger


# def create_vid_lst(DATA_DIR, video):
    # with open(os.sep.join([DATA_DIR, str(video) + '.lst']), 'w') as e:
        # e.write(str(video) + '.avi')
    # e.close()


# def create_vid_dir(DATA_DIR, model_name, video):
#     dir1 = os.sep.join([DATA_DIR, model_name, video])
#     checkdir(dir1, 'pre_out_dir', 0)

