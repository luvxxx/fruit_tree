## demo for pipline
## version: v2
## author allenlwh@gmail.com
## last modified 2017.10.06

import time
import os
import config
import parameters
from parameters import models, prepipeline, pipeline, pipename,is_parallel
from parameters import REG_HOST, URL, timestamp
from parameters import real_WORKER_NUM, PLL, GPUS
from ProcLogger import ProcLogger
from multiprocessing import Pool, cpu_count, Lock, current_process
from multiprocessing.dummy import Pool as ThreadPool



def init_prepipeline(videolist):
    '''pre-pipline, run web/ui dockermodels'''
    lock = Lock()
    DATA_DIR = parameters.conf_dirs.get('DATA_DIR')
    video_lst_file = os.sep.join([DATA_DIR, 'video.lst'])
    
    if not os.path.exists(video_lst_file):
        with open(video_lst_file, 'w') as e:
            for vid in videolist:
                e.write(str(vid) + '.avi\n')
        e.close()

    module_lst_file = os.sep.join([DATA_DIR, 'module.lst'])
    if not os.path.exists(module_lst_file):
        with open(module_lst_file, 'w') as e:
            for mid in pipeline:
                e.write(str(mid) + '\n')
        e.close()

    parameters.init_dir()

    for pi in prepipeline:
        model = models[pi]
        success = False
        if not model.exist():
            print('prepipeline:docker-img not exist: %s' % pi)
            break
        if model.status():
            success = True
            print('prepipeline:docker-img aleady running: %s' % pi)
            continue
        else:
            # attempt to running
            script = eval('config.dockermodels.' + pi)
            success = script.run('init',lock)
        if not success:
            print('prepipeline:docker-run failed:%s' % pi)
            break
    return success


def pos_init_prepipeline():
    for pi in prepipeline:
        model = models[pi]
        if not model.exist():
            print('posprocess_prepipeline:docker-img not exist: %s' % pi)
            continue
        if model.status():
            success = model.stop()
            print('posprocess_prepipeline:docker-img running -> stop: %s' % pi)
            continue
    return success


def do_job_parallel_gpu(videolist):
    lock = Lock()
    print('do_job_parallel_gpu:real_WORKER_NUM:%d' % real_WORKER_NUM)
    pool = ThreadPool(
        real_WORKER_NUM, initializer=pll_init, initargs=(lock, PLL, GPUS))
    results = pool.map(do_job_single, videolist)
    pool.close()
    pool.join()
    print('do_job_parallel_gpu:' + results)
    return results


def do_job_loop(videolist):
    results = []
    print('do_job_loop:' + results)
    for video in videolist:
        success = None
        try:
           success =  do_job_single(video)
           if not success:
                print('do_job_loop: fail on video %s' + video)
        except CalledProcessError as exception:
            print('do_job_loop: error on video %s' + video) 
        results.append(success)
    print('do_job_loop:' + results)
    return results


def do_job_single(video):
    ''' single job with gpu '''
    proclogger = ProcLogger(URL)
    global lock
    global GPUS
    for mid in pipeline:
        print('vid:%s, mid:%s, GPUS=%s' % (video, mid, GPUS))
        model = eval('config.dockermodels.' + mid)
        info = {
            'extra_info': pipename + '_' + timestamp,
            'module_name': mid,
            'status': 'start',
            'video_name': video + '.avi'
        }
        proclogger.post_progress_collection(info)
        success = model.run(video, lock)
        if not success:
            info['status'] = 'fail'
            proclogger.post_progress_collection(info)
            break
        else:
            info['status'] = 'succeed'
            proclogger.post_progress_collection(info)
    return success


def pll_init(l, pll, gpus):
    global lock, PLL, GPUS
    lock = l
    PLL = pll
    GPUS = gpus


def init_videos_from_lst(video_lst_file):
    videolist = []
    vlf = open(video_lst_file)
    for line in vlf.readlines():
        name, _ = os.path.splitext(line)
        videolist.append(name)
    vlf.close()
    return videolist


def testing(video_lst_file=None):
    print('Process:MAIN:PID:%d' % os.getpid())
    if not video_lst_file:
        videolist = [
            # CAM1:
            'MCTTR0101a.mov.deint',
            'MCTTR0201a.mov.deint',
            # CAM2:
            'MCTTR0101b.mov.deint',
            'MCTTR0101e.mov.deint',
            # CAM3:
            'MCTTR0203b.mov.deint',
            'MCTTR0203e.mov.deint',
            # CAM5:
            'MCTTR0205g.mov.deint',
            'MCTTR0205j.mov.deint'
        ]
    else:
        videolist = init_videos_from_lst(video_lst_file)
    # RUN    
    init_success = init_prepipeline(videolist)
    print('0.initialization:'+init_success)
    if init_success:
        # if too quick the pre-model will not be ready
        time.sleep(10)
        vid = videolist[0]
        print('1.test single video:%s'%vid)
        success = do_job_single(vid)
        print('1.result:'+success)
        print('2.test parallel computing on videos:%s'%videolist)
        result_list = do_job_parallel_gpu(videolist)
        print('2.result:' + result_list)
    pos_success = pos_init_prepipeline()
    print('3.postproces:'+pos_success)
    return (init_success and success and pos_success)


def main(video_lst_file):
    print('Process:MAIN:PID:%d' % os.getpid())
    videolist = init_videos_from_lst(video_lst_file)
    init_success = init_prepipeline(videolist)
    if init_success:
        time.sleep(10)
        if is_parallel
            result_list = do_job_parallel_gpu(videolist)
        else:
            result_list = do_job_loop(videolist)
        print(result_list)
        # success = do_job_single(videolist[0])
        # print(success)
    pos_success = pos_init_prepipeline()
    print(pos_success)
    return result_list
    
if __name__ == '__main__':
    testing()