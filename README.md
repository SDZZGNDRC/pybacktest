# PyBacktest

A backtest framework written in python, used for testing trading strategies.

## Features

* **Order Books**: This backtest framework uses order books to simulate the market.  

* Support **Network Delay**

## Structure

### Environment

The environments will be exposed to the strategies, and the strategies will use the environments to make decisions.

#### Info

The environments is consisted of a set of information, which is called `Info`.

##### Time

Current time in unix milliseconds-timestamp.

##### MarketData

```python
# Example of usage.
md = MarketData()
md['books']['BTC-USDT']['asks'][0] # The best ask price of BTC-USDT
md['books']['BTC-USDT']['bids']['2023-08-01', '2023-08-02'][0] # The best bid price of BTC-USDT between 2023-08-01 and 2023-08-02
```

##### Indicators

A variety of indicators that can be used by the strategies.
> To better performance, the indicators will be `calculated lazily`.

```python
# Example of usage.
idc = Indicators()
idc['AveragePrice']['BTC-USDT']['1m'] # The average price of BTC-USDT in the last 1 minute
```

##### Balance

Current balance of the account.

```python
# Example of usage.
balance = Balance()
balance['USDT'] # The amount of USDT
balance.in_total(quote_Ccy='USDT') # The total amount of USDT
```

### Biologist

methods:

* `start(backtest: Backtest) -> History`: Start the backtest.

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

#### Order

properties:

* `uuid`: The unique identifier of the order.
* `pair`: The pair that the order will trade.
* `orderType`: The type of the order, `Market` or `Limit`.
* `side`: The side of the order, `Buy` or `Sell`.
* `ts`: The timestamp of the order.
* `price`: The price of the order. (Only make sense for `Limit` order)
* `value`: The value of the order.

#### CancelOrder

To complete.

### History

The history of the backtest.

properties:

* `hist_level`: The level of the history.

methods:

* `snapshot(env: Environment) -> None`: Record the current state of the environment.
* `save(path: str) -> None`: Save the history to the path.

### Backtest

Describe a backtest.

* `strategy`: The strategy that will be used in the backtest.
* `start`: The start time of the backtest.
* `end`: The end time of the backtest.
* `eval_step`: The time interval between two evaluations.
* `stop_condition`: The condition that will stop the backtest.
* `hist_level`: The level of the history that will be recorded.
