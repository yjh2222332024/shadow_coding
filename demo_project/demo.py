# 测试文件：演示安全审计拦截

def calculate_discount(price, level):
    """折扣计算"""
    if level > 10:
        return price * 0.7
    return price * 0.9

def greet_user(name):
    """问候用户"""
    return f"Hello, {name}!"
