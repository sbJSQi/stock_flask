import pandas as pd
import requests
from sqlalchemy import create_engine

def getUrl(stock_name: list, stock_code: list, start_date: list, end_date: str) -> dict:
    """
    获取请求的url
    :return: 封装好的请求url的字典
    """
    # 请求数据的源地址
    base_url = 'https://q.stock.sohu.com/hisHq?'
    temp_url_list = []      # 暂存组成的单个请求地址
    url_dict = {}           # 初始化返回的字典
    for date in start_date:
        if date == '19910102':
            for i in range(2):
                temp_url = base_url + f'code=zs_{stock_code[i]}&start={date}&end={end_date}'
                temp_url_list.append(temp_url)
        elif date == '19910405':
            temp_url = base_url + f'code=zs_{stock_code[2]}&start={date}&end={end_date}'
            temp_url_list.append(temp_url)
        else:
            temp_url = base_url + f'code=zs_{stock_code[3]}&start={date}&end={end_date}'
            temp_url_list.append(temp_url)
    # 组合URL字典
    for i, name in enumerate(stock_name):
        url_dict[name] = temp_url_list[i]
    return url_dict


def getData(url_dict: dict, stock_name: list[str]):
    """
    获取股票历史数据，并存入MySQL数据库
    :return: 无返回值
    """
    # 数据库连接信息，根据实际情况填写
    db_info = {
        'user': 'root',
        'password': '123456',
        'host': 'localhost',
        'port': '3306',
        'database': 'stock_flask'
    }
    # 创建数据库连接引擎
    engine = create_engine(f"mysql+pymysql://{db_info['user']}:{db_info['password']}@{db_info['host']}:{db_info['port']}/{db_info['database']}")
    # 定义Excel的表头
    columns: list[str] = ['日期', '开盘', '收盘', '涨跌额', '涨跌幅', '最低', '最高', '成交量(手)', '成交金额(万)', '换手率']
    
    def translate_to_english(chinese_name: str) -> str:
        # 将中文股票名称转换为英文
        if chinese_name == "A股指数":
            return "ASharesIndex"
        elif chinese_name == "上证指数":
            return "ShanghaiIndex"
        elif chinese_name == "沪深300":
            return "CSI300"
        elif chinese_name == "深证综指":
            return "ShenzhenCompositeIndex"
        else:
            # 如果名称不在上述四个中，则返回原名称
            return chinese_name
    
    for name in stock_name:
        response = requests.get(url=url_dict[name])
        # 将请求到的数据转换为json格式
        response_json = response.json()
        # 将获取的数据转换为pandas所支持的dataframe数据对象
        data_frame = pd.DataFrame(data=response_json[0]['hq'], columns=columns)
        # 存入数据库
        # 将中文股票名称转换为英文表名
        english_stock_name = translate_to_english(name)
        english_table_name = f"{english_stock_name}HistoricalData"
        # 如果表存在，则删除表
        if engine.has_table(english_table_name):
            engine.execute(f"DROP TABLE {english_table_name}")
        # 保存数据到数据库
        data_frame.to_sql(name=english_table_name, con=engine, index=False)


if __name__ == '__main__':
    stockCode = ['000001', '000002', '399106', '399300']
    stockName = ['上证指数', 'A股指数', '深证综指', '沪深300']
    startDate = ['19910102', '19910405', '20050409']
    # 获取当天的日期，并格式化
    endDate = '20240526'  # 此处填写你想要的结束日期
    url_dict = getUrl(stock_name=stockName, stock_code=stockCode, start_date=startDate, end_date=endDate)
    getData(url_dict=url_dict, stock_name=stockName)
