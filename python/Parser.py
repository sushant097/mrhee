#encoding=utf8
import ply.yacc as yacc
from Lexer import tokens

class RheeParser:
	start = 'begin'
	tokens = []

	precedence = (
	('left', 'RA', 'WA'),
	('nonassoc', 'EQ', 'NE'),
	('nonassoc', 'LT', 'LE', 'GT', 'GE'),
	('left', 'PLUS', 'MINUS'),
	('left', 'TIMES', 'DIVIDE'),
	('left', 'MODULUS', 'POWER'),
	('right', 'UMINUS'),
	)

	def p_begin(self, p):
		'begin : program'
		p[0] = p[1]

	def p_program_recursive(self, p):
		'program : stmt NEWLINE program'
		p[0] = [p[1]] + p[3]
	def p_program_stmt(self, p):
		'program : stmt'
		p[0] = [p[1]]
	def p_program_empty(self, p):
		'program : empty'
		p[0] = []

	def p_stmt(self, p):												# stmt can be single-line or multi-line
		'''stmt : slstmt
				| mlstmt
		'''
		p[0] = p[1]

	# Single Line Statements begin
	def p_slstmt(self, p):
		'''slstmt : expression
					| assignment
					| print
					| input
					| slif
					| incremental
		'''
		p[0] = p[1]

	# simple statement begins
	def p_expression(self, p):
		'expression : expr'
		p[0] = ("expression", p.lineno(1), [p[1]])
	def p_assignment(self, p):
		'assignment : IDENTIFIER ASSIGNMENT expr'
		p[0] = ('assign', p.lineno(1), p[1], p[3])
	def p_print(self, p):
		'print : variableExpr LEKHA SEMICOLON'
		p[0] = ('print', p.lineno(2), p[1])
	def p_print_ln(self, p):
		'print : variableExpr LEKHA'
		p[0] = ('println', p.lineno(2), p[1])
	def p_input(self, p):			#@ variableArgs
		'input : variableArgs LEU'
		p[0] = ('input', p.lineno(2), p[1])
	def p_incremental(self, p):
		'''incremental : IDENTIFIER AI expr
						| IDENTIFIER SI expr
						| IDENTIFIER MI expr
						| IDENTIFIER DI expr
		'''
		p[0] = ('increment', p.lineno(1), p[2], p[1], [p[3]])

	# introduces a shift/reduce but is not harmful
	# dangling else problem solved infavor of shift
	def p_slif(self, p):
		'slif : YEDI expr BHAE slstmt ATHAWA slstmt'
		p[0] = ('slif', p.lineno(1), [p[2]], [p[4]], [p[6]])
	def p_slif_noelse(self, p):
		'slif : YEDI expr BHAE slstmt'
		p[0] = ('slif', p.lineno(1), [p[2]], [p[4]], None)

	# Multi-Line Statements begin
	def p_mlstmt(self, p):
		'''mlstmt : mlif
					| forloop
					| whileloop
					| repeatloop
					| function
					| class
		'''
		p[0] = p[1]

	#if statement
	def p_mlif(self, p):
		'mlif : YEDI expr BHAE NEWLINE program DIYE'
		p[0] = ('mlif', p.lineno(1), [p[2]], p[5], None)
	def p_mlif_opt(self, p):
		'mlif : YEDI expr BHAE NEWLINE program optelse DIYE'
		p[0] = ('mlif', p.lineno(1), [p[2]], p[5], p[6])
	# optelse can be empty but that rule introduces a shift/reduce 
	# so feature implemented in base if-statement and that worked !!
	def p_optelse(self, p):										
		'optelse : ATHAWA expr BHAE NEWLINE program optelse'
		p[0] = [('else-if', p.lineno(1), [p[2]], p[4])] + p[5]
	def p_optelse_oelf(self, p):								# to remove one shift/reduce of empty production
		'optelse : ATHAWA expr BHAE NEWLINE program'
		p[0] = [('else-if', p.lineno(1), [p[2]], p[4])] + p[5]
	def p_optelse_else(self, p):
		'optelse : ATHAWA NEWLINE program'
		p[0] = [('else', p.lineno(1), p[3])]

	# for loop
	def p_forloop_default(self, p):
		'''forloop : SABAI IDENTIFIER ASSIGNMENT expr DEKHI expr NEWLINE program BAISA'''
		p[0] = ('forloop', p.lineno(1), p[2], [p[4]], [p[6]], [("decimal", p.lineno(1), '१')], p[8])
	def p_forloop_increment(self, p):
		'''forloop : SABAI IDENTIFIER ASSIGNMENT expr DEKHI expr COLON expr NEWLINE program BAISA'''
		p[0] = ('forloop', p.lineno(1), p[2], [p[4]], [p[6]], [p[8]], p[10])

	# while loop
	def p_whileloop(self, p):
		'whileloop : JABA SAMMA expr NEWLINE program BAJA'
		p[0] = ('whileloop', p.lineno(1), [p[3]], p[5])

	# repeat loop
	def p_repeatloop(self, p):
		'repeatloop : expr CHOTI NEWLINE program TICHO'
		p[0] = ('repeatloop', p.lineno(2), [p[1]], p[4])

	def p_function(self, p):
		'function : KAAM IDENTIFIER LPARA variableArgs RPARA NEWLINE program MAKA'
		p[0] = ('functiondef', p.lineno(1), p[2], p[4], p[7])

	def p_class(self, p):
		'class : KHAKA IDENTIFIER NEWLINE program KAKHA'
		p[0] = ('classdef', p.lineno(1), p[2], p[4])

	# Helping rules to statement rules
	def p_variableExpr_multi(self, p):
		'variableExpr : variableExpr COMMA expr'
		p[0] = p[1] + [[p[3]]]
	def p_variableExpr_single(self, p):
		'variableExpr : expr'
		p[0] = [[p[1]]]
	def p_variableExpr_empty(self, p):
		'variableExpr : empty'
		pass

	def p_variableArgs_multi(self, p):
		'variableArgs : IDENTIFIER COMMA variableArgs'
		p[0] = [p[1]] + p[3]
	def p_variableArgs_single(self, p):
		'variableArgs : IDENTIFIER'
		p[0] = [p[1]]
	def p_variableArgs_bogus(self, p):
		'variableArgs : IDENTIFIER BOGUS'
		pass
	def p_variableArgs_empty(self, p):
		'variableArgs : empty'
		pass

	# Arithmetic Expression begin
	def p_expr(self, p):
		'''expr : expr PLUS expr
				| expr MINUS expr
				| expr TIMES expr
				| expr DIVIDE expr
				| expr MODULUS expr
				| expr POWER expr
		'''
		p[0] = ('arithop', p.lineno(2), p[2], [p[1]], [p[3]])

	def p_expr_brkt(self, p):
		'expr : LPARA expr RPARA'
		p[0] = ('paranthesis', p.lineno(1), [p[2]])

	def p_expr_atom(self, p):
		'''expr : integer
				| float
				| imaginary
				| string
				| identifier
				| functioncall
		'''
		p[0] = p[1]

	def p_integer(self, p):
		'integer : DECIMALINTEGER'
		p[0] = ("decimal", p.lineno(1), p[1])
	def p_integer_octal(self, p):
		'integer : OCTALINTEGER'
		p[0] = ('octal', p.lineno(1), p[1])
	def p_integer_hexa(self, p):
		'integer : HEXAINTEGER'
		p[0] = ('hexa', p.lineno(1), p[1])
	def p_float(self, p):
		'float : FLOAT'
		p[0] = ('float', p.lineno(1), p[1])
	def p_imaginary(self, p):
		'imaginary : IMAGNUMBER'
		p[0] = ('imaginary', p.lineno(1), p[1])
	def p_string(self, p):
		'string : STRING'
		p[0] = ('string', p.lineno(1), p[1])
	def p_identifier(self, p):
		'identifier : IDENTIFIER'
		p[0] = ('identifier', p.lineno(1), p[1])
	def p_functioncall(self, p):
		'functioncall : IDENTIFIER LPARA variableExpr RPARA'
		p[0]= ('functioncall', p.lineno(1), p[1], p[3])

	def p_uminus(self, p):
		'expr : MINUS expr   %prec UMINUS'
		p[0] = ('unaryminus', p.lineno(1), [p[2]])



	# Condition expression begins
	def p_exp_condition(self, p):
		'''expr : expr GT expr
				| expr LT expr
				| expr GE expr
				| expr LE expr
				| expr EQ expr
				| expr NE expr
				| expr RA expr
				| expr WA expr
		'''
		p[0] = ("binop", p.lineno(2), p[2], [p[1]], [p[3]])
	def p_exp_negation(self, p):
		'''expr : expr CHHA
				| expr CHHAINA
		'''
		p[0] = ("negation", p.lineno(2), p[2], [p[1]])

	def p_empty(self, p):
		'empty : '
		pass
	def p_error(self, p):
		print "Syntax Error Near : " + str(p.type) + " in line number " + str(p.lineno)

	def build(self, lexer, **kwargs):
		self.tokens = lexer.get_tokens()
		self.lexer 	= lexer
		self.parser = yacc.yacc(module=self,**kwargs)

	def get_ast(self, data, lexer=None):
		if not lexer:	lexer = self.lexer
		return self.parser.parse(data, lexer=lexer.get_lexer())

	def test(self,data,lexer=None):
		a = self.get_ast(data, lexer)
		print a
		return a


if __name__ == '__main__':
	from Lexer import RheeLexer
	tokens = []
	from Lexer import tokens
	myLexer = RheeLexer()
	myLexer.build()
	myParser = RheeParser()
	myParser.build(myLexer)
	myParser.test(u'''७*८ चोटि
		क लेख
		टिचो
		७*८ चोटि
		क लेख
		टिचो''', myLexer)