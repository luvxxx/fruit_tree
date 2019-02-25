import sys
import os
import time
sys.path.insert(0, '../..')
from diva_parameters import conf_dirs


def run(video,lock):
    '''
        1. SET model, using the key provide in config.yaml -> pipeline
        2. SET directory, see config.yaml -> directory
        3. CONFIGURE parameters:
            {parameters,sub_parameters,nvidia_parameters}
        4. RUN
    '''

    # 1. SET dockermodel name, must be consistent with the name in config.yaml -> pipeline
    model_name = 'some_docker_name'

    # 2. SET directory information, must be consistent with the directories in config.yaml -> directory
    PREPROCESS_DIR = conf_dirs.get('PREPROCESS_DIR')
    PERSON_DETECT_DIR = conf_dirs.get('PERSON_DETECT_DIR')
    DATA_DIR = conf_dirs.get('DATA_DIR')

    # Create output dir [You may not need this code]
    output_dir = os.sep.join([DATA_DIR, model_name, video])
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create video list [You may not need this code]
    with open(os.sep.join([DATA_DIR, str(video) + '.lst']), 'w') as e:
        e.write(str(video) + '.avi')
    e.close()


    # 3. CONFIGURE parameters. 
    # NOTICE1: It will overwrite parameters in {dockermodel}.yaml
    # NOTICE2: parameters must be in type of dictionary. E.g. :
    # NV_PARAMETER = {'NV_GPU': "'%s'" % str(gid)}
    # PARAMETER = {'-p','8000:8000'} 
    # SUB_PARAMETER = {
    #         '--input_dir': os.sep.join([PREPROCESS_DIR, video, 'frame_25']),
    #         '--input_lst': os.sep.join([PREPROCESS_DIR, video, 'frame_25.lst']),
    #         '--out_dir': os.sep.join([PERSON_DETECT_DIR, video])
    # }

    parameters = {
        parameters:None,
        nvidia_parameters:None,
        sub_parameters : None
    }

    # 4. RUN
    success = dummy_run(video,model_name,lock,parameters)
    return success

def testing():
    from multiprocessing import Pool, Lock
    lock = Lock()
    video = 'MCTTR0101a.mov.deint'
    success = run(video, lock)


if __name__ == '__main__':
    testing()
