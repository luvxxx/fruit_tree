from pyswagger import App, Security
from pyswagger.contrib.client.requests import Client
from pyswagger.utils import jp_compose

## Reading URL
from diva_parameters import URL
# URL = 'http://aladdin1.inf.cs.cmu.edu:83/api/swagger.json'

class ProcLogger():

  def __init__(self, url=URL):
    self.url = url
    self.logger = App.create(url)

  @property
  def url(self):
      return self.url

  @property
  def logger(self):
      return self.logger

  def update_logger(self,url):
      self.logger = App.create(url)   

  def post_progress_collection(self, info):
    '''
    Update status of (pipeline, vid, mid, status) to SQLDB
    Status: start(must be first inserted), fail, succeed
    example:
      curl -X POST \
      --header 'Content-Type: application/json' \
      --header 'Accept: application/json' \
      -d '{
        "extra_info": "string",
        "module_name": "string",
        "status": "start",
        "video_name": "string"
       }' 'http://aladdin1.inf.cs.cmu.edu:83/api/progresses/'
    '''
    # app = App.create(url)
    app = self.logger
    client = Client()
    op1 = app.op['post_progress_collection']
    req_resp = client.request(
        op1(
            payload=
            {
            "extra_info": info.get('extra_info'),
            "module_name": info.get('module_name'),
            "status": info.get('status'), # start, fail, succeed
            "video_name": info.get('video_name')
            }
        )
    )
    return req_resp.status == 201 # 500 if failed
   
  def get_progress_item(self, idx):
    '''
    curl -X GET --header 'Accept: application/json' 'http://aladdin1.inf.cs.cmu.edu:83/api/progresses/{id}'
    '''
    # app = App.create(url)
    app = self.logger
    client = Client()
    resp = client.request(app.op['get_progress_item'](id=idx))
    return resp


  def get_progress_collection(self):
    '''
    curl -X GET --header 'Accept: application/json' 'http://aladdin1.inf.cs.cmu.edu:83/api/progresses/'
    '''
    # app = App.create(url)
    app = self.logger
    client = Client()
    resp = client.request(app.op['get_progress_collection']())
    return resp


def main():
  ## testing init
  proclogger = ProcLogger(URL)
  print(URL)
  ## testing post_progress_collection
  info = {'extra_info': 'this is extra information',
          'module_name': 'module_name101',
          'status':'start',
          'video_name':'video101x'
          }
  success = proclogger.post_progress_collection(info)
  print(success)
  ## testing get_progress_item
  resp2 = proclogger.get_progress_item(2)
  res_dict = resp2.data
  print(res_dict)
  ## testing get_progress_collection
  resp3 = proclogger.get_progress_collection()
  res_list = resp3.data
  print(res_list)


if __name__ == '__main__':
    main()
