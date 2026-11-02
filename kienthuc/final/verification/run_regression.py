"""Chạy unittest, lưu log UTF-8 và kết quả thật, tránh stderr bị PowerShell đổi mã lỗi."""
from pathlib import Path
import json
import sys
import unittest

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
OUT=Path(__file__).resolve().parent
suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'))
with (OUT/'test_suite.txt').open('w',encoding='utf-8') as log:
    result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
summary={'tests_run':result.testsRun,'successful':result.wasSuccessful(),
    'failures':len(result.failures),'errors':len(result.errors),
    'skipped':[{'test':str(test),'reason':reason} for test,reason in result.skipped]}
(OUT/'test_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
raise SystemExit(not result.wasSuccessful())
