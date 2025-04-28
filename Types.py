# Conjunto de tipos de datos permitidos
typenames = {'bool', 'char', 'float', 'int', 'string', 'void'}

# Operaciones binarias válidas
bin_ops = {
	# Operaciones entre enteros
	('int', '+', 'int') : 'int',
	('int', '-', 'int') : 'int',
	('int', '*', 'int') : 'int', 
	('int', '/', 'int') : 'int',

	('int', '<', 'int')  : 'bool',
	('int', '<=', 'int') : 'bool',
	('int', '>', 'int')  : 'bool',
	('int', '>=', 'int') : 'bool',
	('int', '==', 'int') : 'bool',
	('int', '!=', 'int') : 'bool',

	# Operaciones entre flotantes
	('float', '+', 'float') : 'float',
	('float', '-', 'float') : 'float',
	('float', '*', 'float') : 'float',
	('float', '/', 'float') : 'float',

	('float', '<', 'float')  : 'bool',
	('float', '<=', 'float') : 'bool',
	('float', '>', 'float')  : 'bool',
	('float', '>=', 'float') : 'bool',
	('float', '==', 'float') : 'bool',
	('float', '!=', 'float') : 'bool',

	# Operaciones booleanas
	('bool', '&&', 'bool') : 'bool',
	('bool', '||', 'bool') : 'bool',
	('bool', '==', 'bool') : 'bool',
	('bool', '!=', 'bool') : 'bool',

	# Operaciones entre caracteres
	('char', '<', 'char')  : 'bool',
	('char', '<=', 'char') : 'bool',
	('char', '>', 'char')  : 'bool',
	('char', '>=', 'char') : 'bool',
	('char', '==', 'char') : 'bool',
	('char', '!=', 'char') : 'bool',
}

def check_binop(op, left_type, right_type):
	"""
	Verifica si una operación binaria es válida.
	Retorna el tipo de resultado si es válida, o None si no es válida.
	"""
	return bin_ops.get((left_type, op, right_type))


# Operaciones unarias válidas
unary_ops = {
	# Enteros
	('+', 'int') : 'int',
	('-', 'int') : 'int',
	('^', 'int') : 'int',  # Potencia o negación de bits (dependiendo de interpretación)
    
	# Flotantes
	('+', 'float') : 'float',
	('-', 'float') : 'float',

	# Booleanos
	('!', 'bool') : 'bool',
}

def check_unaryop(op, operand_type):
	"""
	Verifica si una operación unaria es válida.
	Retorna el tipo de resultado si es válida, o None si no es válida.
	"""
	return unary_ops.get((op, operand_type))
