from multiprocessing import Pool, cpu_count, Lock, current_process
from multiprocessing.dummy import Pool as ThreadPool
from parameters import GPUS, PLL
import time


def pll_get_gid_simple(guavalogger):
    '''
    Get avaliable gpu_id and change its state in {GPUs} to True as locked
    '''
    logger = guavalogger.logger
    logger.info('pll_get_gid_simple:GPUS:%s' % GPUS)
    gid = -1
    start_time = time.time()
    while True:
        logger.info('check:%s' % GPUS)
        for gidi, locki in GPUS.items():
            if not locki:
                gid = gidi
                pll_lock(gid, guavalogger)
                break
        end_time = time.time()
        if gid >= 0:
            logger.info('get_id:%d get!' % int(gid))
            break
        elif (end_time - start_time > PLL.get('timeout')):
            logger.warn('get_id:%d timeout!' % int(gid))
            break
        else:
            logger.warn('get_id: Continue')
            time.sleep(int(PLL.get('timewait')))
    if gid == -1:
        gid = 0
        logger.warn('cannot get available gid, use gid=0')
    # print('pll_get_gid_simple: GPUS=%s'%(GPUS))
    return gid


def pll_init(l, pll, gpus):
    global lock, PLL, GPUS
    lock = l
    PLL = pll
    GPUS = gpus


def pll_lock(gpu_id, guavalogger):
    logger = guavalogger.logger
    # global GPUS
    gpu_id = str(gpu_id)
    # lock.acquire()
    if not GPUS.get(int(gpu_id)):
        logger.warn('id:%d, unlock->lock' % int(gpu_id))
        GPUS[int(gpu_id)] = True
        print('pll_lock: gpu_id %s,GPUS=%s'%(gpu_id,GPUS))
    # lock.release()


def pll_unlock(gpu_id, guavalogger,lock):
    # global lock
    logger = guavalogger.logger
    # global GPUS
    lock.acquire()
    if GPUS.get(int(gpu_id)):
        logger.warn('id:%d, lock->unlock' % int(gpu_id))
        GPUS[int(gpu_id)] = False
        print('pll_unlock: gpu_id %s,GPUS=%s'%(gpu_id,GPUS))
    lock.release()