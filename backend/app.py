import os
import sys
import logging
import time
import json
import requests
import warnings
import oss2
from functools import wraps
from datetime import datetime
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

from flask import Flask, jsonify, request, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_flask_exporter import PrometheusMetrics
from flask_cors import CORS

# 加载环境变量
load_dotenv()

# 创建Flask应用实例
app = Flask(__name__)
CORS(app)

# 基础配置
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# 设置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)

# 检查API密钥是否存在
api_key = os.environ.get('DASHSCOPE_API_KEY')
if not api_key:
    logger.error("未找到DASHSCOPE_API_KEY环境变量! 请创建.env文件或设置环境变量")
    api_key = "fake-api-key-for-debug"
else:
    logger.info("API密钥已找到")

# 初始化阿里云OSS
oss_access_key_id = os.environ.get('OSS_ACCESS_KEY_ID')
oss_access_key_secret = os.environ.get('OSS_ACCESS_KEY_SECRET')
oss_endpoint = os.environ.get('OSS_ENDPOINT')
oss_bucket_name = os.environ.get('OSS_BUCKET_NAME')

# 调试信息
logger.info(f"OSS_ACCESS_KEY_ID: {oss_access_key_id}")
logger.info(f"OSS_ENDPOINT: {oss_endpoint}")
logger.info(f"OSS_BUCKET_NAME: {oss_bucket_name}")

if all([oss_access_key_id, oss_access_key_secret, oss_endpoint, oss_bucket_name]):
    try:
        auth = oss2.Auth(oss_access_key_id, oss_access_key_secret)
        bucket = oss2.Bucket(auth, oss_endpoint, oss_bucket_name)
        
        # 测试OSS连接
        try:
            for obj in oss2.ObjectIterator(bucket, max_keys=1):
                logger.info("OSS连接成功")
                break
        except Exception as e:
            logger.error(f"OSS连接测试失败: {e}")
            bucket = None
        
    except Exception as e:
        logger.error(f"OSS初始化失败: {e}")
        bucket = None
else:
    logger.warning("阿里云OSS配置不完整，将使用本地存储（不推荐用于生产环境）")
    bucket = None
    # 创建本地上传目录
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads'))
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    logger.info(f"上传目录: {app.config['UPLOAD_FOLDER']}")

# 初始化扩展
if os.environ.get('FLASK_ENV') == 'development':
    warnings.filterwarnings("ignore", 
                           category=UserWarning, 
                           message="Using the in-memory storage for tracking rate limits")

# 初始化限流器
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# 初始化Prometheus监控
try:
    metrics = PrometheusMetrics(app)
    # 添加自定义指标
    tryon_requests = metrics.counter(
        'tryon_requests_total', 
        'Total number of try-on requests',
        labels={'status': lambda r: r.status_code}
    )
except Exception as e:
    logger.warning(f"Prometheus监控初始化失败: {e}")
    metrics = None

# 阿里云AI试衣客户端
class AliyunAITryOnClient:
    """阿里云AI试衣客户端"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('DASHSCOPE_API_KEY')
        self.submit_url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis'
        self.query_url_template = 'https://dashscope.aliyuncs.com/api/v1/tasks/{}'
        
    def submit_tryon_task(self, person_image_url, garment_image_url, garment_type="top"):
        """
        提交试衣任务到阿里云AI试衣Plus API
        
        参数:
            person_image_url: 人物图像的URL
            garment_image_url: 服装图像的URL
            garment_type: 服装类型 ("top", "bottom", "dress")
            
        返回:
            task_id: 任务ID (成功时) 或 None (失败时)
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-DashScope-Async": "enable"
        }
        
        # 构建请求体
        payload = {
            "model": "aitryon-plus",
            "input": {
                "person_image_url": person_image_url,
            },
            "parameters": {
                "resolution": -1,
                "restore_face": True
            }
        }
        
        # 根据服装类型设置不同的输入字段
        if garment_type == "top":
            payload["input"]["top_garment_url"] = garment_image_url
        elif garment_type == "bottom":
            payload["input"]["bottom_garment_url"] = garment_image_url
        elif garment_type == "dress":
            payload["input"]["top_garment_url"] = garment_image_url
        
        try:
            logger.info(f"提交试衣任务: {person_image_url} + {garment_image_url} ({garment_type})")
            logger.info(f"请求头: {headers}")
            logger.info(f"请求体: {json.dumps(payload, indent=2)}")
            
            response = requests.post(self.submit_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"阿里云响应: {json.dumps(result, indent=2)}")
            
            task_id = result.get('output', {}).get('task_id')
            
            if task_id:
                logger.info(f"任务提交成功，任务ID: {task_id}")
                return task_id
            else:
                logger.error(f"响应中未找到task_id: {result}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"提交试衣任务时请求出错: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"响应内容: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"提交试衣任务时发生未知错误: {e}")
            return None
    
    def query_task_status(self, task_id):
        """
        查询任务状态
        
        参数:
            task_id: 任务ID
            
        返回:
            dict: 包含任务状态和结果信息的字典
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        query_url = self.query_url_template.format(task_id)
        
        try:
            logger.info(f"查询任务状态: {task_id}")
            response = requests.get(query_url, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            logger.info(f"任务状态响应: {json.dumps(result, indent=2)}")
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"查询任务状态时出错: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"响应内容: {e.response.text}")
            return None
    
    def wait_for_task_completion(self, task_id, max_retries=30, interval=5):
        """
        等待任务完成
        
        参数:
            task_id: 任务ID
            max_retries: 最大重试次数
            interval: 检查间隔(秒)
            
        返回:
            dict: 任务结果或None(超时或失败)
        """
        for attempt in range(max_retries):
            result = self.query_task_status(task_id)
            if not result:
                time.sleep(interval)
                continue
            
            task_status = result.get('output', {}).get('task_status')
            
            if task_status == 'SUCCEEDED':
                logger.info(f"任务 {task_id} 完成")
                return result
            elif task_status == 'FAILED':
                error_msg = result.get('output', {}).get('message', '未知错误')
                logger.error(f"任务 {task_id} 失败: {error_msg}")
                return None
            elif task_status in ['PENDING', 'RUNNING', 'PRE-PROCESSING', 'POST-PROCESSING']:
                logger.info(f"任务 {task_id} 状态: {task_status} (尝试 {attempt+1}/{max_retries})")
                time.sleep(interval)
            else:
                logger.warning(f"未知的任务状态: {task_status}")
                time.sleep(interval)
        
        logger.error(f"任务 {task_id} 在 {max_retries} 次尝试后仍未完成")
        return None

# 创建全局客户端实例
tryon_client = AliyunAITryOnClient()

# 辅助函数
def allowed_file(filename):
    """检查文件扩展名是否允许"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_to_oss(file, filename):
    """上传文件到阿里云OSS"""
    if bucket is None:
        # 如果没有配置OSS，使用本地存储
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return f"{request.host_url}uploads/{filename}"
    
    try:
        # 生成唯一文件名
        unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
        
        # 上传到OSS
        bucket.put_object(unique_filename, file)
        
        # 返回OSS文件的公共URL
        oss_url = f"https://{oss_bucket_name}.{oss_endpoint.replace('https://', '')}/{unique_filename}"
        logger.info(f"文件已上传到OSS: {oss_url}")
        return oss_url
    except Exception as e:
        logger.error(f"上传到OSS失败: {e}")
        # 失败时回退到本地存储
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return f"{request.host_url}uploads/{filename}"

# 路由定义
@app.route('/')
def hello():
    return "PAIDA虚拟试穿服务已启动!"

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'ok', 'message': '服务正常运行'})

@app.route('/api/verify')
def verify_api_key():
    """验证DashScope API密钥"""
    headers = {
        "Authorization": f"Bearer {os.environ.get('DASHSCOPE_API_KEY')}"
    }
    try:
        response = requests.get("https://dashscope.aliyuncs.com/api/v1/models", headers=headers, timeout=10)
        if response.status_code == 200:
            return jsonify({"status": "success", "message": "API key is valid"})
        else:
            return jsonify({"status": "error", "message": f"API key validation failed: {response.status_code}"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"API key validation error: {str(e)}"})

@app.route('/api/tryon/upload', methods=['POST'])
def upload_image():
    """上传图片到服务器或OSS"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件部分'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            # 上传文件到OSS或本地
            image_url = upload_to_oss(file, filename)
            
            return jsonify({'url': image_url})
        
        return jsonify({'error': '不支持的文件类型'}), 400
    except Exception as e:
        logger.error(f"上传文件时出错: {e}")
        return jsonify({'error': '上传文件时发生错误'}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """提供已上传的文件（仅当使用本地存储时）"""
    if bucket is not None:
        return jsonify({'error': '文件存储在OSS，请使用OSS URL'}), 404
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/tryon/direct', methods=['POST'])
@limiter.limit("10 per hour")
def direct_tryon():
    """直接处理试衣请求"""
    try:
        logger.info("收到试衣请求")
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '没有提供JSON数据'}), 400
        
        person_url = data.get('person_image_url')
        garment_url = data.get('garment_image_url')
        garment_type = data.get('garment_type', 'top')
        
        logger.info(f"试衣参数: person_url={person_url}, garment_url={garment_url}, garment_type={garment_type}")
        
        if not person_url or not garment_url:
            return jsonify({'error': '缺少必需的参数: person_image_url 或 garment_image_url'}), 400
        
        # 检查URL是否可公开访问
        if 'localhost' in person_url or '127.0.0.1' in person_url:
            return jsonify({'error': '人物图像URL不可公开访问，请使用公共存储服务'}), 400
            
        if 'localhost' in garment_url or '127.0.0.1' in garment_url:
            return jsonify({'error': '服装图像URL不可公开访问，请使用公共存储服务'}), 400
        
        # 提交试衣任务
        task_id = tryon_client.submit_tryon_task(person_url, garment_url, garment_type)
        if not task_id:
            return jsonify({'error': '提交试衣任务失败，请检查API密钥和网络连接'}), 500
        
        # 等待任务完成
        result = tryon_client.wait_for_task_completion(task_id)
        if not result:
            return jsonify({'error': '获取试衣结果失败或任务超时'}), 500
        
        task_status = result.get('output', {}).get('task_status')
        if task_status == 'SUCCEEDED':
            image_url = result['output']['image_url']
            return jsonify({
                'status': 'success',
                'image_url': image_url,
                'task_id': task_id
            })
        else:
            error_msg = result.get('output', {}).get('message', '未知错误')
            return jsonify({
                'status': 'error',
                'message': f'试衣任务失败: {error_msg}',
                'task_id': task_id
            }), 500
            
    except Exception as e:
        logger.exception("处理试衣请求时发生异常")
        return jsonify({'error': '服务器内部错误', 'details': str(e)}), 500

@app.route('/api/tryon/status/<task_id>', methods=['GET'])
def get_tryon_status(task_id):
    """查询试衣任务状态"""
    try:
        if not task_id:
            return jsonify({'error': '缺少task_id参数'}), 400
        
        result = tryon_client.query_task_status(task_id)
        if not result:
            return jsonify({'error': '查询任务状态失败'}), 500
        
        task_status = result.get('output', {}).get('task_status')
        if task_status == 'SUCCEEDED':
            image_url = result['output']['image_url']
            return jsonify({
                'status': 'success',
                'image_url': image_url,
                'task_status': task_status
            })
        else:
            return jsonify({
                'status': task_status.lower(),
                'task_status': task_status,
                'message': result.get('output', {}).get('message', '')
            })
    except Exception as e:
        logger.exception("查询任务状态时发生异常")
        return jsonify({'error': '服务器内部错误', 'details': str(e)}), 500

# 错误处理
@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': '文件太大'}), 413

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"服务器内部错误: {e}")
    return jsonify({'error': '服务器内部错误'}), 500

# 应用启动
if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 5001))
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"启动Flask应用在 {host}:{port}，调试模式: {debug}")
    app.run(host=host, port=port, debug=debug)