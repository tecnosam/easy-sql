from db.mysql import Connection as con
import re

# TODO: make port to not be a compulsory argument
def join( joiner, seq ):
	res = f"{seq[0]}"
	if len(seq) > 1:
		for i in range(1, len(seq)):
			res += f",{seq[i]}"

	return res

def extract_con_str(con_string):
	# connection string format mysql://usename:pasword@host:port/database
	params = re.sub('(mysql://|:|@|/)', '\t', con_string).strip().split("\t")
	return params

def seq_format(seq, joiner:str, sep = "=", pad = False, padder = "'"):
	if type(seq) == str:
		return seq
	if type(seq) == dict:
		if pad:

			for key in seq:
				if type(seq[key]) == str:
					seq[key] = f"{padder}{seq[key]}{padder}"

		return join(joiner, [f"`{key}`{sep}{seq[key]}"for key in seq])

	if pad:
		for i in range(len(seq)):
			if type(seq[i]) == str:
				seq[i] = f"{padder}{seq[i]}{padder}"

	return join(joiner, seq)

class Instance:
	def __init__( self, con_string = None ):
		try:
			self.db = con( *extract_con_str(con_string) )
		except AttributeError:
			raise Exception("Wrongly formatted connection string")


	def fetch(self, table:str, columns:list = None, conditions:str = None,
				 orders:dict = None, limit:int=None ):

		db = self.db if self else con()
		n_cols = 0 if columns is None else len(columns)

		# turn the parameters to strings
		_cols = "*" if columns is None else seq_format( columns, "," )
		_conds = None if conditions is None else seq_format(conditions, " AND ")
		_orders = None if orders is None else seq_format(orders, ",", " ")

		# build query
		sql = f"SELECT {_cols} FROM `{table}`"
		if conditions is not None:
			sql += f" WHERE {_conds}"
		if orders is not None:
			sql += f" ORDER BY {_orders} "
		if limit is not None:
			sql += f" LIMIT {limit};"

		# execute query
		res = db.get( sql )

		if columns is not None:
			# build json like result
			ret = [ { columns[i]: row[i] for i in range(n_cols) } for row in res ]

			return ret

		return res, sql

	def insert(self, tbl:str, data:dict):
		cols = seq_format( list(data.keys()), ',', pad = True, padder = "`" )
		vals = seq_format( list(data.values()), ',', pad = True )
		sql = f"INSERT into `{tbl}` ({cols}) values ({vals}) "

		return self.db.set(sql), sql

	def update( self, tbl:str, updates:dict, conditions:dict ):
		updates = seq_format( updates, ',', pad = True )
		conditions = seq_format( conditions, ' AND ', pad = True )
		sql = f"UPDATE `{tbl}` SET {updates} WHERE {conditions}"

		return self.db.set(sql), sql

	def delete( self, tbl:str, conditions:dict ):
		conditions = seq_format( conditions, joiner = ' AND ', pad = True )
		sql = f"DELETE FROM `{tbl}` WHERE {conditions}"

		return self.db.set(sql), sql

	def truncate( self, tbl:str ):
		sql = f"TRUNCATE `{tbl}`"

		return self.db.set(sql), sql