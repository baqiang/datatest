# -*- encoding: utf-8 -*-
import time
import pandas as pd
import numpy as np
from DataApi import quantosToken 

from jaqs.data import DataApi

from jaqs.data import RemoteDataService
from jaqs.trade import AlphaBacktestInstance
from jaqs.trade import PortfolioManager
#from jaqs.trade import RealTimeTradeApi

import jaqs.util as jutil
import jaqs.trade.analyze as ana
from jaqs.trade import AlphaStrategy
from jaqs.trade import AlphaTradeApi
from jaqs.trade import model
from jaqs.data import DataView

# 设置文件存储路径
dataview_dir_path = 'demoStrategy/dataview'
backtest_result_dir_path = 'demoStrategy'


data_config = {
  "remote.data.address": "tcp://data.quantos.org:8910",
  "remote.data.username":  quantosToken.phone,
  "remote.data.password":  quantosToken.key}
trade_config = {
  "remote.trade.address": "tcp://gw.quantos.org:8901",
  "remote.trade.username":  quantosToken.phone,
  "remote.trade.password":  quantosToken.key}

# 设置Strategy number, 根据自己的实际情况设置
# 例如：StrategyNo = 1043
StrategyNo = 1045

# -------------------------------------------------------------------------------
# 设置目标股票、业绩基准、权重、时间
# -------------------------------------------------------------------------------
symbol_weights = {'600519.SH': 0.25,
                  '600036.SH': 0.25,
                  '601318.SH': 0.25,
                  '000651.SZ': 0.25}

benchmark = '000300.SH'

my_symbols = ','.join(symbol_weights.keys())
start_date = 20170201
end_date = 20171001

# 定义权重函数
def stockWeight(context, user_options=None):
    return pd.Series(symbol_weights)

# -------------------------------------------------------------------------------
# Main code 这个代码框不需要修改
# -------------------------------------------------------------------------------

def test_save_dataview():
    ds = RemoteDataService()
    ds.init_from_config(data_config)
    dv = DataView()

    props = {'start_date': start_date, 'end_date': end_date,
             'fields': 'sw1',
             'symbol': my_symbols,
             'freq': 1}

    dv.init_from_config(props, ds)
    dv.prepare_data()

    # set the benchmark
    res, _ = ds.daily(benchmark, start_date=dv.start_date, end_date=dv.end_date)
    dv._data_benchmark = res.set_index('trade_date').loc[:, ['close']]

    dv.save_dataview(folder_path=dataview_dir_path)


def test_alpha_strategy_dataview():
    dv = DataView()

    dv.load_dataview(folder_path=dataview_dir_path)

    props = {
        "symbol": dv.symbol,
        "universe": ','.join(dv.symbol),

        "start_date": dv.start_date,
        "end_date": dv.end_date,

        "period": "week",
        "days_delay": 0,

        "init_balance": 1e7,
        "position_ratio": 1.0,
        "commission_rate": 2E-4  # 手续费万2
    }
    props.update(data_config)
    props.update(trade_config)

    trade_api = AlphaTradeApi()

    signal_model = model.FactorSignalModel()
    signal_model.add_signal('stockWeight', stockWeight)

    strategy = AlphaStrategy(signal_model=signal_model, pc_method='factor_value_weight')
    pm = PortfolioManager()

    bt = AlphaBacktestInstance()
    
    context = model.Context(dataview=dv, instance=bt, strategy=strategy, trade_api=trade_api, pm=pm)
    
    signal_model.register_context(context)

    bt.init_from_config(props)

    bt.run_alpha()

    bt.save_results(folder_path=backtest_result_dir_path)
    

def test_backtest_analyze():
    ta = ana.AlphaAnalyzer()
    dv = DataView()
    dv.load_dataview(folder_path=dataview_dir_path)

    ta.initialize(dataview=dv, file_folder=backtest_result_dir_path)

    ta.do_analyze(result_dir=backtest_result_dir_path, selected_sec=ta.universe,
                  brinson_group=None)

# 运行这里跑回测
test_save_dataview()
test_alpha_strategy_dataview()
test_backtest_analyze()