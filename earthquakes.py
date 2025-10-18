# The Python standard library includes some functionality for communicating
# over the Internet.
# However, we will use a more powerful and simpler library called requests.
# This is external library that you may need to install first.
import requests
import json


def get_data():
    # With requests, we can ask the web service for the data.
    # Can you understand the parameters we are passing here?
    response = requests.get(
        "http://earthquake.usgs.gov/fdsnws/event/1/query.geojson",
        params={
            'starttime': "2000-01-01",
            "maxlatitude": "58.723",
            "minlatitude": "50.008",
            "maxlongitude": "1.67",
            "minlongitude": "-9.756",
            "minmagnitude": "1",
            "endtime": "2018-10-11",
            "orderby": "time-asc"}
    )

    # 检查请求是否成功,检查 HTTP 请求状态码，如果不是 200，则抛出异常。
    response.raise_for_status()
    # The response we get back is an object with several fields.
    # The actual contents we care about are in its text field:
    text = response.text
    # To understand the structure of this text, you may want to save it
    # to a file and open it in VS Code or a browser.
    # See the README file for more information.
    ...

    # We need to interpret the text to get values that we can work with.
    # What format is the text in? How can we load the values?
    # 文本格式是 JSON。我们使用 json.loads() 将 JSON 字符串
    # 转换为 Python 字典对象，这是我们能够操作的数据结构。
    data = json.loads(text)
    return data

def count_earthquakes(data):
    """Get the total number of earthquakes in the response."""
    # 地震记录列表存储在顶级键 'features' 中。我们返回该列表的长度。
    # 使用 .get('features', []) 确保如果 'features' 键不存在，代码也不会崩溃。
    return len(data.get('features', []))


def get_magnitude(earthquake):
    """Retrive the magnitude of an earthquake item."""
    # 震级 (magnitude) 存储在嵌套的 'properties' 字典下的 'mag' 键中。
    # 连续使用 .get() 确保安全访问深层嵌套的数据。
    return earthquake.get('properties', {}).get('mag')


def get_location(earthquake):
    """Retrieve the latitude and longitude of an earthquake item."""
    # There are three coordinates, but we don't care about the third (altitude)
    # 坐标存储在 'geometry' 字典下的 'coordinates' 列表中，顺序为 [经度, 纬度, 深度]。
    # 我们使用默认值 [None, None, None] 来防止索引错误。
    coordinates = earthquake.get('geometry', {}).get('coordinates', [None, None, None])
    
    # 提取第 1 个元素（纬度）和第 0 个元素（经度）。
    latitude = coordinates[1]
    longitude = coordinates[0]
    
    # 返回 (纬度, 经度)
    return latitude, longitude

def get_maximum(data):
    """Get the magnitude and location of the strongest earthquake in the data."""
    # 初始化最大震级为一个不可能的负值，确保第一个地震会被选中。
    max_magnitude = -1.0
    # 初始化最大位置为 N/A。
    max_location = "N/A"

    # 遍历数据字典中 'features' 键下的所有地震记录。
    for earthquake in data.get('features', []):
        # 使用辅助函数获取当前地震的震级。
        magnitude = get_magnitude(earthquake)
        
        # 检查震级是否有效 (非 None) 且大于当前最大震级。
        if magnitude is not None and magnitude > max_magnitude:
            # 找到新的最大值，更新最大震级。
            max_magnitude = magnitude
            
            # 获取新最大值的纬度和经度。
            latitude, longitude = get_location(earthquake)
            
            # 获取地名（place）信息。
            place = earthquake.get('properties', {}).get('place', 'Unknown')
            
            # 格式化位置字符串，包含地名和坐标。
            max_location = f"'{place}' (Lat: {latitude}, Lon: {longitude})"
            
    return max_magnitude, max_location


# With all the above functions defined, we can now call them and get the result
data = get_data()
print(f"Loaded {count_earthquakes(data)}")
max_magnitude, max_location = get_maximum(data)
print(f"The strongest earthquake was at {max_location} with magnitude {max_magnitude}")