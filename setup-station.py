import gi,datetime,cairo,math,threading,sys,time
sys.path.append("C:/msys64/usr/lib/python3.7/site-packages")
import serial
import serial.tools.list_ports
from configparser  import ConfigParser
from Recursos import data as Recursos
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, GLib, Gdk, Gio, GdkPixbuf

program = 'Deja Station'
version = '0.1.1'
copyright = '(c) Jlara Industries'
comments = 'Programa para estacion de trabajo y recopilacion de datos'
website = 'https://github.com/Jlarac/Deja-Station'
nameicon = 'python.png'
autors = ['Jairo Lara']

class MyWindow(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self)
		self.set_default_size(800, 500)
		self.cargar_headerbar_paginas()
		self.set_icon_from_file(nameicon)
		self.ventana_actual,self.linea_actual,self.proceso_actual=[],[],[]
		self.analizando,self.serial_port,self.puerto=False,False,''
		self.conectar_puerto()

		t = threading.Thread(target=self.escuchando_puerto)
		t.daemon = True
		t.start()

		self.menu_principal=Gtk.Notebook()
		self.menu_principal.set_show_tabs(False)
		self.add(self.menu_principal)

		self.now=datetime.datetime.now()
		self.weeknum=str(datetime.date(self.now.year, self.now.month, self.now.day).isocalendar()[1])
		self.fecha=str(self.now.month)+'/'+str(self.now.day)+'/'+str(self.now.year)
		self.hora=str(self.now.hour)+':'+str(self.now.minute)+':'+str(self.now.second)
		
		self.box_paginas=Gtk.Box(spacing=5)
		self.ventana_pagina()
		self.menu_principal.append_page(self.box_paginas)
		self.box_configuraciones=Gtk.Box(spacing=16)
		self.box_configuraciones.set_hexpand(True)
		self.ventana_configuracion()
		self.menu_principal.append_page(self.box_configuraciones)
		if self.serial_port:
			self.mensaje('Conectado puerto: '+self.puerto)
		else:
			self.mensaje('No conectado a puerto serial')
	def cargar_headerbar_paginas(self):
		self.hb = Gtk.HeaderBar()
		self.hb.set_show_close_button(True)
		self.hb.props.title = program
		self.hb.props.subtitle = Recursos.nombre_empresa
		caja_headerbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		button = Gtk.Button()
		icon = Gio.ThemedIcon(name="applications-system-symbolic")
		image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
		button.add(image)
		button.connect('clicked',self.ir_ventana_configuracion)
		button2 = Gtk.Button()
		icon = Gio.ThemedIcon(name="preferences-system-details-symbolic")
		image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
		button2.connect('clicked',self.ventana_acerca)
		button2.add(image)
		self.entrada_busqueda=Gtk.SearchEntry()
		self.entrada_busqueda.connect('search_changed',self.iniciar_busqueda)
		self.url_estacion=self.poner_etiqueta('	'+Recursos.planta+'  -  '+Recursos.linea+'  -  '+Recursos.proceso)
		caja_headerbar.add(button)
		caja_headerbar.add(self.url_estacion)
		self.hb.pack_start(caja_headerbar)
		self.hb.pack_end(button2)
		self.hb.pack_end(self.entrada_busqueda)
		self.set_titlebar(self.hb)
	def poner_etiqueta(self,texto):
		label=Gtk.Label()
		label.set_text(texto)
		label.set_valign(Gtk.Align.CENTER)
		return label
	def ventana_pagina(self):
		grid_pagina=Gtk.Grid()
		box_encabezado=Gtk.Box(spacing=16)
		#box_encabezado.set_hexpand(True)

		#color_ultima_pieza=Gtk.ColorButton()
		
		#color_ultima_pieza.show_editor(False)
		#color_verde=Gdk.RGBA()
		#color_verde.red=0.0
		#color_verde.green=1.0
		#color_verde.blue=0.0
		#color_verde.alpha=1.0
		#color_ultima_pieza.set_rgba(color_verde)
		#color_ultima_pieza.set_title('Label')

		#color_ultima_pieza.set_property("show-editor", False)
		#color_ultima_pieza.props.show_editor=False

		eventobox=Gtk.EventBox()
		self.mensaje_eventobox_pagina=self.poner_etiqueta('Programa iniciado correctamente')
		eventobox.add(self.mensaje_eventobox_pagina)

		grid_1=Gtk.Grid()
		grid_1.set_column_spacing(15)
		grid_1.set_row_spacing(15)

		label=self.poner_etiqueta('Numero de serie')
		self.entrada_escaner = Gtk.Entry()
		self.entrada_escaner.connect('activate',self.entrada_escaner_enter)
		self.entrada_escaner.set_valign(Gtk.Align.CENTER)
		self.serie_analizando=self.poner_etiqueta('')
		grid_1.attach(label, 0, 0, 1, 1)
		grid_1.attach_next_to(self.entrada_escaner, label, Gtk.PositionType.RIGHT, 1, 1)
		grid_1.attach_next_to(self.serie_analizando,self.entrada_escaner, Gtk.PositionType.RIGHT, 1, 1)
		grid_2=Gtk.Grid()
		grid_2.set_column_spacing(15)
		grid_2.set_row_spacing(15)
		label2=self.poner_etiqueta('FlexFlow')
		self.ff_switch = Gtk.Switch()
		self.ff_switch.connect("notify::active", self.on_switch_activated)
		self.ff_switch.set_active(True)
		boton_cancelar_analizando=Gtk.Button()
		boton_cancelar_analizando.set_label('Cancelar')
		boton_cancelar_analizando.connect('clicked',self.cancelar_analisis)
		grid_2.attach(label2, 0, 0, 1, 1)
		grid_2.attach_next_to(self.ff_switch, label2, Gtk.PositionType.RIGHT, 1, 1)
		grid_2.attach_next_to(boton_cancelar_analizando,label2, Gtk.PositionType.LEFT, 1, 1)

		box_encabezado.pack_start(grid_1, True, True, 0)
		box_encabezado.pack_end(grid_2, False, True, 0)
		box_encabezado.set_hexpand(True)
		
		self.liststore_base_datos = Gtk.ListStore(str,str,str,str,str,str,str,str)
		valores_semanal=[]
		for valor in Recursos.base_de_datos.keys():
			if Recursos.base_de_datos[valor][7]==str(self.weeknum):	
				valores_semanal.append(Recursos.base_de_datos[valor])
		for valor in range(len(valores_semanal)-1,-1,-1):
			self.liststore_base_datos.append(valores_semanal[valor])

		self.current_filter_language = None
		self.language_filter = self.liststore_base_datos.filter_new()
		self.language_filter.set_visible_func(self.language_filter_func)

		self.scrollable_treelist = Gtk.ScrolledWindow()
		self.scrollable_treelist.set_vexpand(True)
		self.treeview = Gtk.TreeView.new_with_model(self.language_filter)
		for i, column_title in enumerate(['N. Serie','P. Inicial','P. Final','Delta P.','Estado','Fecha','Hora','Semana']):
			renderer = Gtk.CellRendererText()
			column = Gtk.TreeViewColumn(column_title, renderer, text=i)
			column.set_expand(True)
			column.set_resizable(True)
			self.treeview.append_column(column)

		grid_pagina.attach(eventobox, 0, 0, 1, 1)
		grid_pagina.attach_next_to(box_encabezado,eventobox,Gtk.PositionType.BOTTOM,1,1)
		grid_pagina.attach_next_to(self.scrollable_treelist,box_encabezado,Gtk.PositionType.BOTTOM,1,1)

		grid_pagina.set_column_spacing(10)
		grid_pagina.set_row_spacing(10)

		self.scrollable_treelist.add(self.treeview)
		self.box_paginas.pack_start(grid_pagina, True, True, 0)
	def ventana_configuracion(self):
		grid_principal=Gtk.Grid()
		grid_principal.set_column_spacing(50)
		grid_principal.set_row_spacing(50)
		self.action_bar=Gtk.ActionBar()
		self.action_bar.set_hexpand(True)

		button2 = Gtk.Button()
		icon = Gio.ThemedIcon(name="emblem-default-symbolic")
		image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
		button2.connect('clicked',self.cambio_entradas_configuraciones)
		button2.add(image)

		label9=self.poner_etiqueta('Puertos')
		self.puertos_liststore = Gtk.ListStore(str)
		try:
			for valor in self.serial_ports:
				self.puertos_liststore.append([valor])
		except:
			pass
		self.puertos_combo = Gtk.ComboBox.new_with_model(self.puertos_liststore)
		renderer_text = Gtk.CellRendererText()
		self.puertos_combo.pack_start(renderer_text, True)
		self.puertos_combo.add_attribute(renderer_text, "text", 0)
		self.puertos_combo.set_active(0)

		label=self.poner_etiqueta('Guardar')
		self.action_bar.pack_start(label9)
		self.action_bar.pack_start(self.puertos_combo)
		self.action_bar.pack_end(button2)
		self.action_bar.pack_end(label)

		grid_configuraciones=Gtk.Grid()
		grid_configuraciones.set_column_spacing(15)
		grid_configuraciones.set_row_spacing(15)
		grid_configuraciones2=Gtk.Grid()
		grid_configuraciones2.set_column_spacing(15)
		grid_configuraciones2.set_row_spacing(15)

		label=self.poner_etiqueta('Empresa')
		self.entrada_empresa = Gtk.Entry()
		self.entrada_empresa.set_text(Recursos.nombre_empresa)
		self.entrada_empresa.set_valign(Gtk.Align.CENTER)
		label2=self.poner_etiqueta('Planta')
		self.entrada_planta = Gtk.Entry()
		self.entrada_planta.set_text(Recursos.planta)
		self.entrada_planta.set_valign(Gtk.Align.CENTER)
		label3=self.poner_etiqueta('Linea')
		self.entrada_linea = Gtk.Entry()
		self.entrada_linea.set_text(Recursos.linea)
		self.entrada_linea.set_valign(Gtk.Align.CENTER)
		label4=self.poner_etiqueta('Proceso')
		self.entrada_proceso = Gtk.Entry()
		self.entrada_proceso.set_text(Recursos.proceso)
		self.entrada_proceso.set_valign(Gtk.Align.CENTER)

		ajuste_presion1 = Gtk.Adjustment(value=-8.0, lower=-8.5, upper=-6.0, step_increment=0.5, page_increment=0.0, page_size=0.0)
		ajuste_presion2 = Gtk.Adjustment(value=-9.0, lower=-10.0, upper=-8.5, step_increment=0.5, page_increment=0.0, page_size=0.0)
		self.spin_presion_min = Gtk.SpinButton(adjustment=ajuste_presion2, climb_rate=0.0, digits=1.0)
		self.spin_presion_max = Gtk.SpinButton(adjustment=ajuste_presion1, climb_rate=0.0, digits=1.0)
		ajuste_delta1 = Gtk.Adjustment(value=0.009000, lower=0.000000, upper=0.010000, step_increment=0.0001, page_increment=0, page_size=0)
		ajuste_delta2 = Gtk.Adjustment(value=0.012000, lower=0.010000, upper=0.020000, step_increment=0.0001, page_increment=0, page_size=0)
		self.spin_delta_min = Gtk.SpinButton(adjustment=ajuste_delta1, climb_rate=0.0, digits=6)
		self.spin_delta_max = Gtk.SpinButton(adjustment=ajuste_delta2, climb_rate=0.0, digits=6)

		label5=self.poner_etiqueta('Presion inicial min')
		label6=self.poner_etiqueta('Presion inicial max')
		label7=self.poner_etiqueta('Delta presion min')
		label8=self.poner_etiqueta('Delta presion max')

		grid_configuraciones.attach(label, 0, 0, 1, 1)
		grid_configuraciones.attach_next_to(self.entrada_empresa,label,Gtk.PositionType.RIGHT,1,1)
		grid_configuraciones.attach_next_to(label2,label,Gtk.PositionType.BOTTOM,1,1)
		grid_configuraciones.attach_next_to(self.entrada_planta,label2,Gtk.PositionType.RIGHT,1,1)
		grid_configuraciones.attach_next_to(label3,label2,Gtk.PositionType.BOTTOM,1,1)
		grid_configuraciones.attach_next_to(self.entrada_linea,label3,Gtk.PositionType.RIGHT,1,1)
		grid_configuraciones.attach_next_to(label4,label3,Gtk.PositionType.BOTTOM,1,1)
		grid_configuraciones.attach_next_to(self.entrada_proceso,label4,Gtk.PositionType.RIGHT,1,1)

		grid_configuraciones2.attach(label5, 0, 0, 1, 1)
		grid_configuraciones2.attach_next_to(self.spin_presion_min,label5,Gtk.PositionType.RIGHT,1,1)
		grid_configuraciones2.attach_next_to(label6,label5,Gtk.PositionType.BOTTOM,1,1)
		grid_configuraciones2.attach_next_to(self.spin_presion_max,label6,Gtk.PositionType.RIGHT,1,1)
		grid_configuraciones2.attach_next_to(label7,label6,Gtk.PositionType.BOTTOM,1,1)
		grid_configuraciones2.attach_next_to(self.spin_delta_min,label7,Gtk.PositionType.RIGHT,1,1)
		grid_configuraciones2.attach_next_to(label8,label7,Gtk.PositionType.BOTTOM,1,1)
		grid_configuraciones2.attach_next_to(self.spin_delta_max,label8,Gtk.PositionType.RIGHT,1,1)

		eventobox=Gtk.EventBox()
		self.mensaje_eventobox_configuraciones=self.poner_etiqueta('Programa iniciado correctamente')
		eventobox.add(self.mensaje_eventobox_configuraciones)

		grid_principal.attach(eventobox, 0, 0, 2, 1)
		grid_principal.attach_next_to(self.action_bar,eventobox,Gtk.PositionType.BOTTOM,2,1)
		grid_principal.attach_next_to(grid_configuraciones,self.action_bar,Gtk.PositionType.BOTTOM,1,1)
		grid_principal.attach_next_to(grid_configuraciones2,grid_configuraciones,Gtk.PositionType.RIGHT,1,1)

		self.box_configuraciones.pack_end(grid_principal, False, False, 0)
	def ventana_acerca(self, widget):
		about = Gtk.AboutDialog()
		about.set_program_name(program)
		about.set_version(version)
		about.set_authors(autors)
		about.set_copyright(copyright)
		about.set_comments(comments)
		about.set_website(website)
		icon=GdkPixbuf.Pixbuf.new_from_file(nameicon)
		about.set_logo(icon)
		about.run()
		about.destroy()
	def ir_ventana_configuracion(self,button):
		if self.menu_principal.get_current_page()==0:
			self.menu_principal.set_current_page(1)
		else:
			self.menu_principal.set_current_page(0)
	def language_filter_func(self, model, iter, data):
		columna=0
		if self.current_filter_language is None or self.current_filter_language == "None" or self.current_filter_language == "":
			return True
		else:
			for i in range(8):
				if model[iter][i] == self.current_filter_language:
					columna=i
			return model[iter][columna] == self.current_filter_language
	def iniciar_busqueda(self,widget):
		if widget.get_text()!="":
			self.liststore_base_datos.clear()
			valores_semanal=[]
			for valor in Recursos.base_de_datos.keys():
				valores_semanal.append(Recursos.base_de_datos[valor])
			for valor in range(len(valores_semanal)-1,-1,-1):
				self.liststore_base_datos.append(valores_semanal[valor])
		else:
			self.liststore_base_datos.clear()
			valores_semanal=[]
			for valor in Recursos.base_de_datos.keys():
				if Recursos.base_de_datos[valor][7]==str(self.weeknum):	
					valores_semanal.append(Recursos.base_de_datos[valor])
			for valor in range(len(valores_semanal)-1,-1,-1):
				self.liststore_base_datos.append(valores_semanal[valor])
		self.current_filter_language = widget.get_text()
		self.language_filter.refilter()
	def cancelar_analisis(self,widget):
		self.serie_analizando.set_text('')
		self.entrada_escaner.set_text('')
		self.analizando=False
		self.entrada_escaner.set_editable(True)
	def conectar_puerto(self,port=None):
		if port==None:
			list = serial.tools.list_ports.comports()
			self.serial_ports = []
			for element in list:
				self.serial_ports.append(element.device)
			for puerto in self.serial_ports:
				try:
					self.puerto=puerto
					self.puerto_conectado = serial.Serial(port=self.puerto,baudrate=9600,timeout=25)
					self.puerto_conectado.isOpen()
					self.serial_port=True
				except:
					self.serial_port=False
		else:
			try:
				self.puerto=self.serial_ports[port]
				self.puerto_conectado = serial.Serial(port=self.puerto,baudrate=9600,timeout=25)
				self.puerto_conectado.isOpen()
				self.serial_port=True
			except:
				self.serial_port=False
				self.mensaje(self.puerto+'\tFallo al conectar')
	def cambio_entradas_configuraciones(self,widget):
		self.conectar_puerto(port=self.puertos_combo.get_active())
		Recursos.nombre_empresa=self.entrada_empresa.get_text()
		Recursos.planta=self.entrada_planta.get_text()
		Recursos.linea=self.entrada_linea.get_text()
		Recursos.proceso=self.entrada_proceso.get_text()
		Recursos.pimin=self.spin_presion_min.get_text()
		Recursos.pimax=self.spin_presion_max.get_text()
		Recursos.dpmin=self.spin_delta_min.get_text()
		Recursos.dpmax=self.spin_delta_max.get_text()
		Recursos.guardar_configuraciones()
		self.hb.props.subtitle = Recursos.nombre_empresa
		self.url_estacion.set_text('	'+Recursos.planta+'  -  '+Recursos.linea+'  -  '+Recursos.proceso)
	def entrada_escaner_enter(self,widget):
		if widget.get_text()!='':
			self.serie_analizando.set_text(widget.get_text())
			self.entrada_escaner.set_editable(False)
			self.analizando=True
			time.sleep(1)
			self.guardar_analisis()
	def guardar_analisis(self):
		self.now=datetime.datetime.now()
		self.weeknum=str(datetime.date(self.now.year, self.now.month, self.now.day).isocalendar()[1])
		self.fecha=str(self.now.month)+'/'+str(self.now.day)+'/'+str(self.now.year)
		self.hora=str(self.now.hour)+':'+str(self.now.minute)+':'+str(self.now.second)

		try:
			datos_cincinati=[]
			for i in range(5):
				cadena=self.puerto_conectado.readline()
				if len(cadena)>150:
					datos_cincinati.append(str(cadena))
					break

			for dato in datos_cincinati:
				if len(dato)>150:
					#print('presion inicial',dato[161:170])
					#print('presion final',dato[95:104])
					#print('delta presion1',dato[74:82])
					#print('delta presion2',dato[140:148])
					#print('hora',datos_cincinati[2][22:30])
					#print('fecha',datos_cincinati[2][35:43])
					presion_inicial=dato[161:170]
					presion_final=dato[95:104]
					delta_presion=dato[74:82]
			presion_inicial='-8.583227'
			presion_final='-8.568699'
			delta_presion='0.020314'
			paso_actual=str(len(Recursos.base_de_datos)+1)
			if float(delta_presion)>float(self.spin_delta_min.get_text()) and float(delta_presion)<float(self.spin_delta_max.get_text()):
				estado='PASO'
			else:
				estado='FALLO'
			datos=[self.entrada_escaner.get_text(),presion_inicial,presion_final,delta_presion,estado,self.fecha,self.hora,self.weeknum]
			Recursos.base_de_datos[paso_actual]=datos
			Recursos.guardar_base_datos(paso_actual,datos)
			self.liststore_base_datos.clear()
			valores_semanal=[]
			for valor in Recursos.base_de_datos.keys():
				if Recursos.base_de_datos[valor][7]==str(self.weeknum):	
					valores_semanal.append(Recursos.base_de_datos[valor])
			for valor in range(len(valores_semanal)-1,-1,-1):
				self.liststore_base_datos.append(valores_semanal[valor])
			self.mensaje(self.entrada_escaner.get_text()+'\t -'+estado)

		except:
			self.mensaje('Falla en serial')
		self.serie_analizando.set_text('')
		self.entrada_escaner.set_text('')
		self.analizando=False
		self.entrada_escaner.set_editable(True)
	def mensaje(self,texto):
		self.mensaje_eventobox_configuraciones.set_text(texto)
		self.mensaje_eventobox_pagina.set_text(texto)


	def escuchando_puerto(self):
		while True:
			#print('lobezno')
			if self.analizando and self.serial_port:
				datos_cincinati=[]
				print('escarcha')
				cadena=self.puerto_conectado.readline()
				if len(cadena)>150:
					datos_cincinati.append(str(cadena))



	def on_switch_activated(self, switch, gparam):
		if switch.get_active():
			state = "on"
		else:
			state = "off"
		#print("Switch was turned", state)

	def ventana_ppap(self):
		self.image = Gtk.Image.new_from_file("wallet.png")
		#self.texto=Gtk.Label()
		#self.texto.set_text('PPAP')
		self.page1=Gtk.Box()
		self.page1.set_border_width(10)

		self.button_image=Gtk.Button()
		self.button_image.add(self.image)
		self.button_image.set_border_width(0)
		self.button_image.set_size_request(32,32)
		self.page1.pack_start(self.button_image, True, True, 0)
		#self.menu_principal.append_page(self.page1,self.texto)

	def on_timeout(self, user_data):
		new_value = self.liststore[self.current_iter][1] + 1
		if new_value > 100:
			self.current_iter = self.liststore.iter_next(self.current_iter)
			if self.current_iter is None:
				self.reset_model()
			new_value = self.liststore[self.current_iter][1] + 1

		self.liststore[self.current_iter][1] = new_value
		return True

	def reset_model(self):
		for row in self.liststore:
			row[1] = 0
		self.current_iter = self.liststore.get_iter_first()

	def on_button_clicked(self, widget):
		print(widget.get_label())

	

if __name__ == '__main__':
	win = MyWindow()
	win.connect("destroy", Gtk.main_quit)
	win.show_all()
	Gtk.main()