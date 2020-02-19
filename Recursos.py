from configparser  import ConfigParser
class datos(object):
	def cargar_configuraciones(self):
		self.plantas,self.lineas_por_planta=[],{}
		self.menu_lineas_por_plantas={}
		parser = ConfigParser()
		parser.read('config.cfg')
		self.nombre_empresa=parser.get('general','nombre')
		for numero,planta in parser.items('Plantas'):
			parser = ConfigParser()
			parser.read('config.cfg')
			self.menu_lineas_por_plantas[planta]={}
			for numero,linea in parser.items(planta):
				self.menu_lineas_por_plantas[planta][linea]={}
				parser = ConfigParser()
				parser.read(linea+'.cfg')
				try: 
					for llave,valor in parser.items('Procesos'):	
						self.menu_lineas_por_plantas[planta][linea][valor]={}
				except:
					pass
	def guardar_configuraciones(self):
		pass
data=datos()
data.cargar_configuraciones()