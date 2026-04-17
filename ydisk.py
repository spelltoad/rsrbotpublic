import os
import requests
import yadisk
from collections import defaultdict

from regions_codes import REGION_CODES

YADISK_HEADERS = {
    'Authorization': '***'
}


ya = yadisk.YaDisk(token="***")
chat_messages = defaultdict(list)

cwd = os.getcwd() + "/data"

async def write_to_log(log_message, server_log_path="/Маршруты по регионам/log.txt", local_path="log.txt"):
    try:
        ya.download(server_log_path, local_path)
        with open(local_path, 'a') as log_file:
            log_file.write(log_message + '\n')
        ya.remove(server_log_path)
        ya.upload(local_path, server_log_path)
        print("Log written")
    except Exception as e:
        print(f"An error occurred: {e}")

async def save_file(File, path):
    response = requests.get(File.file_path)

    # Проверяем, успешно ли выполнен запрос
    if response.status_code == 200:
        # Открываем файл в бинарном режиме и записываем данные
        with open(path, 'wb') as file:
            file.write(response.content)
        print("File successfully downloaded")
    else:
        print("An error when downloading a file:", response.status_code)

async def find_or_create_folder(base_path, name_of_region):
     parts = name_of_region.split()
     
     for i in range(1, len(parts) + 1):
         folder_name = " ".join(parts[:i])
         folder_path = ('/Маршруты по регионам' + base_path + '/' + folder_name)
         if ya.exists(folder_path):
             return folder_name + '/' +  " ".join(parts[i:])
 
     full_folder_path = os.path.join(cwd + base_path, name_of_region)
     os.makedirs(full_folder_path, exist_ok=True)
     return name_of_region + '/'

async def save_photos(photos, number_of_region, name_of_region, message_date):
    date_folder = message_date.strftime("%Y-%m-%d")
    date_file = message_date.strftime("%H%M%S")
    date = message_date.strftime("%Y-%m-%d %H:%M:%S")
    
    base_path = f'/{REGION_CODES[number_of_region]}'
    region_folder = await find_or_create_folder(base_path, name_of_region)
    full_path = base_path + '/' + region_folder + date_folder
    os.makedirs(cwd + full_path, exist_ok=True)

    for i, photo in enumerate(photos):
        file_path = full_path + '/' + f'{date_file}_{i}.jpg'
        
        file = await photo.get_file()
        await save_file(file, cwd + file_path)
        print(f"Uploading: /Маршруты по регионам{file_path}")
       
        print(f"Making dirs: /Маршруты по регионам{full_path}")
        try:
            ya.makedirs('/Маршруты по регионам' + full_path)
            await write_to_log(f'{date}\tNew folder:/Маршруты по регионам{file_path}')
        except (yadisk.exceptions.PathExistsError, yadisk.exceptions.PathNotFoundError):
            pass
        try:
            ya.upload(cwd + file_path, '/Маршруты по регионам' + file_path)
            print('Uploaded photo: ' + '/Маршруты по регионам' + file_path)
            await write_to_log(f'{date}\tNew photo: /Маршруты по регионам{file_path}')
        except yadisk.exceptions.PathExistsError:
            pass

        print(f'Saved photo: {file_path}')
