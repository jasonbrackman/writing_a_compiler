code = """
start
if a < 0:
    a + b
else:
    a - b
done
"""

import ast
top = ast.parse(code)
print(ast.dump(top))
