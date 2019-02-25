import sys
import os
sys.path.insert(0, '../..')
import parameters
from parameters import models, conf_log, conf_dirs, TEST, timestamp
import multiprocessing
import parallel

def dummy_run(video,model_name,lock,PARA):
    '''
        1. GET model, using the key provided in config.yaml -> pipeline
        2. DEFINE directory, see config.yaml -> directory
        3. NEW video list with only one {video}
           (we keep the function of docker which can deal with multiple videos)
        4. INIT logger
        5. UPDATE parameters
        6. RUN
    '''

    model = models.get(model_name)

    DATA_DIR = conf_dirs.get('DATA_DIR')
    # parameters.create_vid_dir(DATA_DIR, model_name, video)
    # parameters.create_vid_lst(DATA_DIR, video)
    output_module_dir = os.sep.join([DATA_DIR, model_name])
    parameters.checkdir(output_module_dir , 'output_module_dir', 0)

    if not lock:
        lock.acquire()
    logger = parameters.creat_logger(video, model_name, conf_log)

    ## UPDATE parameters
    if PARA.get('parameters'):
        para = PARA.get('parameters')
        print('update parameters:%s' % para)
        model.update_parameters(para)
        del para

    if PARA.get('sub_parameters'):
        para = PARA.get('sub_parameters')
        print('update sub_parameters:%s' % para)
        model._parameters(para)

    if model.type == 'nvidia_docker':
        if not PARA.get('nvidia_parameters'):
            print('update nvidia_parameters:%s' % PARA.get('nvidia_parameters'))
            # GPU: lock a gpu if there is an available one
            gid = parallel.pll_get_gid_simple(logger)
            NV_PARAMETER = {'NV_GPU': "'%s'" % str(gid)}
            print('gid_%d'%int(gid))
        else:
            NV_PARAMETER = PARA.get('nvidia_parameters')
        model.update_nvidia_parameters(NV_PARAMETER)

    model.rename(video.split('.')[0] + model_name + '_' + timestamp)
    logger.logger.warn('model_%s:%s' % (model_name, model.name))
    print('model.para:%s'%model.cmd)

    if not lock:
        lock.release()

    if  TEST:
        success = model.test(logger)
    else:
        success = model.run(logger)
    # GPU: unlock a gpu
    if model.type == 'nvidia_docker' and success:
        parallel.pll_unlock(gid, logger, lock)
    return success


def main():
    import os
    from parameters import conf_dirs
    from multiprocessing import Pool, Lock
    # An example:
    video = 'MCTTR0101a.mov.deint'
    PREPROCESS_DIR = conf_dirs.get('PREPROCESS_DIR')
    PERSON_DETECT_DIR = conf_dirs.get('PERSON_DETECT_DIR')
    PARA = {
        'parameters':None,
        'nvidia_parameters':None,
        'sub_parameters' : {
        '--img_dir': os.sep.join([PREPROCESS_DIR, video, 'frame_25']),
        '--img_lst_file': os.sep.join([PREPROCESS_DIR, video, 'frame_25.lst']),
        '--out_dir': os.sep.join([PERSON_DETECT_DIR, video])
        }
    }
    model_name = 'persondetect'
    lock = Lock()
    video = 'MCTTR0101a.mov.deint'
    success = dummy_run(video,model_name,lock,PARA)
    print success

if __name__ == '__main__':
    main()