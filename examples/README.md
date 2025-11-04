# IQ Option API Examples

This directory contains working examples demonstrating various features of the IQ Option API Python wrapper.

## 📁 Available Examples

### 1. `basic_trading.py`
**Basic Trading Operations**

Demonstrates fundamental operations:
- Connection and authentication
- Account balance checks
- Retrieving historical candles
- Basic trade execution (binary options)

**Usage:**
```bash
python basic_trading.py
```

### 2. `market_analysis.py`
**Technical Analysis and Market Data**

Shows how to perform market analysis:
- Historical data retrieval and analysis
- Technical indicators
- Traders' sentiment analysis
- Simple moving averages (SMA)
- Financial information lookup

**Usage:**
```bash
python market_analysis.py
```

### 3. `streaming_data.py`
**Real-time Data Streaming**

Demonstrates live data monitoring:
- Real-time candle streaming
- Continuous price updates
- Connection monitoring
- Stream management

**Usage:**
```bash
python streaming_data.py
```

### 4. `portfolio_management.py`
**Portfolio and Position Management**

Shows portfolio operations:
- Account overview
- Trading history
- Open positions monitoring
- Commission information
- Instrument information

**Usage:**
```bash
python portfolio_management.py
```

## ⚙️ Setup

1. Install dependencies:
```bash
pip install -r ../requirements.txt
```

2. Update credentials in each example file:
```python
EMAIL = "your_email@example.com"
PASSWORD = "your_password"
```

3. Run any example:
```bash
cd examples
python basic_trading.py
```

## ⚠️ Important Notes

- **All examples use PRACTICE account by default** (demo/training mode)
- **Never commit your credentials** to version control
- **Test thoroughly** before using with real money
- **Trading involves risk** - use at your own discretion

## 🔧 Customization

Feel free to modify these examples to suit your needs:
- Adjust timeframes and intervals
- Change assets/instruments
- Implement your own strategies
- Add custom logging or notifications

## 📚 Learn More

For complete API documentation, see the main [README.md](../README.md) file.

---

**Remember**: These examples are for educational purposes only. Always test your code thoroughly before live trading.

