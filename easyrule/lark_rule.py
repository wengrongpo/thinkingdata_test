import json

import lark_oapi as lark
from lark_oapi.api.bitable.v1 import *


# SDK 使用说明: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/preparations-before-development
# 以下示例代码是根据 API 调试台参数自动生成，如果存在代码问题，请在 API 调试台填上相关必要参数后再使用
def main():
    # 创建client
    # 使用 user_access_token 需开启 token 配置, 并在 request_option 中配置 token
    client = lark.Client.builder() \
        .enable_set_token(True) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    # 构造请求对象
    request: SearchAppTableRecordRequest = SearchAppTableRecordRequest.builder() \
        .app_token("C2LFb1mbXaOyvhsopbecFtOunNc") \
        .table_id("tblsAb7kyT7Hqffw") \
        .request_body(SearchAppTableRecordRequestBody.builder()
            .view_id("vew8EMZLNX") 
            .field_names(["包含关键字", "告警来源组件","处理操作","时间间隔（min）","出现次数"])
            .build()) \
        .build()

    # 发起请求
    option = lark.RequestOption.builder().user_access_token("u-feOza6kcVcNWeZIwhRqglNlg6Szw54nbjgG001e00Azb").build()
    response: SearchAppTableRecordResponse = client.bitable.v1.app_table_record.search(request, option)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.bitable.v1.app_table_record.search failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
        return

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
    main()