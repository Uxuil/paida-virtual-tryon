import os

class Config:
    # 阿里云API配置
    DASHSCOPE_API_KEY = os.environ.get('DASHSCOPE_API_KEY')
    
    # 服务器配置
    HOST = '0.0.0.0'
    PORT = 5001
    DEBUG = os.environ.get('FLASK_DEBUG', False)
    
    # 允许的文件扩展名
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    
    # 任务状态检查间隔(秒)和最大重试次数
    TASK_CHECK_INTERVAL = 5
    MAX_TASK_CHECK_RETRIES = 30


class ProductionConfig:
    DEBUG = False
    TESTING = False
    # 生产环境数据库配置
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # 生产环境Redis配置
    # REDIS_URL = os.environ.get('REDIS_URL')