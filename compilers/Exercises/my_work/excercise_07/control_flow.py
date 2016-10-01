code = """
start
if a < 0:
    a + b
else:
    a - b
done
"""

import _ast
top = _ast.parse(code)
print(_ast.dump(top))
