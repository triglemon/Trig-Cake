""""Json method wrapper module"""
import json
import aiofiles


async def async_load(file_name):
    """Loading json data"""
    async with aiofiles.open(f'json/{file_name}.json') as file_content:
        file_string = await file_content.read()
        return json.loads(file_string)


async def delete_dump(data, key, file_name):
    del data[key]
    async with aiofiles.open(f'json/{file_name}.json', 'w') as out_file:
        await out_file.write(json.dumps(data))


async def new_value_dump(data, key, value, file_name):
    """Assigning new value to json key and dumping to file"""
    data[key] = value
    async with aiofiles.open(f'json/{file_name}.json', 'w') as out_file:
        await out_file.write(json.dumps(data))


async def remove_dump(data, key, value, file_name):
    data[key].remove(value)
    if not data[key]:
        del data[key]
        return True
    async with aiofiles.open(f'json/{file_name}.json', 'w') as out_file:
        await out_file.write(json.dumps(data))


async def append_value_dump(data, key, value, file_name):
    """Appending entry to json list and dumping to file"""
    data[key].append(value)
    async with aiofiles.open(f'json/{file_name}.json', 'w') as out_file:
        await out_file.write(json.dumps(data))
