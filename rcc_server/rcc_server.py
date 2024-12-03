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
    
    def __init__(self,**kwargs) -> None:
        
        self.__receiver_url=f'http://{kwargs.get('url','')}:8991/sync_json'
        self.__get_url=''
        self.__success_event='te_ops_client_trigger_record'
        self.__debug_event='te_ops_client_debug_test'
        self.__debug_url=''
        self.__device_id='test_device'
        self.__appid=kwargs.get('appid', '')
        self.basic_info={              
            "#account_id": "wrp_sendtest",
            "#distinct_id": "wrp_sendtest",
            "#time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "#event_name": "te_ops_client_trigger_record",
            "#type": "track",
            "properties": {
                "#device_id": self.__device_id,
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

    @property
    def receiver_url(self) -> str:
        return self.__receiver_url

    @receiver_url.setter
    def receiver_url(self, url: str) -> None:
        self.__receiver_url = url

    @property
    def get_url(self) -> str:
        return self.__get_url

    @get_url.setter
    def get_url(self, url: str) -> None:
        self.__get_url = url

    @property
    def success_event(self) -> str:
        return self.__success_event

    @success_event.setter
    def success_event(self, event: str) -> None:
        self.__success_event = event

    @property
    def debug_event(self) -> str:
        return self.__debug_event

    @debug_event.setter
    def debug_event(self, event: str) -> None:
        self.__debug_event = event

    @property
    def debug_url(self) -> str:
        return self.__debug_url

    @debug_url.setter
    def debug_url(self, url: str) -> None:
        self.__debug_url = url

    @property
    def appid(self) -> str:
        return self.__appid

    @appid.setter
    def appid(self, appid: str) -> None:
        self.__appid = appid

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
            
    def send_request_with_response(self,url,data,appid,device_id):
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

            # 显示请求响应的总耗时
            
            #处理响应数据
            # print(response.text)
            # print(response.headers)
            # print(response.json())
            encoded_data = response.json()['data']
            decoded_data = base64.b64decode(encoded_data)
            decompressed_data = gzip.decompress(decoded_data)
            json_data = json.loads(decompressed_data)
            # print('返回的数据为',json_data)
            with open('output.txt', 'w') as f:
                print(json_data, file=f)

            print("Printed output saved to 'output.txt'.")
            print(f"请求响应总耗时: {total_time_ms} 毫秒")
            response_size = len(json.dumps(json_data))/1024/1024
            print(f"响应加密后大小为：{len(response.text)/1024/1024} mb")
            print(f"响应解密后大小为：{response_size:.2f} mb")
            # task_ids = []
            # td_strategy_info = json_data['config']['td_strategy_info']
            # for strategy_info in td_strategy_info:
            #     task_ids.append(strategy_info['taskId'])
            return json_data
            
        except requests.HTTPError as err:
            print(response.json())  
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
    def send_pull_success(self):
        
        
        url=self.__receiver_url
        
        basic_info=self.basic_info
        payload = {
            'data': basic_info,
            "appid": self.__appid
        }

        response = requests.request("POST", url, json=payload)

        print(response.text)
