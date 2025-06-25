import hashlib
import json

import requests
from rcc_server.rcc_server import RccServer

class Strategy(RccServer):

    def __init__(self, **kwargs) -> None:
        super().__init__( **kwargs)
    
    @staticmethod
    def process_response(response, configId, templateCode, strategyId):
        
        try:
            customParams = response['config'][configId]['#custom_params']
            datas = response['config'][configId][templateCode]
            result = json.dumps(next(filter(lambda data: data['#strategy_id'] == strategyId, datas)), ensure_ascii=False)
        except:
            print(f'策略{strategyId}可能已下线,{json.dumps(response,ensure_ascii=False)}')
            return False
        print(f"策略{strategyId}结果为：", result)
        print(f"自定义参数的结果为：", customParams)
        result_md5 = RccServer.process_result(result)
        print(f'策略内容的md5为:{result_md5}')  
        return True
    
    @staticmethod
    def process_result(result):
        result_obj = json.loads(result)
        strategy_id=result_obj.pop('#strategy_id', None)
        result = json.dumps(result_obj, ensure_ascii=False)
        return hashlib.md5(result.encode()).hexdigest(),strategy_id  
    
    @staticmethod 
    def debug_process_response(response, configId, templateCode):
        try:
            strateg_id=response['config'][configId][templateCode][0]['#strategy_id']       
            print(response['config'][configId])
            print(f'策略{strateg_id}正在测试上线')
            return strateg_id
        except KeyError:
            try:
                strategy_and_status=response['config']['#strategy_status_map'][configId][templateCode]
                for key,value in strategy_and_status.items():
                    if value=='suspend':
                        print(f'策略{key}正在测试暂停')
                    elif value=='online':
                        print(f'策略{key}正在测试上线，环境条件错误')
                    elif value=='offline':    
                        print(f'策略{key}正在测试下线')
            except KeyError:
                print('未进行发送测试或configId、templateCode有误')      
                return 0 
            
    @staticmethod
    def validate_strategy_list(datas, content_md5):
        strategy_set=set()
        for i in range(0, 5):
            strategy_list = datas[f'performance_template_{i}'] if i > 0 else datas['performance_template']
            md5_content = content_md5[f'performance_template_{i}'] if i > 0 else content_md5['performance_template']
            for data in strategy_list:
                strategy_md5,strategy_id=RccServer.process_result(json.dumps(data))
                assert strategy_md5 == md5_content, f"策略列表中的数据与预期 MD5 不匹配"
                print(f'策略{strategy_id}拉取正确')
                strategy_set.add(strategy_id)
        assert len(strategy_set)==200,f'策略数量不正确,数量为{len(strategy_set)}'
        print(f'策略数量正确')
        
    def getConfig(self, **kwargs):
        
        response=self.rcc_request(self._get_url,self._rcc_request_params,appid=self._appid,device_id=self._device_id)
        configId=kwargs.get('configId','')
        strategyId=kwargs.get('strategyId','')
        templateCode=kwargs.get('templateCode','')
        # 调用新封装的函数
        flag=Strategy.process_response(response,configId,templateCode, strategyId)
        
        if kwargs.get('is_validate','')==True:
            config_datas=response['config'][configId]
            Strategy.validate_strategy_list(config_datas, kwargs.get('content_md5',''))
        
        strategyStatus=response['config']['#strategy_status_map']
        
        if kwargs.get('check_status','')==True:
            try:
                strategyStatus=response['config']['#strategy_status_map'][configId][templateCode][strategyId]
            except:
                if flag:print(f"策略{strategyId}的状态为：Online")
                return
        
        print(f"策略{strategyId}的状态为：",json.dumps(strategyStatus,ensure_ascii=False))
    
    def debugConfig(self, **kwargs):
        
        response=self.rcc_request(self._debug_url,self._rcc_request_params,appid=self._appid,device_id=self._device_id)
        configId=kwargs.get('configId','')
        templateCode=kwargs.get('templateCode','')
        
        taskId=Strategy.debug_process_response(response,configId,templateCode)
        
        if taskId==0 :
            return
        print("拉取到的任务ID:",taskId) 

        self.basic_info.update({"properties": {
            "#device_id": self._device_id,
            "#lib": "Cpp",
            "#lib_version": "1.3.6-beta.1",
            "#os": "Windows",
            "#rcc_pull_result": {
                "business_type": "2",
                "is_pull_success": True,
                # "pull_fail_code": -6,
                "ops_config_content":response['config']
            },
        },"#event_name": self._debug_event})
        
        
        if kwargs.get('show_error')==True and kwargs.get('error_reason')!=None :self.basic_info['properties']['#rcc_pull_result']['pull_fail_code']=kwargs.get('error_reason')
        
        payload = {
            'data': f'{json.dumps(self.basic_info)}'
        }
    
        response = requests.request("POST", self._data_debug_url, data=payload)

        print(response.text) 