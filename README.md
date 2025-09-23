# PyBacktest - Python量化回测框架

一个基于Python开发的量化交易策略回测框架，支持订单簿级别的市场模拟。

## 项目简介

PyBacktest是一个专业的量化交易策略回测框架，具有以下核心特性：

* **订单簿模拟**：基于真实的订单簿数据进行市场模拟，支持滑点和市场冲击
* **保证金交易**：支持杠杆交易和保证金管理
* **网络延迟模拟**：可以模拟不同交易所的网络延迟
* **多种交易品种**：支持现货和期货交易
* **高性能**：采用惰性加载和按需更新机制优化性能

## 安装

### 从源码安装

```bash
# 克隆项目
git clone https://github.com/your-username/pybacktest.git
cd pybacktest

# 安装依赖
pip install -e .
```

### 依赖要求

* Python >= 3.8
* pandas >= 2.1.1
* numpy >= 1.26.1
* matplotlib >= 3.8.0
* pyarrow >= 13.0.0

## 快速开始

### 基本使用示例

```python
from pybacktest.world import World
from pybacktest.backtest import Backtest
from pybacktest.strategy import CustomStrategy
from pybacktest.history import HistLevel
from pybacktest.event import CreateEvent
from pybacktest.order import Order, orderType, orderSide
from pybacktest.instrument import Instrument, Pair, InstType
from pybacktest.environment import Environment

# 1. 创建策略
def simple_strategy(env: Environment):
    """简单的买入持有策略"""
    events = []
    
    # 在特定时间点创建订单
    if env.simTime == 1689070299902:
        # 创建交易品种
        inst = Instrument(
            Pair('BTC', 'USDT'), 
            'BTC-USDT', 
            InstType.SPOT,
            0,  # 上市时间
            9999999999999,  # 过期时间
            1.0,  # 合约大小
            0.01  # 最小价格变动
        )
        
        # 创建市价买单
        order = Order(
            inst,
            orderType.MARKET,
            orderSide.BUYLONG,
            env.simTime,
            amount=1.0  # 交易数量
        )
        
        # 创建订单事件
        event = CreateEvent(int(env.simTime), 'OKX', order)
        events.append(event)
    
    return events

# 2. 配置回测
strategy = CustomStrategy('simple_strategy', ['BTC-USDT'], simple_strategy)

backtest = Backtest(
    strategy=strategy,
    start=1689070299902,  # 开始时间戳
    end=1689070343902,    # 结束时间戳
    hist_level=HistLevel.DEBUG,  # 历史记录级别
    exchanges=['OKX'],    # 交易所列表
    eval_step=1000,       # 评估间隔(毫秒)
    initial_balance={'OKX': {'USDT': 10000}}  # 初始资金
)

# 3. 运行回测
world = World('./data/path')  # 数据文件路径
history = world.run(backtest)

# 4. 保存结果
history.save('./backtest_results.json')
```

### 自定义策略开发

```python
from pybacktest.strategy import Strategy
from pybacktest.event import Event
from pybacktest.environment import Environment

class MyCustomStrategy(Strategy):
    """自定义策略示例"""
    
    def __init__(self, name: str, pairs: list):
        super().__init__(name, pairs, indicators=[], stateful=False)
        
    def eval(self, env: Environment) -> list[Event]:
        """策略评估逻辑"""
        events = []
        
        # 获取市场数据
        market_data = env['market_data']
        books = market_data['books']
        
        # 简单的均值回归策略
        btc_book = books['BTC-USDT']
        best_bid = btc_book['bids'][0].price
        best_ask = btc_book['asks'][0].price
        mid_price = (best_bid + best_ask) / 2
        
        # 策略逻辑
        if mid_price < best_bid * 0.99:  # 价格低于买一价1%
            # 创建买入订单
            # ... 订单创建逻辑
            pass
        elif mid_price > best_ask * 1.01:  # 价格高于卖一价1%
            # 创建卖出订单
            # ... 订单创建逻辑
            pass
            
        return events
```

## 核心组件

### World（世界）

回测的核心控制器，管理整个模拟过程。

```python
world = World(data_path, max_interval=2000)
history = world.run(backtest)
```

### Backtest（回测配置）

定义回测的参数和条件。

```python
backtest = Backtest(
    strategy=strategy,
    start=start_ts,
    end=end_ts,
    hist_level=HistLevel.DEBUG,
    exchanges=['OKX'],
    eval_step=1000
)
```

### Strategy（策略）

交易策略的基类，支持自定义策略实现。

```python
class MyStrategy(Strategy):
    def eval(self, env: Environment) -> list[Event]:
        # 策略逻辑
        return events
```

### Environment（环境）

策略运行的环境，包含市场数据、交易所等信息。

```python
env = Environment(data_path, simTime, max_interval=2000)
```

### Exchange（交易所）

模拟交易所行为，包括订单执行、余额管理等。

```python
exchange = Exchange(data_path, simTime, initial_balance={'USDT': 1000})
```

### Order（订单）

交易订单的表示。

```python
order = Order(
    instrument=inst,
    order_type=orderType.MARKET,
    side=orderSide.BUYLONG,
    timestamp=ts,
    amount=1.0,
    leverage=10  # 杠杆倍数
)
```

## 数据格式

### 订单簿数据

PyBacktest使用Parquet格式存储订单簿数据，目录结构如下：

```
data/
├── books/
│   └── BTC-USDT/
│       └── part-0-{start_ts}-{end_ts}.parquet
```

数据列包括：
- `instId`: 交易品种ID
- `price`: 价格
- `size`: 数量
- `side`: 买卖方向 (bid/ask)
- `timestamp`: 时间戳
- `action`: 动作类型 (snapshot/update)

## 高级功能

### 杠杆交易

```python
# 10倍杠杆开多仓
order = Order(
    instrument=inst,
    order_type=orderType.MARKET,
    side=orderSide.BUYLONG,
    timestamp=ts,
    amount=1.0,
    leverage=10,
    action=orderAction.OPEN
)
```

### 指标计算

框架支持多种技术指标的计算：

```python
# 获取移动平均价格
avg_price = env['indicators']['AveragePrice']['BTC-USDT']['1m']

# MACD指标
macd = env['indicators']['MACD']['BTC-USDT']

# RSI指标  
rsi = env['indicators']['RSI']['BTC-USDT']
```

### 历史记录

支持不同级别的历史记录：

```python
from pybacktest.history import HistLevel

# 调试级别 - 记录所有细节
backtest = Backtest(hist_level=HistLevel.DEBUG)

# 标准级别 - 记录关键信息
backtest = Backtest(hist_level=HistLevel.STANDARD)

# 最小级别 - 只记录最终结果
backtest = Backtest(hist_level=HistLevel.MINIMAL)
```

## 开发指南

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_Exchanges.py
```

### 代码结构

```
src/pybacktest/
├── backtest.py      # 回测配置
├── world.py         # 世界模拟器
├── strategy.py      # 策略基类
├── environment.py   # 环境管理
├── exchanges.py     # 交易所模拟
├── order.py         # 订单管理
├── positions.py     # 仓位管理
├── instrument.py    # 交易品种
├── event.py         # 事件系统
├── history.py       # 历史记录
├── simTime.py       # 模拟时间
└── marketdata.py    # 市场数据
```

### 扩展框架

您可以扩展框架以支持新的功能：

1. **自定义指标**：继承`Indicator`类
2. **新的订单类型**：扩展`Order`类
3. **额外的数据源**：实现新的数据加载器

## 示例策略

### 均值回归策略

基于价格偏离均值的策略，当价格偏离均值一定幅度时进行反向交易。

### 动量策略

跟随价格趋势，在价格上涨时买入，下跌时卖出。

### MACD交叉策略

基于MACD指标的金叉和死叉信号进行交易。

### 网格交易策略

在特定价格区间内设置多个买卖点位。

## 性能优化

* **惰性加载**：市场数据按需加载，减少内存占用
* **按需更新**：订单簿只在需要时更新
* **高效数据结构**：使用优化的数据结构和算法

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

本项目采用MIT许可证。详见LICENSE文件。

## 支持

如有问题或建议，请通过以下方式联系：
- 创建Issue
- 发送邮件至：sdzzgndrc@gmail.com

## 更新日志

### v1.1.0
- 新增杠杆交易支持
- 优化性能表现
- 完善文档和示例

### v1.0.0
- 初始版本发布
- 基础回测功能
- 订单簿模拟支持
