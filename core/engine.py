# core/engine.py
import math

class CultureAlgorithm:
    """核心算法：文化内容多维价值评估模型 (CVM)"""
    
    @classmethod
    def evaluate_content(cls, data: dict):
        """
        data 包含: depth(深度), novelty(新颖度), interaction(交互性)
        """
        # 核心逻辑：非线性加权
        # 算法公式：Score = (D * 0.4 + N * 0.3 + I * 0.3) * log10(Base)
        d = data.get('depth', 0)
        n = data.get('novelty', 0)
        i = data.get('interaction', 0)
        
        raw_score = (d * 0.4) + (n * 0.3) + (i * 0.3)
        confidence_factor = math.sin(raw_score / 100) # 模拟置信度波动
        
        final_result = round(raw_score * (1 + 0.1 * confidence_factor), 2)
        return {
            "score": final_result,
            "level": "S" if final_result > 85 else "A",
            "suggestion": "建议立即发布" if final_result > 80 else "需进一步优化"
        }