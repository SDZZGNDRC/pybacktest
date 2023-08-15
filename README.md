# PyBacktest

A backtest framework written in python, used for testing trading strategies.

## Features

* **Order Books**: This backtest framework uses order books to simulate the market.  

* Support simulating the **Network Delay**: It takes time to receive the market data and send the orders, and the time is different for different exchanges.

## Structure

### World

The world is consisted of environments and strategies.

methods:

* `start(backtest: Backtest) -> History`: Start the backtest.
* `eval()`: Evaluate the environments by calling registered functions.

### Environment

The environments will be exposed to the strategies, and the strategies will use the environments to make decisions.

#### Info

The environments is consisted of a set of information, which is called `Info`.

#### Time(Info)

Current time in unix milliseconds-timestamp.

#### Exchange(Info)

The exchange that the strategy is trading on.

**properties**:

* MarketData

* Orders  

  The orders that the strategy has placed.  

* Balance

  Current balance of the account.

**methods**:

* `__init__(self, name: str, network_delay: bool = false) -> None`: Initialize the exchange.

> Note: The `network_delay` mechanism is unavailable currently.

* `eval() -> None`: Try to execute the orders that the strategy has placed; update the market data and the balance.

### Indicators(Info)

A variety of indicators that can be used by the strategies.
> To better performance, the indicators will be `calculated lazily`.

```python
# Example of usage.
idc = Indicators()
idc['AveragePrice']['BTC-USDT']['1m'] # The average price of BTC-USDT in the last 1 minute
```

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

methods:

* `eval(env: Environment) -> List[Action]`: Evaluate the environment and return the action that the strategy will take.

#### Metadata

Describe the strategy itself.

* `name`: The name of the strategy.
* `stateful`: Whether the strategy is stateful or not.
* `pairs`: The pairs that the strategy will trade.
* `indicator`: The indicator that the strategy will use.

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

* `hist_level`: The level of the history.

methods:

* `snapshot(env: Environment) -> None`: Record the current state of the environment.
* `save(path: str) -> None`: Save the history to the path.

### MarketData

To reduce the memory usage, load the market data `lazily`.  
The data are originally stored in multiple parquet files.  

**properties**:

* `step_interval`: The time interval between two evaluations.
* `books`: The order books of the market.
* ...

**methods**:

* `__init__(self, step_interval: int, path: str) -> None`: Initialize the market data.
* `eval(steps: int = 1) -> None`: Update the market data to `steps` later.

**Usage**:

```python
# Example of usage.
md = MarketData()
md['books']['BTC-USDT']['asks'][0] # The best ask price of BTC-USDT
md['books']['BTC-USDT']['bids']['2023-08-01', '2023-08-02'][0] # The best bid price of BTC-USDT between 2023-08-01 and 2023-08-02
```

### Order  

The orders that the strategy has placed.  
**properties**:

* `uuid`: The unique identifier of the order.
* `pair`: The pair that the order will trade.
* `orderType`: The type of the order, `Market` or `Limit`.
* `side`: The side of the order, `Buy` or `Sell`.
* `ts`: The timestamp of the order.
* `price`: The price of the order. (Only make sense for `Limit` order)
* `value`: The value of the order.
* `status`: The status of the order, `Pending`, `Filled` or `Canceled`.
* `detail`: The detail of transaction.

**methods**:

* `ATP() -> float`: Return the average transaction price of the order.

### Backtest

Describe a backtest.

* `strategy`: The strategy that will be used in the backtest.
* `start`: The start time of the backtest.
* `end`: The end time of the backtest.
* `eval_step`: The time interval between two evaluations.
* `stop_condition`: The condition that will stop the backtest.
* `hist_level`: The level of the history that will be recorded.
* `exchanges`: The exchanges that the strategy will trade on.

## Test

To complete.
