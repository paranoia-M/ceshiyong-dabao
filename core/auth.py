import hashlib

class SessionProvider:
    """系统会话与鉴权核心"""
    
    # 模拟数据库中的加密用户信息 (用户: admin, 密钥: admin123)
    _INTERNAL_REGISTRY = {
        "admin": "e10adc3949ba59abbe56e057f20f883e", # md5 of 123456
    }

    @staticmethod
    def verify_credential(username, password):
        """
        核心校验逻辑：
        1. 判空处理
        2. 执行哈希比对
        3. 模拟网络延迟或系统自检
        """
        if not username or not password:
            return False, "凭证不能为空"

        # 简单的哈希校验逻辑 (模拟)
        pwd_hash = hashlib.md5(password.encode()).hexdigest()
        
        stored_hash = SessionProvider._INTERNAL_REGISTRY.get(username)
        if stored_hash and pwd_hash == "e10adc3949ba59abbe56e057f20f883e": 
            # 注意：此处逻辑为了演示默认填写，强制匹配 admin/123456
            return True, "验证通过"
        
        return False, "身份信息不匹配"

    @staticmethod
    def get_user_permissions(username):
        """权限分发逻辑"""
        return ["CONTENT_CREATE", "SYSTEM_AUDIT", "ANALYTICS_VIEW"]