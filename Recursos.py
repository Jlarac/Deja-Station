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
		self.pimin=parser.get('configuraciones','presion inicial min')
		self.pimax=parser.get('configuraciones','presion inicial max')
		self.dpmin=parser.get('configuraciones','delta presion min')
		self.dpmax=parser.get('configuraciones','delta presion max')
		parser = ConfigParser()
		parser.read('Linea_prueba.cfg')
		for numero_serie in parser.sections():
			self.base_de_datos[numero_serie]=[]
			for clave,valor in parser.items(numero_serie):
				self.base_de_datos[numero_serie].append(valor)
	def guardar_configuraciones(self):
		parser = ConfigParser()
		parser.read('config.cfg')
		parser.set('general','nombre',self.nombre_empresa)
		parser.set('general','planta',self.planta)
		parser.set('general','linea',self.linea)
		parser.set('general','proceso',self.proceso)
		parser.set('configuraciones','presion inicial min',self.pimin)
		parser.set('configuraciones','presion inicial max',self.pimax)
		parser.set('configuraciones','delta presion min',self.dpmin)
		parser.set('configuraciones','delta presion max',self.dpmax)
		with open('config.cfg', 'w') as configfile:
			parser.write(configfile)
	def guardar_base_datos(self,seccion,data):
		parser = ConfigParser()
		parser.read('Linea_prueba.cfg')
		nombres=['serie','presion inicial','presion final','delta presion','estatus','fecha','hora','semana']
		parser.add_section(seccion)
		for i,dato in enumerate(data):
			parser.set(seccion, nombres[i], dato)
		with open('Linea_prueba.cfg', 'w') as configfile:
			parser.write(configfile)

data=datos()
data.cargar_configuraciones()