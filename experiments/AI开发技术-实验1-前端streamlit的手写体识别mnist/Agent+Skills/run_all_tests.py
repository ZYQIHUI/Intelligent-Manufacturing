"""运行所有测试并保存结果"""
import sys
import os

# 切换到 Agent+Skills 目录
os.chdir(r"D:\SchoolContents\智能创造\小组实验\AI开发技术-实验1-前端streamlit的手写体识别mnist\Agent+Skills")
sys.path.insert(0, ".")

import pytest

# 运行测试，捕获输出
result = pytest.main(["-v", "tests/", "--tb=short"])
print(f"\n{'='*60}")
print(f"Pytest exit code: {result}")
print(f"0=ALL PASSED, 1=SOME FAILED, 2=NO TESTS, 3=INTERNAL ERROR")
