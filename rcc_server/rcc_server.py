import base64
import binascii
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime
import gzip
import hashlib
import json
import time
import requests

class RccServer:
    
    def __str__(self):
        return f"RccServer(appid={self._appid}, device_id={self._device_id}, url={self._receiver_url})"
    
    def __init__(self,**kwargs) -> None:
        """RccServer类用于与ThinkingData远程配置中心交互
        
        属性:
            url (str): 服务器ip地址
            device_id (str): 设备ID,默认为'test_device'
            appid (str): 应用ID
        """
        self._appid=kwargs.get('appid', '')
        self._device_id=kwargs.get('device_id', 'test_device')
        self._receiver_url=f"http://{kwargs.get('url','')}:8991/sync_json"
        self._get_url=f"http://{kwargs.get('url','')}:8991/v1/remote-config/get"
        self._success_event='te_ops_client_trigger_record'
        self._debug_event='te_ops_client_debug_test'
        self._data_debug_url=f"http://{kwargs.get('url','')}:8991/data_debug?appid={self._appid}&source=client&dryRun=0&deviceId={self._device_id}"
        self._debug_url=f"http://{kwargs.get('url','')}:8991/v1/remote-config/debug"
        self.basic_info={              
            "#account_id": "wrp_sendtest",
            "#distinct_id": "wrp_sendtest",
            "#time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "#event_name": "te_ops_client_trigger_record",
            "#type": "track",
            "properties": {
                "#device_id": self._device_id,
                "#lib": "Cpp",
                "#lib_version": "1.3.6-beta.1",
                "#os": "Windows",
                "#ops_task_id": "11850",
                "#ops_push_status": 6,
                "#ops_exp_group_id": "2611",
                "#ops_push_id": "0caee832-6200-4fd4-b9e8-914db21fd9b1",
                "#zone_offset": 8,
                "#ops_trigger_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "#ops_actual_push_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        self._rcc_request_params = {
            "appId": self._appid,
            # "last_fetch_time": "1733108400000",
            # "local_user_id": 1086335071327105026,
            "template_code": f"td_config_center_{self._appid}",
            # "template_code": "td_strategy",
            "request_params": {
                "#account_id": 'dcf51fcb-60db-4d60-8f3a-d89ce3e1411',
                "#os": "iOS",
                "#device_id": self._device_id,
                # "#client_user_id": "96310A8C-5294-4F51-90CD-F26A019DBD86",
                "#os_version": "17.4",
                "#system_language": "zh",
                "#app_version": "1.0",
                "#bundle_id": "cn.thinkingdata.ios.sdk",
                "#distinct_id": "AB2A9348-D76F-46D4-8F19-20230D79CFEA",
                "#simulator": False,
                "#zone_offset": 8,
                "#manufacturer": "Apple",
                "#device_type": "iPhone",
                "#device_model": "arm64",
                "#network_type": "WIFI",
                "#install_time": "2024-05-26 01:07:22.264"
            }
        }

    @property
    def receiver_url(self) -> str:
        return self._receiver_url

    @receiver_url.setter
    def receiver_url(self, url: str) -> None:
        self._receiver_url = url

    @property
    def get_url(self) -> str:
        return self._get_url

    @get_url.setter
    def get_url(self, url: str) -> None:
        self._get_url = url

    @property
    def success_event(self) -> str:
        return self._success_event

    @success_event.setter
    def success_event(self, event: str) -> None:
        self._success_event = event

    @property
    def debug_event(self) -> str:
        return self._debug_event

    @debug_event.setter
    def debug_event(self, event: str) -> None:
        self._debug_event = event

    @property
    def debug_url(self) -> str:
        return self._debug_url

    @debug_url.setter
    def debug_url(self, url: str) -> None:
        self._debug_url = url

    @property
    def appid(self) -> str:
        return self._appid

    @appid.setter
    def appid(self, appid: str) -> None:
        self._appid = appid

    @property
    def rcc_request_params(self):
        return self._rcc_request_params

    @rcc_request_params.setter
    def rcc_request_params(self, params):
        self._rcc_request_params = params

    def encode_sign_headers(self,data,appid,device_id):
        
        data=json.dumps(data)
        content_length=len(data.encode('utf-8'))
        # 获取当前时间的毫秒级时间戳 
        #milliseconds = int(time.time() * 1000)
        milliseconds = 1716809774315

        pre_data=str(milliseconds)+data+'thinkingdata-remote-config'

        # 创建SHA256对象
        sha256 = hashlib.sha256()

        # 更新SHA256对象的数据
        sha256.update(pre_data.encode())

        # 计算SHA256哈希值
        hashed_data = sha256.hexdigest()

        # # 将十六进制字符串转换为二进制数据
        binary_data = binascii.unhexlify(hashed_data)

        # # 对二进制数据进行 BASE64 编码
        base64_data = base64.b64encode(binary_data).decode()

        headers={
            'device_id': device_id,
            'appid': appid,
            'sign':f'{base64_data}',
            'timestamp': f'{milliseconds}',
            'Content-Length': f'{content_length}',
            # "Host": "10.206.32.97:8991"
        }
        return headers
    
    def send_request(self,url,data,appid,device_id):
        # 生成长度为10的随机字符串
        # i+=1
        # print(f'这是第{i}次')
        headers=self.encode_sign_headers(data,appid,device_id)
        data=json.dumps(data)
        try:
            response = requests.post(url, data=data,headers=headers)
            response.raise_for_status()  # 检查是否有错误发生
            
            #处理响应数据
            print(response.text)
            print(response.headers)
            encoded_data = response.json()['data']
            decoded_data = base64.b64decode(encoded_data)
            decompressed_data = gzip.decompress(decoded_data)
            json_data = json.loads(decompressed_data)
            print('返回的数据为：',json_data)
            task_ids = []
            td_strategy_info = json_data['config']['td_strategy_info']
            for strategy_info in td_strategy_info:
                task_ids.append(strategy_info['taskId'])
            return task_ids
            
        except requests.HTTPError as err:
            print(f'HTTP error occurred: {err}')

        except requests.exceptions.RequestException as err:
            print(f'Request exception occurred: {err}')
            
    def rcc_request(self,url,data,appid,device_id):
         # 生成长度为10的随机字符串
        # i+=1
        # print(f'这是第{i}次')
        headers=self.encode_sign_headers(data,appid,device_id)
        data=json.dumps(data)
        try:
            print("请求头：",headers)
            print("请求体：",data)
            # 发送请求前记录开始时间
            start_time = time.time()

            response = requests.post(url, data=data,headers=headers)
            # 计算请求响应的总耗时
            end_time = time.time()
            response.raise_for_status()  # 检查是否有错误发生
            
            total_time = end_time - start_time 
            total_time_ms=total_time*1000

            encoded_data = response.json()['data']
            decoded_data = base64.b64decode(encoded_data)
            decompressed_data = gzip.decompress(decoded_data)
            json_data = json.loads(decompressed_data)
            
            print(f"请求响应总耗时: {total_time_ms} 毫秒")
            response_size = len(json.dumps(json_data))/1024/1024
            print(f"响应加密后大小为：{len(response.text)/1024/1024} mb")
            print(f"响应解密后大小为：{response_size:.2f} mb")
            
            return json_data
            
        except requests.HTTPError as err:
            print(response.text)  
            print(f'HTTP error occurred: {err}')

        except requests.exceptions.RequestException as err:
            print(response.json())  
            print(f'Request exception occurred: {err}')     
            
        except Exception:
            print(response.json())      
        
    def run_test_concurrently(self,num_requests,data,appid,device_id):
        with ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [executor.submit(self.send_request(data,appid,device_id)) for _ in range(num_requests)]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f'Exception occurred: {e}')
                    
    @staticmethod
    def process_result(result):
        result_obj = json.loads(result)
        strategy_id=result_obj.pop('#strategy_id', None)
        result_obj.get('#ops_receipt_properties', {}).pop('ops_request_id', None)
        result_obj.get('#ops_receipt_properties', {}).pop('ops_strategy_id', None)
        # print(f'剔除后的json{json.dumps(result_obj)}')
        result = json.dumps(result_obj, ensure_ascii=False)
        return hashlib.md5(result.encode()).hexdigest(),strategy_id  
    
    
    