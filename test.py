import zipfile
import json
# 新建压缩包，放文件进去,若压缩包已经存在，将覆盖。可选择用a模式，追加
str='{"ans": "<?xml version="1.0"?>-<root company="" pagetype="" zoom="1"><rect type="" text="asdasf" w="816" h="780.8000000000001" y="1088" x="1363.2"/><rect type="" text="asdasfczxcdd" w="489.59999999999997" h="563.2" y="2412.8" x="2880"/>'
a=json.loads(str)
print (a)
# 关闭资源
