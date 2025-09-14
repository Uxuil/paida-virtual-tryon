import requests
import time
import logging
from config import Config

logger = logging.getLogger(__name__)

class AliyunAITryOnClient:
    """阿里云AI试衣客户端"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or Config.DASHSCOPE_API_KEY
        self.submit_url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis'
        self.query_url_template = 'https://dashscope.aliyuncs.com/api/v1/tasks/{}'
        
    def submit_tryon_task(self, person_image_url, garment_image_url, garment_type="top"):
        """
        提交试衣任务到阿里云
        
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
            # 对于连衣裙，不需要设置下装
            
        try:
            logger.info(f"提交试衣任务: {person_image_url} + {garment_image_url} ({garment_type})")
            response = requests.post(self.submit_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            task_id = result.get('output', {}).get('task_id')
            
            if task_id:
                logger.info(f"任务提交成功，任务ID: {task_id}")
                return task_id
            else:
                logger.error(f"响应中未找到task_id: {result}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"提交试衣任务时请求出错: {e}")
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
            response = requests.get(query_url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"查询任务状态时出错: {e}")
            return None
    
    def wait_for_task_completion(self, task_id, max_retries=None, interval=None):
        """
        等待任务完成
        
        参数:
            task_id: 任务ID
            max_retries: 最大重试次数
            interval: 检查间隔(秒)
            
        返回:
            dict: 任务结果或None(超时或失败)
        """
        max_retries = max_retries or Config.MAX_TASK_CHECK_RETRIES
        interval = interval or Config.TASK_CHECK_INTERVAL
        
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
            elif task_status in ['PENDING', 'RUNNING']:
                logger.info(f"任务 {task_id} 状态: {task_status} (尝试 {attempt+1}/{max_retries})")
                time.sleep(interval)
            else:
                logger.warning(f"未知的任务状态: {task_status}")
                time.sleep(interval)
        
        logger.error(f"任务 {task_id} 在 {max_retries} 次尝试后仍未完成")
        return None

# 创建全局客户端实例
tryon_client = AliyunAITryOnClient()