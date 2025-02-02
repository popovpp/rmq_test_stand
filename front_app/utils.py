import csv
import aiohttp
import asyncio
import os
import socket
from typing import List, Optional
from pydantic import BaseModel


class TestParams(BaseModel):
    test_name: str
    mode: str
    cmd_list: Optional[List[str]] = None


async def get_test_list_from_file(filename: str) -> List[dict]:
    tests_list = []
    with open(filename, encoding='utf-8') as r_file:
        # Создаем объект reader, указываем символ-разделитель ","
        file_reader = csv.reader(r_file, delimiter=",")
        # Счетчик для подсчета количества строк и вывода заголовков столбцов
        count = 0
        # Считывание данных из CSV файла
        for row in file_reader:
            test_obj = TestParams(
                test_name=row[0].strip(),
                mode=row[1].strip(),
                cmd_list=[]
            )
            for i in range(2, len(row)):
                test_obj.cmd_list.append(row[i].strip())
            tests_list.append(test_obj.__dict__)
            count += 1
        print(f'Всего в файле {count} строк.')
    return tests_list


def get_local_ip():
    """Получение локального ip адреса хоста"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 1))
        local_ip = s.getsockname()[0]
        return local_ip
    except Exception as error:
        print(error)
        return '0.0.0.0'


async def post_request(url, json_data=None, params=None):
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "accept": "application/json",
                "Content-Type": "application/json"
            }
            async with session.post(
                url,
                json=json_data,
                headers=headers,
                params=params
            ) as resp:
                print(resp.status)
                print(await resp.text())
        return resp.status, await resp.text()
    except Exception as error:
        print(error)
        return None


async def waiting_for_file(file_name):

    while not os.path.exists(file_name):
        await asyncio.sleep(1)


def delete_result_file(filename):
    if os.path.exists(filename):
        os.remove(filename)
