# gone/typesys.py
'''
Gone Type System
================
This file implements basic features of the Gone type system.  There is a 
lot of flexibility (and insanity) possible here, but the best strategy
might be to not overthink the problem.  At least not at first.  Here
are the minimal basic requirements:

1. Types have names (e.g., 'int', 'float', 'string')
2. Types have to be comparable. (e.g., int != float).
3. Types support different operators (e.g., +, -, *, /, etc.)

To deal with all this initially, I'd recommend representing types
as simple strings.  Put information about the operators in tables.
Make a few support functions to check operators and perform other tasks.
KEEP IT SIMPLE. REPEAT. SIMPLE. 

Note: You will need to have some coordination with code the checker.py 
module. Try to keep the inner workings of types as isolated as possible. 
Make helper functions as needed.  You may need to change this file
later--ideally you don't want to change everything else when you do.
'''

# List of builtin types.  These will get added to the symbol table
builtin_types = [ 'int', 'float', 'string', 'bool' ]

# Bool type. Used in the checker for conditionals
bool_type = 'bool'

# Error type. Set in the checker on bad declarations, etc.
error_type = None

# Dict mapping all valid binary operations to result type
_supported_binops = {
    # Integer operations
    ('int', '+', 'int') : 'int',
    ('int', '-', 'int') : 'int',
    ('int', '*', 'int') : 'int',
    ('int', '/', 'int') : 'int',
    ('int', '<', 'int') : 'bool',
    ('int', '<=', 'int') : 'bool',
    ('int', '>', 'int') : 'bool',
    ('int', '>=', 'int') : 'bool',
    ('int', '==', 'int') : 'bool',
    ('int', '!=', 'int') : 'bool',

    # Floating point operations
    ('float', '+', 'float') : 'float',
    ('float', '-', 'float') : 'float',
    ('float', '*', 'float') : 'float',
    ('float', '/', 'float') : 'float',
    ('float', '<', 'float') : 'bool',
    ('float', '<=', 'float') : 'bool',
    ('float', '>', 'float') : 'bool',
    ('float', '>=', 'float') : 'bool',
    ('float', '==', 'float') : 'bool',
    ('float', '!=', 'float') : 'bool',

    # String operations
    ('string', '+', 'string') : 'string',
    ('string', '*', 'int') : 'string',
    ('int', '*', 'string') : 'string',
    ('string', '<', 'string') : 'bool',
    ('string', '<=', 'string') : 'bool',
    ('string', '>', 'string') : 'bool',
    ('string', '>=', 'string') : 'bool',
    ('string', '==', 'string') : 'bool',
    ('string', '!=', 'string') : 'bool',

    # Bool operations
    ('bool', '==', 'bool') : 'bool',
    ('bool', '!=', 'bool') : 'bool',
    ('bool', '||', 'bool') : 'bool',
    ('bool', '&&', 'bool') : 'bool',
    }

# Dict mapping all valid unary operations to result type
_supported_unaryops = {
    # Integers
    ('+', 'int') : 'int',
    ('-', 'int') : 'int',

    # Floats
    ('+', 'float') : 'float',
    ('-', 'float') : 'float',

    # Bool
    ('!', 'bool') : 'bool'
}
    
def check_binop(left_type, op, right_type):
    ''' 
    Check the validity of a binary operator. Returns the result type if valid,
    Returns error_type otherwise. 
    '''
    return _supported_binops.get((left_type, op, right_type), error_type)

def check_unaryop(op, type):
    '''
    Check the validity of a unary operator. Returns the result type if valid,
    Returns error_type otherwise.
    '''
    return _supported_unaryops.get((op, type), error_type)
