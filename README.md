# PyBacktest

A backtest framework written in python, used for testing trading strategies.

## Features

* **Order Books**: This backtest framework uses order books to simulate the market.  
* `Slippage/Market impact`
* `margin/leverage`: Support margin trading and leverage trading.
* Support simulating the **Network Delay**: It takes time to receive the market data and send the orders, and the time is different for different exchanges.

## Structure

### World

The world is consisted of environments and strategies.

methods:

* `start(backtest: Backtest) -> History`: Start the backtest.
  * Initialize the Environment
* `eval()`: Evaluate the environments by calling registered functions.

### Environment

The environments will be exposed to the strategies, and the strategies will use the environments to make decisions.

#### Info

The environments is consisted of a set of information, which is called `Info`.

### SimTime

The time in the simulation.

properties:

* `__start: int`: The start time of the simulation.
* `__end: int`: The end time of the simulation.
* `__ts: int`: The timestamp of the simulation time.

methods:

* `__init__(self, start: int, end: int) -> None`: Initialize the simulation time.
* `update(ts: int) -> None`: Update the simulation time to `ts`.
* `__str__() -> str`: Return the string representation of the simulation time in milliseconds.
* `__int__() -> int`: Return the integer representation of the simulation time in milliseconds.
* `__float__() -> float`: Return the float representation of the simulation time in milliseconds.
* `set(ts: int) -> None`: Set the simulation time to `ts`.

### Exchange

The exchange that the strategy is trading on.

**properties**:

* MarketData

* Orders  

  The orders that the strategy has placed.  

* Balance

  Current balance of the account.

**methods**:

* `__init__(self, name: str, simTime: SimTime, network_delay: bool = false) -> None`: Initialize the exchange.

> Note: The `network_delay` mechanism is unavailable currently.

* `eval() -> None`: Try to execute the orders that the strategy has placed; update the market data and the balance.  The order entered earlier should be executed first.  

### Indicators(Info)

A variety of indicators that can be used by the strategies.
> To better performance, the indicators will be `calculated lazily`.

```python
# Example of usage.
idc = Indicators()
idc['AveragePrice']['BTC-USDT']['1m'] # The average price of BTC-USDT in the last 1 minute
```

* `MACD`: Moving Average Convergence Divergence
* `Feedback indicators`: The thought behind this kind of indicator is that the strategy will be able to adjust itself according to its recently performance.
  * `HitRate`: The hit rate of the strategy.
  * `Risk/Reward Ratio`: The risk/reward ratio of the strategy.
* `RSI`: Relative Strength Index
* `Volume`: The number of stocks or contracts traded over a certain period of time.
* `Stochastic oscillator`
* `Williams %R`
* `Ulcer Indicator`
* 订单簿的衍生指标
  * `Order Book Imbalance`: It measures the difference between the total buy orders and sell orders at a specific price level.
  * 变换频率最快的价格档位
  * 买卖双方的订单变化频率
* Indicators about which price-level most trading activities have taken place.

### Balance(Info)

Current balance of the account.  
As a wrapper of all balances in different exchanges.  

```python
# Example of usage.
balance = Balance(exchanges: List[Exchange])
balance['USDT'] # The amount of USDT
balance.in_total(quote_Ccy='USDT') # The total amount of USDT
```

### Strategy

We should consider to separate the strategy into `signal generator` and `risk manager`. The `signal generator` will generate the signals which indicate the direction of the market, and the `risk manager` will decide the amount of the orders.

methods:

* `eval(env: Environment) -> List[Action]`: Evaluate the environment and return the action that the strategy will take.

#### Metadata

Describe the strategy itself.

* `name`: The name of the strategy.
* `stateful: bool`: Whether the strategy is stateful or not.
* `pairs: List[str]`: The pairs that the strategy will trade.
* `indicators: List[str]`: The indicators that the strategy will use.

#### Alpha

Tha alpha generate the signals which indicate the direction of the market.

#### Risk Management

The risk management will decide the amount of the orders.

### Action

Represent the action that the strategy will take.

### EmitOrder(Action)

Create an order.

properties:

* `exchange: str`: The exchange that the order will be placed on.
* `order: Order`: The order that will be created.

### CancelOrder(Action)

Cancel an order.

properties:

* `uuid: str`: The unique identifier of the order that will be canceled.

### History

The history of the backtest.

properties:

* `hist_level: str`: The level of the history.

methods:

* `snapshot(env: Environment) -> None`: Record the current state of the environment.
* `save(path: str) -> None`: Save the history to the path.

### MarketData

To reduce the memory usage, load the market data `lazily`.  
The data are originally stored in multiple parquet files.  

**properties**:

* `books`: The order books of the market.
* ...

**methods**:

* `__init__(self, simTime: SimTime, path: str) -> None`: Initialize the market data.
* `update() -> None`: Update the market data to current simTime.

**Usage**:

```python
# Examples of usage.
md = MarketData()
md['books']['BTC-USDT']['asks'][0] # The best ask price of BTC-USDT
```

### BookLevel

The item of the order book.

**properties**:

* `price: float`: The price of the order.
* `amount: float`: The amount of the order.
* `count: int`: The number of orders. (Maybe not useful)

### Book

The order book structure of the specific pair.

**properties**:

* `asks: Asks`: The asks of the order book.
* `bids: Bids`: The bids of the order book.

**methods**:

* `__init__(self, pair: str, simTime: SimTime, path: str, max_interval: int = 3000) -> None`: Initialize the order books.
* `update() -> None`: Update the order books to current simTime. To enhance the performance, the order books will be `updated only when necessary` instead of updating every time.
* `__getitem__(self, side: str) -> pd.Series[BookLevel]`: Return the asks or bids of the order book.

**Usage**:

```python
# Examples of usage.
book = Book()
book['asks'][0] # The best ask price
```

### Books

The order books structure contains multiple books of different pairs.

**properties**:

* `__books: Dict[str, Book]`: The order books.

**methods**:

* `__init__(self, simTime: SimTime, path: str) -> None`: Initialize the order books.
* `update() -> None`: Update the order books to current simTime. (`Update only when necessary`)
* `__getitem__(self, pair: str) -> Book`: Return the order book of the specific pair. Use `lazy loading` to reduce the memory usage.

### Order  

The orders that the strategy has placed.  
**properties**:

* `uuid: uuid.UUID`: The unique identifier of the order.
* `pair: str`: The pair that the order will trade.
* `orderType: str`: The type of the order, `Market` or `Limit`.
* `side: str`: The side of the order, `Buy` or `Sell`.
* `ts: int`: The timestamp of the order.
* `price: float`: The price of the order. (Only make sense for `Limit` order)
* `amount: float`: The value of the order.
* `status: str`: The status of the order, `Pending`, `Filled` or `Canceled`.
* `details: List[TransDetail]`: The detail of transaction.

**methods**:

* `ATP() -> float`: Return the average transaction price of the order.
* `fee() -> float`: Return the fee of the order.
* `leftAmount() -> float`: Return the amount that has not been executed.
* `exe(price: float, amount: float, fee: float) -> None`: Execute the order.

### TransDetail

The detail of transaction.

properties:

* `pair: str`: The pair that the transaction has traded.
* `side: str`: The side of the transaction, `Buy` or `Sell`.
* `ts: int`: The timestamp of the transaction.
* `price: float`: The price of the transaction.
* `amount: float`: The amount of the transaction.
* `fee: float`: The fee of the transaction.

### Backtest

Describe a backtest.

**properties**:

* `strategy: Strategy`: The strategy that will be used in the backtest.
* `start: int`: The start time of the backtest.
* `end: int`: The end time of the backtest.
* `eval_step: int = 1000`: The time interval between two evaluations.
* `stop_condition: Callable`: The condition that will stop the backtest.
* `hist_level: str`: The level of the history that will be recorded.
* `exchanges: List[str]`: The exchanges that the strategy will trade on.

## Test

To complete.

## Examples of strategies

### Mean Reversion

### Momentum

### MACD Crossover

### Grid Trading
