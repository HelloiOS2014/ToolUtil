# -*- coding:UTF-8 -*-
# file   : AudioUtil.py
# time   : 2023/11/29 
# author : panghu
# Desc   :
import json
import os
import shutil
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.asr.v20190614 import asr_client, models
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import time

secret_id = "AKIDoVyDDzax72i9KH3f4HG0Vmob9RTFl11l"
secret_key = "ay70d07yaw0pQr2ygDWcR1MSJvKVR9cr"
cos_region = 'ap-guangzhou'
cos_bucket = "panghu-audio-1256735925"

cos_config = CosConfig(Region=cos_region, SecretId=secret_id, SecretKey=secret_key)
cos_client = CosS3Client(cos_config)


def start_task(endpoint, params, create_req, create_resp):
    try:
        cred = credential.Credential(secret_id, secret_key)
        http_profile = HttpProfile()
        http_profile.endpoint = endpoint
        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile
        client = asr_client.AsrClient(cred, "", client_profile)
        req = create_req()
        req.from_json_string(json.dumps(params))
        resp = create_resp(client, req)
        return json.loads(resp.to_json_string())
    except TencentCloudSDKException as err:
        print(err)
        return None
    except:
        return None


def identify_audio(url):
    result = start_task(
        endpoint="asr.tencentcloudapi.com",
        params={
            "EngineModelType": "16k_zh",
            "ChannelNum": 1,
            "ResTextFormat": 2,
            "SourceType": 0,
            "Url": url
        },
        create_req=lambda: models.CreateRecTaskRequest(),
        create_resp=lambda client, req: client.CreateRecTask(req)
    )

    if result is not None:
        return result["Data"]["TaskId"]
    else:
        return None


def get_identify_result(task_id):
    result = start_task(
        endpoint="asr.tencentcloudapi.com",
        params={"TaskId": task_id},
        create_req=lambda: models.DescribeTaskStatusRequest(),
        create_resp=lambda client, req: client.DescribeTaskStatus(req)
    )

    if result is None:
        return False, "发起查询结果失败"
    result_data = result.get("Data")
    if result_data is None:
        return False, "获取解析结果失败"

    status_str = result_data.get("StatusStr")
    if status_str == "failed":
        return False, result_data.get("ErrorMsg")

    if status_str != "success":
        time.sleep(1)
        return get_identify_result(task_id)

    detail_list = result_data.get("ResultDetail")
    if detail_list is None or (not isinstance(detail_list, list)):
        return False, "获取不到解析结果"

    if len(detail_list) <= 0:
        return False, "解析结构有问题"

    detail_data = detail_list[0]

    return True, detail_data.get("FinalSentence")


def upload_file(fold_path, output_path, finish_path):
    for file in os.listdir(fold_path):
        if file == ".DS_Store":
            continue
        file_path = os.path.join(fold_path, file)
        timestamp = int(time.time())
        file_key = f"{timestamp}-{file}"
        print(f"开始上传{file}")
        try:
            upload_response = cos_client.upload_file(
                Bucket=cos_bucket,
                Key=file_key,
                LocalFilePath=file_path,
                EnableMD5=False,
                progress_callback=lambda consumed_bytes, total_bytes: print(
                    "上传({}):{}%".format(file, int(100 * (float(consumed_bytes) / float(total_bytes)))))
            )
            print(f"完成上传:{file}")
            file_url = cos_client.get_object_url(Bucket=cos_bucket, Key=file_key)
            print(f"文件 URL：{file_url}")
            print("等待解析结果返回中...")
            dst_path = os.path.join(finish_path, file)
            shutil.move(file_path, dst_path)

            task_id = identify_audio(url=file_url)
            if task_id is None:
                print(f"{file}解析失败")
                continue
            task_status, task_result = get_identify_result(task_id)
            if task_status is True and isinstance(task_result, str):
                output_file = f"{output_path}/{'.'.join(file.split('.')[:-1])}.txt"
                print(f"解析成功:已经写入文件:{output_file}")
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(task_result)
            else:
                print(f"解析失败：{task_result}")
        except:
            print(f"{file}上传失败")
