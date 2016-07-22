class table(object):
	def __init__(self):
		super(table,self).__init__()
		self.table_info={}

	def set_default_table(self):
		self.table_info.setdefault('table_offset', 0)
		#set table 0 vlan
		self.table_info.setdefault('vlan_table', self.table_info['table_offset'])
