# b1ddi

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-orange.svg)](https://github.com/mragusa/b1ddi/issues)

> **b1ddi** is a collection of Python tools and scripts for automating interactions with the [Infoblox BloxOne DDI (B1DDI)](https://www.infoblox.com/products/bloxone-ddi/) and [B1TDC](https://www.infoblox.com/products/bloxone-threat-defense/) APIs.

---

## 🧭 Overview

**b1ddi** helps network engineers simplify management of **DNS**, **DHCP**, and **IPAM** resources on Infoblox’s cloud-based DDI platform.

It provides a set of lightweight, CLI-driven Python utilities for:
- Querying and managing DNS zones, records, and views
- Managing DHCP networks, options, and fixed addresses
- Handling user authentication and API tokens
- Working with BloxOne TDC (Tenant Data Center) objects and named lists

All scripts rely on the [Infoblox UDDI API](https://csp.infoblox.com/apidoc) and [BloxOne Module](https://github.com/ccmarris/python-bloxone) and are structured for easy extension and integration.

---

## ✨ Features

- 🔧 Create, update, or delete DNS and DHCP objects  
- 🧩 Modular CLI utilities (DNS, DHCP, B1TDC, etc.)  
- ⚡ Quick command-line interaction with BloxOne API  
- 📦 Simple configuration using `.ini` file  
- 🪶 Lightweight dependencies (no heavy frameworks)  

---

## 🗂️ Project Structure

```
src/
├── b1ddi/
├───├─ bin/
│   ├──── b1ddi-dns-*.py          # DNS management scripts
│   ├──── b1ddi-dhcp-*.py         # DHCP management scripts
│   ├──── b1td-*.py                # Threat Defense scripts 
├── b1ddi-sample.ini            # Example configuration file
├── requirements.txt
├── LICENSE
└── README.md
```

---

## ⚙️ Installation

### Requirements

- Python **3.8+**
- Access credentials (API key / secret) for Infoblox BloxOne
- Internet access to `csp.infoblox.com`

### Install

Clone and install dependencies:

```bash
git clone https://github.com/mragusa/b1ddi.git
cd b1ddi
pip install -r requirements.txt
```

Or, if using **Poetry**:

```bash
poetry install
```

---

## 🧾 Configuration

Copy the example config and update with your own credentials:

```bash
cp b1ddi-sample.ini b1config.ini
```

### Example `b1config.ini`

```ini
[BloxOne]
api_version = 'v1' 
api_key = your_api_key
url = https://csp.infoblox.com
```
---

## 🚀 Usage

Each script provides subcommands (e.g., `get`, `add`, `update`, `delete`), and detailed help:

```bash
python3 b1ddi-dns-record.py --help
```

### Examples

**List DNS Views**
```bash
python3 b1ddi-dns-view.py get
```

**Add a DNS Record**
```bash
python3 b1ddi-dns-record.py add --zone example.com --name api --type A --value 10.0.0.10
```

**Update DHCP Option**
```bash
python3 b1ddi-dhcp-options.py update --network mynet --option 6 --value 8.8.8.8
```

**List B1TDC Named Lists**
```bash
python3 b1tdc.py get-named-lists
```

---

## 🤝 Contributing

Contributions are very welcome!  

To contribute:
1. Fork this repo  
2. Create a new branch (`feature/my-feature`)  
3. Commit your changes  
4. Submit a pull request  

Please ensure your code follows Python best practices (`black`, `flake8`, etc.) and includes updated usage examples or help text if relevant.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 📚 References

- [Infoblox BloxOne DDI API Documentation](https://csp.infoblox.com/apidoc/)
- [Python UDDI Library](https://github.com/ccmarris/python-bloxone)

---

## 💬 Support

If you encounter a bug or have a feature request, please [open an issue](https://github.com/mragusa/b1ddi/issues).  
For Infoblox product-related questions, visit the [Infoblox Community](https://community.infoblox.com/).

---

> _Maintained by [Mike Ragusa](https://github.com/mragusa)_
