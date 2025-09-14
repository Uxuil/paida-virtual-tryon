try:
    from flask import Flask
    print("✓ Flask 导入成功")
except ImportError:
    print("✗ Flask 导入失败")

try:
    import requests
    print("✓ requests 导入成功")
except ImportError:
    print("✗ requests 导入失败")

try:
    from dotenv import load_dotenv
    print("✓ python-dotenv 导入成功")
except ImportError:
    print("✗ python-dotenv 导入失败")
