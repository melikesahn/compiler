
from strings_with_arrows import *

DIGITS = '0123456789' #Sayısal karakterlerin bir dizesini tanımlar. Lexer sınıfında kullanılıcak.
# ERRORS #####################################################################

class Error:
		def __init__(self, pos_start, pos_end, error_name, details): 
      #Hata nesnesinin başlatıcı metodu. Pozisyonları, hata adını ve ayrıntıları alır.
				self.pos_start = pos_start
				self.pos_end = pos_end
				self.error_name = error_name
				self.details = details
		
		def as_string(self):
				result  = f'{self.error_name}: {self.details}\n'
				result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
				result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
				return result

class IllegalCharError(Error): #tanımsız karakterlerin bulunduğu durumlar için kullanılır.
		def __init__(self, pos_start, pos_end, details):
				super().__init__(pos_start, pos_end, 'Illegal Character', details)

class InvalidSyntaxError(Error): #geçersiz sözdizimi durumları için kullanılacak.
		def __init__(self, pos_start, pos_end, details=''):
				super().__init__(pos_start, pos_end, 'Invalid Syntax', details)


# POSITION ###############################################################################################

class Position:
     #Başlatıcı metod, Position nesnesini oluşturur ve gerekli özellikleri atanır: 
    #idx karakterin indeksi, ln satır numarası, col sütun numarası, fn dosya adı ve ftxt tam metin.
		def __init__(self, idx, ln, col, fn, ftxt):
				self.idx = idx
				self.ln = ln
				self.col = col
				self.fn = fn
				self.ftxt = ftxt
		#Bir sonraki karaktere geçmek için kullanılır. current_char mevcut karakteri alır, 
  # eğer mevcut satırın sonuna ulaşılmışsa satır numarasını ve sütun numarasını günceller.
		def advance(self, current_char=None):
				self.idx += 1
				self.col += 1

				if current_char == '\n':
						self.ln += 1
						self.col = 0

				return self
# Bir kopya oluşturur. Bu metod, mevcut Position nesnesinin bir kopyasını döndürür. 
# Bu, analiz sırasında geçici pozisyonlar oluşturmak için kullanılır.
		def copy(self):
				return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)


# TOKENS ####################################################################################

TT_INT		= 'INT'
TT_FLOAT    = 'FLOAT'
TT_PLUS     = 'PLUS'
TT_MINUS    = 'MINUS'
TT_MUL      = 'MUL'
TT_DIV      = 'DIV'
TT_LPAREN   = 'LPAREN'
TT_RPAREN   = 'RPAREN'
TT_EOF		= 'EOF'
TT_STRING   = 'STRING'
#Başlatıcı metod, Token nesnesini oluşturur ve gerekli özellikleri atanır: 
# type_ tokenin türü (TT_INT, TT_FLOAT, TT_PLUS vb.), value tokenin değeri (varsayılan olarak None), 
# pos_start ve pos_end tokenin başlangıç ve bitiş konumları.
class Token:
   
		def __init__(self, type_, value=None, pos_start=None, pos_end=None):
				self.type = type_
				self.value = value
#Eğer pos_start belirtilmişse, bu pozisyon bilgisini tokenin pos_start ve pos_end özelliklerine kopyalar. 
# Bu, bir tokenin metin içindeki konumunu takip etmek için kullanılır.
				if pos_start:
					self.pos_start = pos_start.copy()
					self.pos_end = pos_start.copy()
					self.pos_end.advance()

				if pos_end:
					self.pos_end = pos_end
#Token nesnesinin temsilini oluşturan özel bir metod. 
# Eğer value varsa, tokenin türü ve değerini birleştirerek döndürür. 
# Değilse, sadece tokenin türünü döndürür.		
		def __repr__(self):
				if self.value: return f'{self.type}:{self.value}'
				return f'{self.type}'

# LEXER  #########################################################################################################3
#Bu sınıf, girilen metni tokenize etmek için kullanılır.
class Lexer:
#Başlatıcı metodu, Lexer nesnesini oluşturur ve gerekli özellikleri atanır: 
# fn dosya adı veya metnin kaynağı, text ise tokenize edilecek metin.
		def __init__(self, fn, text):
				self.fn = fn
				self.text = text
				self.pos = Position(-1, 0, -1, fn, text)#Metindeki konumu (Position nesnesi olarak) temsil eden pos özelliğini başlatır. Başlangıçta -1 indeksle, 0 satır ve -1 sütunda olacaktır.
				self.current_char = None  #Şu an işlenen karakteri saklamak için current_char özelliğini başlatır. Başlangıçta None değeri atanır.              
				self.advance() # Lexer oluşturulduktan sonra, ilk karakteri okumak için advance() metodunu çağırır.
#İleri gitme metodudur. pos özelliğini günceller ve bir sonraki karaktere geçer. 
# Eğer metnin sonuna gelinmişse, current_char'ı None olarak ayarlar.
		def advance(self):
				self.pos.advance(self.current_char)
				self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None
#Metni tokenize etmek için kullanılan ana metod. Metnin her karakterini okuyarak, karşılık gelen tokenleri oluşturur.
		def make_tokens(self):
			tokens = [] #Oluşturulan tokenleri depolamak için bir liste oluşturulur.

			while self.current_char != None: #Metnin sonuna gelene kadar döngüyü çalıştırır.
				if self.current_char in ' \t': #Eğer karakter bir boşluk veya sekme ise, bir sonraki karaktere geçer.
					self.advance()
				elif self.current_char in DIGITS: #Eğer karakter bir rakam ise, bir sayıyı oluşturmak için make_number() metodunu çağırır.
					tokens.append(self.make_number())
				elif self.current_char == '+': #Eğer karakter + ise, TT_PLUS tipinde bir token oluşturur.
					tokens.append(Token(TT_PLUS, pos_start=self.pos))
					self.advance()
				elif self.current_char == '-':
					tokens.append(Token(TT_MINUS, pos_start=self.pos))
					self.advance()
				elif self.current_char == '*':
					tokens.append(Token(TT_MUL, pos_start=self.pos))
					self.advance()
				elif self.current_char == '/':
					tokens.append(Token(TT_DIV, pos_start=self.pos))
					self.advance()
				elif self.current_char == '(':
					tokens.append(Token(TT_LPAREN, pos_start=self.pos))
					self.advance()
				elif self.current_char == ')':
					tokens.append(Token(TT_RPAREN, pos_start=self.pos))
					self.advance()
			
				else:#Yukarıdaki durumlar dışında bir karakterle karşılaşılırsa, bir hata oluşturur.
					pos_start = self.pos.copy()
					char = self.current_char
					self.advance()
					return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")
#Son olarak, dosyanın sonunu belirten bir TT_EOF (End of File) tokeni ekler.
			tokens.append(Token(TT_EOF, pos_start=self.pos))
			return tokens, None #Oluşturulan token listesini ve herhangi bir hata olmadığını döndürür.


		def make_number(self):
				num_str = '' #adında boş bir dize oluşturulur. Bu dize, şu anda tanımlanan sayının karakterlerini biriktirecek.
				dot_count = 0 # adında bir sayı oluşturulur ve başlangıçta sıfıra eşitlenir. Bu sayı, nokta (.) karakterinin kaç kez kullanıldığını takip eder.
				pos_start = self.pos.copy() #Sayının başlangıç konumu, mevcut pozisyonun bir kopyası olarak pos_start değişkenine atanır. Bu, sayının başlangıç konumunu takip etmemize olanak tanır.
#Bu döngü, mevcut karakterin rakam (0-9) veya nokta (.) olup olmadığını kontrol eder. 
# Eğer mevcut karakter, None değilse ve rakam veya nokta ise döngü devam eder.
				while self.current_char != None and self.current_char in DIGITS + '.':
						if self.current_char == '.': #Eğer mevcut karakter bir nokta ise:
								if dot_count == 1: break #Eğer daha önce bir nokta kullanıldıysa (yani dot_count 1 ise), döngüyü sonlandırırız. Bu, birden fazla nokta kullanımını engeller.
								dot_count += 1 #değeri artırılır. Bu, bir noktanın kullanıldığını belirtir.
								num_str += '.' #Nokta karakteri, num_str dizesine eklenir.
						else:
								num_str += self.current_char #Eğer mevcut karakter bir rakam ise, o karakter num_str dizesine eklenir.
						self.advance()#Son olarak, mevcut karakterin işlendiğinden emin olmak için lexerde ilerleriz.

				if dot_count == 0: #Eğer nokta kullanılmamışsa:
						return Token(TT_INT, int(num_str), pos_start, self.pos) 
  #num_str dizesi bir tamsayı olarak yorumlanır ve bu tamsayıya karşılık gelen bir Token nesnesi oluşturulur. 
  # Bu nesnenin tipi TT_INT olur ve pos_start ile self.pos (mevcut pozisyon) arasındaki metin aralığına işaret eder.
				else: #Eğer nokta kullanılmışsa:
						return Token(TT_FLOAT, float(num_str), pos_start, self.pos)
#num_str dizesi bir ondalık sayı olarak yorumlanır ve bu ondalık sayıya karşılık gelen bir Token nesnesi oluşturulur. 
# Bu nesnenin tipi TT_FLOAT olur ve pos_start ile self.pos (mevcut pozisyon) arasındaki metin aralığına işaret eder.

# NODES #############################################################################################

class NumberNode:#Bu sınıf, bir sayıyı temsil eden düğümü tanımlar.
#Bir sayı, sözdizim ağacında (parse tree) bir yaprak düğümü olarak kullanılır. tok parametresi, bu düğümün değerini (yani, bir Token nesnesini) içerir.
	def __init__(self, tok):
		self.tok = tok #belirtilen tokeni self.tok özelliğine atar.

	def __repr__(self): #Bu metot, sınıfın dize temsilini oluşturur. Basitçe, düğümün içindeki tokeni gösterir.
		return f'{self.tok}'

class BinOpNode:
#Bu sınıf, iki alt düğüm arasında bir işlemi temsil eden düğümü tanımlar. 
#Örneğin, 2 + 3 ifadesindeki + işlemi bir binop düğümü oluşturur. Sol alt düğüm 2'yi, sağ alt düğüm ise 3'ü temsil eder.
	def __init__(self, left_node, op_tok, right_node):
#Yapıcı metot, bir BinOpNode örneği oluşturur. left_node ve right_node parametreleri, 
#sırasıyla sol ve sağ alt düğümleri temsil eder. op_tok parametresi ise bu işlemin tipini belirten bir Token nesnesidir.
		self.left_node = left_node
		self.op_tok = op_tok
		self.right_node = right_node

	def __repr__(self):# Bu metot, sınıfın dize temsilini oluşturur. Düğümün içindeki sol alt düğüm, işlem türü (Token) ve sağ alt düğümü içeren bir ifadeyi döndürür.
		return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode:
#Bu sınıf, tek bir alt düğüm arasında bir işlemi temsil eden düğümü tanımlar. 
#Örneğin, -5 ifadesindeki - işlemi bir unaryop düğümü oluşturur. Alt düğüm, -5 ifadesini temsil eder.
	def __init__(self, op_tok, node):
#Yapıcı metot, bir UnaryOpNode örneği oluşturur. op_tok parametresi, işlemin türünü belirten bir Token nesnesidir. 
#node parametresi ise bu işlemin uygulandığı alt düğümü temsil eder.
		self.op_tok = op_tok
		self.node = node

	def __repr__(self):
#Bu metot, sınıfın dize temsilini oluşturur. Düğümün içindeki işlem türünü ve uygulandığı alt düğümü içeren bir ifadeyi döndürür.
		return f'({self.op_tok}, {self.node})'
#Bu sınıflar, dil bilgisinin parse edilmesi sırasında oluşturulan ağaç yapısının düğümlerini temsil eder ve bu ağaç yapısı, 
#dil bilgisinin yapısını anlamak ve yorumlamak için kullanılır.

# PARSE RESULT  #######################################################################################

class ParseResult:
	def __init__(self):
#Yapıcı metod, ParseResult sınıfının örneğini oluşturur. İlk olarak, error ve node özelliklerini None olarak ayarlar. 
#Bu özellikler, sırasıyla parse işlemindeki hata durumunu ve parse işleminden elde edilen düğümü temsil eder.
		self.error = None
		self.node = None
#Bu metot, bir alt parse sonucunu (başka bir ParseResult örneği) kaydeder. Eğer res bir ParseResult örneği ise, bu örneğin içindeki hata (error) özelliğini kontrol eder. 
#Eğer hata varsa, bu hatayı mevcut ParseResult örneğinin hata özelliğine (self.error) kaydeder. Aksi takdirde, res'in içindeki düğümü (node) döndürür.
	def register(self, res):
		if isinstance(res, ParseResult):
			if res.error: self.error = res.error
			return res.node

		return res
#Bu metot, bir parse işleminin başarılı olduğunu belirtir ve elde edilen düğümü (node) kaydeder.
	def success(self, node):
		self.node = node
		return self
#Bu metot, bir parse işleminin başarısız olduğunu belirtir ve bir hata nesnesini (error) kaydeder.
	def failure(self, error):
		self.error = error
		return self
#ParseResult sınıfı, parse işleminin sonucunu depolamak ve parse ağacını oluşturmak için kullanılır. 
# Başarılı bir parse işlemi sonucunda, oluşturulan parse ağacı node özelliğinde tutulur. 
# Eğer bir hata oluşmuşsa, bu hata error özelliğinde saklanır.

# PARSER ##########################################################################################3
#Bu kod bir dil bilgisinin ayrıştırılması (parse) işlemini gerçekleştiren bir sınıf olan Parser'ı tanımlar.
class Parser:
#Yapıcı metod, Parser sınıfının bir örneğini oluşturur. Bu metod, parse edilecek tokenleri (tokens) alır ve bu tokenleri Parser sınıfının tokens özelliğine atar. 
# Ayrıca, tok_idx özelliğini -1 olarak başlatır ve advance metodunu çağırarak bir sonraki tokeni alır.
	def __init__(self, tokens):
		self.tokens = tokens
		self.tok_idx = -1
		self.advance()
#Bu metod, Parser'ın mevcut işaretçisini (tok_idx) bir sonraki tokena (veya EOF'a) ilerletir. Eğer işaretçi token listesinin sınırlarını aşmazsa, 
#işaretçiyi bir sonraki tokene ilerletir ve bu tokeni current_tok özelliğine atar. Son olarak, ilerletilen tokeni döndürür.
	def advance(self, ):
		self.tok_idx += 1
		if self.tok_idx < len(self.tokens):
			self.current_tok = self.tokens[self.tok_idx]
		return self.current_tok
#Bu metod, dil bilgisinin ayrıştırılması işlemini başlatır. expr metodunu çağırarak dil bilgisinin bir ifadesini ayrıştırır. 
# Eğer parse işlemi başarılı ise ve mevcut token EOF değilse, InvalidSyntaxError hatası oluşturur ve döndürür.
# Aksi halde, parse metodunun sonucunu döndürür.
	def parse(self):
		res = self.expr()
		if not res.error and self.current_tok.type != TT_EOF:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected '+', '-', '*' or '/'"
			))
		return res
#u Parser sınıfı, dil bilgisinin sentaksını analiz eder ve doğru bir şekilde ayrıştırılmasını sağlar. 
# Eğer sentaksta bir hata bulunursa, bu hata parse metodunun sonucu olarak döndürülür.
#######################################################################3

#Bu metod, bir matematiksel ifadenin en temel parçalarından birini (faktör) parse eder. 
# Faktörler, bir ünary operatör (+ veya -), bir sayı veya parantez içine alınmış bir ifade olabilir. 
# Metod, mevcut tokenin türüne göre farklı davranır:
	def factor(self):
		res = ParseResult()
		tok = self.current_tok
#Eğer mevcut tokenin türü TT_PLUS veya TT_MINUS ise, bir ünary operatörün varlığını belirtir ve bir sonraki faktörü almak için factor metodunu çağırır. 
#Ardından, elde edilen faktörle birlikte bir UnaryOpNode oluşturarak başarı durumunu döndürür.
		if tok.type in (TT_PLUS, TT_MINUS):
			res.register(self.advance())
			factor = res.register(self.factor())
			if res.error: return res
			return res.success(UnaryOpNode(tok, factor))
#Eğer mevcut tokenin türü TT_INT veya TT_FLOAT ise, bir sayıyı temsil eder ve bu sayıyı içeren bir NumberNode oluşturarak başarı durumunu döndürür.		
		elif tok.type in (TT_INT, TT_FLOAT):
			res.register(self.advance())
			return res.success(NumberNode(tok))
#Eğer mevcut tokenin türü TT_LPAREN ise, bir parantez açılışını temsil eder. Bu durumda, bir ifadeyi parse etmek için expr metodunu çağırır. 
# Ardından, bir parantez kapatılışının olup olmadığını kontrol eder. Eğer parantez kapatılışı yoksa, "Expected ')'" hatası döndürür. 
# Aksi halde, ifadeyi başarıyla parse etmiş olur ve başarı durumunu döndürür.
		elif tok.type == TT_LPAREN:
			res.register(self.advance())
			expr = res.register(self.expr())
			if res.error: return res
			if self.current_tok.type == TT_RPAREN:
				res.register(self.advance())
				return res.success(expr)
			else:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected ')'"
				))
#Yukarıdaki durumlar dışında, geçersiz bir ifadeyle karşılaşıldığını belirtir ve "Expected int or float" hatası döndürür.
		return res.failure(InvalidSyntaxError(
			tok.pos_start, tok.pos_end,
			"Expected int or float"
		))
# Bu metod, bir matematiksel terimi parse eder. Bir terim, çarpma veya bölme işlemleri ile ilişkilendirilmiş faktörlerin bir kombinasyonudur. 
# Bu metod, bin_op metodu kullanılarak faktörleri çarpma veya bölme operatörleriyle birleştirir.
	def term(self):
		return self.bin_op(self.factor, (TT_MUL, TT_DIV))
#Bu metod, bir matematiksel ifadeyi parse eder. Bir ifade, toplama veya çıkarma işlemleri ile ilişkilendirilmiş terimlerin bir kombinasyonudur. 
# Bu metod, bin_op metodu kullanılarak terimleri toplama veya çıkarma operatörleriyle birleştirir.
	def expr(self):
		return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

############################################################################
#Bu metod, bir ikili operatörü (örneğin, çarpma veya bölme) içeren matematiksel ifadeleri parse etmek için kullanılır.
	def bin_op(self, func, ops):
#func: Bu, bir alt ifadeyi parse etmek için çağrılan bir fonksiyon referansıdır. Örneğin, term veya factor fonksiyonları bu parametre ile belirtilir.
#ops: Bu, izin verilen operatör türlerini içeren bir dizi veya demettir. Örneğin, çarpma ve bölme operatörlerinin türlerini içerebilir.
		res = ParseResult()
		left = res.register(func())
		if res.error: return res

		while self.current_tok.type in ops:
			op_tok = self.current_tok
			res.register(self.advance())
			right = res.register(func())
			if res.error: return res
			left = BinOpNode(left, op_tok, right)

		return res.success(left)
#Metod, bir ParseResult nesnesi oluşturur ve func fonksiyonunu çağırarak bir sol ifadeyi parse eder. 
# Eğer bir hata varsa, bu hatayı döndürür. Ardından, mevcut tokenin türünün izin verilen operatörler arasında olup olmadığını kontrol eder. 
# Eğer mevcut tokenin türü, izin verilen operatörlerin biriyle eşleşiyorsa, bu operatörü alır ve bir sonraki ifadeyi (sağ ifadeyi) func fonksiyonu ile parse eder. 
# Daha sonra, bu sol ve sağ ifadeleri ve alınan operatörü kullanarak bir BinOpNode oluşturur ve sol ifadeyi bu yeni oluşturulan düğümle değiştirir.
#Son olarak, işlem başarılı olduğunda, oluşturulan BinOpNode düğümünü içeren bir başarı durumu döndürür.



# RUN ################################################################################################

def run(fn, text):
		# Token oluşturma
		lexer = Lexer(fn, text)
		tokens, error = lexer.make_tokens()
		if error: return None, error
		
		# AST oluşturma (abstract syntax tree)
		parser = Parser(tokens)
		ast = parser.parse()
		#sonuç döndürme
		return ast.node, ast.error