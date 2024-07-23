# -*- coding: gbk -*-
import base64
import requests
import os
import json
import shutil
import time
import jsonlines
import re
from tqdm import tqdm
import sys
import subprocess  # ���� subprocess ģ��
import mimetypes  # ���� mimetypes ģ��

model_type = "claude-3-5-sonnet-20240620"
IMAGE_DIR = r"J:\�������ģ̬\claude-3.5-sonnet\chineseBQB"
PROCESSED_DIR = r"J:\�������ģ̬\claude-3.5-sonnet\processed_" + model_type
JSONL_FILE = "J:\�������ģ̬\claude-3.5-sonnet\image_descriptions_processed-" + model_type + ".jsonl"

prompt_template = "����һλ����ȵ�����ͼƬ����ߣ��ó��������������ͼƬ�����ܶ���ͼƬ�е�ϸ΢֮������ͼ�е������沿���顢������Ϣ��������¶�ͱ���Ԣ����г�ǿ���������������Ϣ��Ҫ��ϸ��Ϊ�˰�������õ����ͼ����Ϣ�����Ѿ���ͼ�������������ϢժҪ����������:{zhuti},����:{wenzi}���㷵�ص������б���������ṩ����������֣�����ɾ�����޸ġ������֪�����������ʹ�õ���������������Ĳ����������õĳ��������Խ�����Ϣ������������С�"

def image_to_base64(file_path):
    """
    image to base64
    """
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return encoded_string.decode("utf-8")
def extract_zhutiandwenzi(image_name):
    cleaned_name = re.sub(r"\d{5}", "", image_name)
    cleaned_name = os.path.splitext(cleaned_name)[0]
    zhutiandwenzi = cleaned_name.strip().strip(".")
    return zhutiandwenzi
def split_zhutiandwenzi(zhutiandwenzi):
    parts = zhutiandwenzi.split("-", 1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    else:
        return "", ""
def process_images(image_paths):

    for i, image_path in enumerate(tqdm(image_paths, desc="Processing Images", unit="image")):

        filename = os.path.basename(image_path)
        zhutiandwenzi = extract_zhutiandwenzi(filename)
        zhuti, wenzi = split_zhutiandwenzi(zhutiandwenzi)
        prompt_ch_2 = prompt_template.format(zhuti=zhuti, wenzi=wenzi)

        media_type = mimetypes.guess_type(image_path)[0]

        content_list = [
            {
                "type": "text",
                "text": prompt_ch_2
            },
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": image_to_base64(image_path),
                }
            }
        ]

        url = "https://XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/v1/messages"
        body = {
            "model": model_type,
            "max_tokens": 4096,
            "messages": [
                {
                    "role": "user",
                    "content": content_list
                }
            ],
            "stream": False
        }

        try:
            response = requests.post(url, headers={
                'x-api-key': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json'
            }, json=body, timeout=60)
            response.raise_for_status()
            response_json = response.json()
            print("response_json:", response_json)
            content = response_json['content'][0]['text']

            result = {
                "picName": filename,
                "description": content
            }
            shutil.move(image_path, os.path.join(PROCESSED_DIR, filename))
            os.utime(os.path.join(PROCESSED_DIR, filename), (time.time(), time.time()))
            with jsonlines.open(JSONL_FILE, mode='a') as writer:
                writer.write(result)

        except requests.exceptions.RequestException as e:
            print(f"�������: {e}")
        except (json.JSONDecodeError, KeyError) as e:
            print(f"������Ӧ����: {e}")
        finally:
            time.sleep(2)

if __name__ == '__main__':
    image_paths = [os.path.join(IMAGE_DIR, f) for f in os.listdir(IMAGE_DIR) if
                   os.path.isfile(os.path.join(IMAGE_DIR, f))]
    process_images(image_paths)
