# Setup Guide - IQ Option API

Complete step-by-step guide to set up and start using the IQ Option API Python wrapper.

## 📋 Prerequisites

- **Python 3.7 or higher** installed on your system
- **pip** package manager
- **Git** (optional, for cloning the repository)
- **IQ Option account** (recommended: PRACTICE account for testing)

## 🚀 Installation Steps

### Step 1: Clone or Download Repository

**Option A: Using Git**
```bash
git clone https://github.com/yourusername/iqoptionapi.git
cd iqoptionapi
```

**Option B: Download ZIP**
- Download the repository as ZIP
- Extract to your desired location
- Navigate to the extracted folder

### Step 2: Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install requests websocket-client
```

### Step 4: Verify Installation

Test if everything works:

```python
from iqoptionapi import IQ_Option
print("Installation successful!")
```

## 🧪 Quick Test

Create a test file `test_connection.py`:

```python
from iqoptionapi import IQ_Option

# Your IQ Option credentials
EMAIL = "your_email@example.com"
PASSWORD = "your_password"

# Initialize and connect
api = IQ_Option(EMAIL, PASSWORD)
check, reason = api.connect()

if check:
    print("✅ Connection successful!")
    balance = api.get_balance()
    print(f"Balance: ${balance:.2f}")
    api.logout()
else:
    print(f"❌ Connection failed: {reason}")
```

Run:
```bash
python test_connection.py
```

## 🔧 Configuration

### Using Environment Variables (Recommended)

Create a `.env` file (not committed to git):

```bash
IQ_EMAIL=your_email@example.com
IQ_PASSWORD=your_password
IQ_ACCOUNT_TYPE=PRACTICE
```

Python code:
```python
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv('IQ_EMAIL')
PASSWORD = os.getenv('IQ_PASSWORD')
ACCOUNT_TYPE = os.getenv('IQ_ACCOUNT_TYPE', 'PRACTICE')
```

### Account Types

- **PRACTICE**: Demo/training account (recommended for learning)
- **REAL**: Real money account (use with caution!)
- **TOURNAMENT**: Tournament account

## 📂 Project Structure

```
iqoptionapi/
├── README.md              # Main documentation
├── SETUP.md               # This file
├── CONTRIBUTING.md        # Contribution guidelines
├── LICENSE                # License file
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
├── examples/             # Example scripts
│   ├── basic_trading.py
│   ├── market_analysis.py
│   ├── streaming_data.py
│   └── portfolio_management.py
├── api.py                # Low-level API
├── stable_api.py         # High-level API
├── constants.py          # Asset constants
├── http/                 # HTTP modules
├── ws/                   # WebSocket modules
└── ...
```

## 🔐 Security Best Practices

1. **Never commit credentials**
   - Use `.env` files or environment variables
   - Add `.env` to `.gitignore`
   - Keep credentials secure

2. **Start with PRACTICE account**
   - Test all code before using real money
   - Verify connections and data
   - Understand all functions

3. **Use secure networks**
   - Avoid public Wi-Fi for live trading
   - Use VPN if necessary
   - Enable 2FA on your IQ Option account

## 🐛 Troubleshooting

### Common Issues

#### "Module not found" error
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

#### SSL/TLS errors
```bash
# Solution: Update websocket-client
pip install --upgrade websocket-client requests
```

#### Connection timeout
- Check internet connection
- Verify IQ Option servers are online
- Try again later if servers are down

#### Login failed
- Verify credentials are correct
- Check if 2FA is enabled (see examples for 2FA handling)
- Ensure account is not locked

#### "Asset not found"
- Check asset name in `constants.py`
- Use uppercase letters (e.g., "EURUSD" not "eurusd")
- Verify asset is available for your account type

### Getting Help

1. Check existing issues on GitHub
2. Review documentation in README.md
3. Try examples in `examples/` directory
4. Open a new issue if problem persists

## 📚 Next Steps

1. **Read the README.md** for complete API documentation
2. **Try the examples** in `examples/` directory
3. **Explore available assets** in `constants.py`
4. **Test strategies** with PRACTICE account
5. **Join the community** for discussions and updates

## ⚠️ Important Reminders

- ⚠️ **Never commit credentials** to version control
- ⚠️ **Start with PRACTICE account** for testing
- ⚠️ **Understand the risks** before live trading
- ⚠️ **This is educational software** - use responsibly
- ⚠️ **Trading involves financial risk** - never invest more than you can afford to lose

## 🎯 Recommended Learning Path

1. ✅ Complete setup (this guide)
2. ✅ Run `basic_trading.py` example
3. ✅ Understand connection and authentication
4. ✅ Learn to get candles and market data
5. ✅ Test simple trading strategies
6. ✅ Review `market_analysis.py` for analysis
7. ✅ Explore real-time streaming
8. ✅ Develop your own strategies

## 🔗 Useful Links

- [IQ Option Official Website](https://iqoption.com)
- [Python Documentation](https://docs.python.org/)
- [Requests Library Docs](https://requests.readthedocs.io/)
- [WebSocket-Client Docs](https://websocket-client.readthedocs.io/)

---

**Ready to start?** Try running the examples in the `examples/` directory!

