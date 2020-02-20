from configparser  import ConfigParser
class datos(object):
	def cargar_configuraciones(self):
		self.base_de_datos={}
		parser = ConfigParser()
		parser.read('config.cfg')
		self.nombre_empresa=parser.get('general','nombre')
		self.planta=parser.get('general','planta')
		self.linea=parser.get('general','linea')
		self.proceso=parser.get('general','proceso')
		parser = ConfigParser()
		parser.read('Linea_prueba.cfg')
		for numero_serie in parser.sections():
			self.base_de_datos[numero_serie]=[]
			for clave,valor in parser.items(numero_serie):
				self.base_de_datos[numero_serie].append(valor)
	def guardar_configuraciones(self):
		pass
data=datos()
data.cargar_configuraciones()