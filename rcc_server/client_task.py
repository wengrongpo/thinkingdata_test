import json

import requests
from rcc_server.rcc_server import RccServer

class ClientTask(RccServer):

    @staticmethod
    def process_response(response):
        
        pass
    
    def getConfig(self, **kwargs):
        
        request_params=self._rcc_request_params.copy()
        request_params['template_code']='td_strategy'
        if kwargs.get('debug')==True:
            response=self.rcc_request(self._debug_url,request_params,appid=self._appid,device_id=self._device_id)
        else:    
            response=self.rcc_request(self._get_url, request_params, appid=self._appid, device_id=self._device_id)
        
        return response
        
    
    def debugConfig(self, **kwargs):
        response=self.getConfig(debug=True)
        task_ids = [info['taskId'] for info in response['config']['td_strategy_info']]
        print(f'拉取到的任务ID：{task_ids}')
        
        self.basic_info.update({"properties": {
            "#device_id": self._device_id,
            "#lib": "Cpp",
            "#lib_version": "1.3.6-beta.1",
            "#os": "Windows",
            "#rcc_pull_result": {
                "business_type": "1",
                "is_pull_success": True,
                # "pull_fail_code": -6,
                "ops_task_id_list": task_ids,
            },
        },"#event_name": self._debug_event})
        
        payload = {
            'data': f'{json.dumps(self.basic_info)}'
        }

        response = requests.request("POST", self._data_debug_url,  data=payload)

        print(response.text)
        
        
    
    def send_pull_success(self,taskId):
        
        url=self._receiver_url
        basic_info=self.basic_info
        
        basic_info['properties']['#ops_task_id']=taskId
        payload = {
            'data': basic_info,
            "appid": self._appid
        }

        response = requests.request("POST", url, json=payload)

        print(response.text)   