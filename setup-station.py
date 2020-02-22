import gi,datetime,cairo,math
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

		screen = Gdk.Screen.get_default()
		provider = Gtk.CssProvider()
		style_context = Gtk.StyleContext()
		style_context.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		css = b"""
		.entry {
		    background: orange;
		}
		"""
		provider.load_from_data(css)

		self.menu_principal=Gtk.Notebook()
		self.menu_principal.set_show_tabs(False)
		self.add(self.menu_principal)

		self.now=datetime.datetime.now()
		self.weeknum=datetime.date(self.now.year, self.now.month, self.now.day).isocalendar()[1]
		self.fecha=str(self.now.day)+'/'+str(self.now.month)+'/'+str(self.now.year)
		self.hora=str(self.now.hour)+':'+str(self.now.minute)+':'+str(self.now.second)

		
		self.box_paginas=Gtk.Box(spacing=5)
		self.ventana_pagina()
		self.menu_principal.append_page(self.box_paginas)
		self.box_configuraciones=Gtk.Box(spacing=16)
		self.box_configuraciones.set_hexpand(True)
		self.ventana_configuracion()
		self.menu_principal.append_page(self.box_configuraciones)

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

		#eventobox=Gtk.EventBox()
		#eventobox.override_background_color(0,color_verde)
		#eventobox.add(self.poner_etiqueta('LISTO'))


		grid_1=Gtk.Grid()
		grid_1.set_column_spacing(15)
		grid_1.set_row_spacing(15)

		label=self.poner_etiqueta('Numero de serie')
		self.entrada_escaner = Gtk.Entry()
		self.entrada_escaner.connect('activate',self.entrada_escaner_enter)
		self.entrada_escaner.set_valign(Gtk.Align.CENTER)
		grid_1.attach(label, 0, 0, 1, 1)
		grid_1.attach_next_to(self.entrada_escaner, label, Gtk.PositionType.RIGHT, 1, 1)
		grid_2=Gtk.Grid()
		grid_2.set_column_spacing(15)
		grid_2.set_row_spacing(15)
		label2=self.poner_etiqueta('FlexFlow')
		self.ff_switch = Gtk.Switch()
		self.ff_switch.connect("notify::active", self.on_switch_activated)
		self.ff_switch.set_active(True)
		grid_2.attach(label2, 0, 0, 1, 1)
		grid_2.attach_next_to(self.ff_switch, label2, Gtk.PositionType.RIGHT, 1, 1)

		box_encabezado.pack_start(grid_1, True, True, 0)
		box_encabezado.pack_end(grid_2, False, True, 0)
		box_encabezado.set_hexpand(True)
		
		self.liststore_base_datos = Gtk.ListStore(str,str,str,str,str,str,str,str)
		for valor in sorted(Recursos.base_de_datos.keys(),reverse=True):
			if Recursos.base_de_datos[valor][7]==str(self.weeknum):	
				self.liststore_base_datos.append(Recursos.base_de_datos[valor])

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

		grid_pagina.attach(box_encabezado, 0, 0, 1, 1)
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

		label=self.poner_etiqueta('Guardar')


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
		#self.entrada_empresa.connect('activate',self.cambio_entradas_configuraciones)
		self.entrada_empresa.set_valign(Gtk.Align.CENTER)

		label2=self.poner_etiqueta('Planta')
		self.entrada_planta = Gtk.Entry()
		self.entrada_planta.set_text(Recursos.planta)
		#self.entrada_planta.connect('activate',self.cambio_entradas_configuraciones)
		self.entrada_planta.set_valign(Gtk.Align.CENTER)

		label3=self.poner_etiqueta('Linea')
		self.entrada_linea = Gtk.Entry()
		self.entrada_linea.set_text(Recursos.linea)
		#self.entrada_linea.connect('activate',self.cambio_entradas_configuraciones)
		self.entrada_linea.set_valign(Gtk.Align.CENTER)

		label4=self.poner_etiqueta('Proceso')
		self.entrada_proceso = Gtk.Entry()
		self.entrada_proceso.set_text(Recursos.proceso)
		#self.entrada_proceso.connect('activate',self.cambio_entradas_configuraciones)
		self.entrada_proceso.set_valign(Gtk.Align.CENTER)


		ajuste_presion1 = Gtk.Adjustment(value=0.0, lower=0.0, upper=10.0, step_increment=1.0, page_increment=0.0, page_size=0.0)
		ajuste_presion2 = Gtk.Adjustment(value=8.0, lower=7.0, upper=10.0, step_increment=1.0, page_increment=0.0, page_size=0.0)
		self.spin_presion_min = Gtk.SpinButton(adjustment=ajuste_presion1, climb_rate=0.0, digits=0.0)
		self.spin_presion_max = Gtk.SpinButton(adjustment=ajuste_presion2, climb_rate=0.0, digits=0.0)

		ajuste_delta1 = Gtk.Adjustment(value=0, lower=0, upper=100, step_increment=1, page_increment=0, page_size=0)
		ajuste_delta2 = Gtk.Adjustment(value=0, lower=0, upper=100, step_increment=1, page_increment=0, page_size=0)
		self.spin_delta_min = Gtk.SpinButton(adjustment=ajuste_delta1, climb_rate=0.0, digits=0)
		self.spin_delta_max = Gtk.SpinButton(adjustment=ajuste_delta2, climb_rate=0.0, digits=0)

		label5=self.poner_etiqueta('Presion inicial min')
		self.entrada_pimin = Gtk.Entry()
		self.entrada_pimin.set_text(Recursos.pimin)
		#self.entrada_pimin.connect('activate',self.cambio_entradas_configuraciones)
		self.entrada_pimin.set_valign(Gtk.Align.CENTER)

		label6=self.poner_etiqueta('Presion inicial max')
		self.entrada_pimax = Gtk.Entry()
		self.entrada_pimax.set_text(Recursos.pimax)
		#self.entrada_pimax.connect('activate',self.cambio_entradas_configuraciones)
		self.entrada_pimax.set_valign(Gtk.Align.CENTER)

		label7=self.poner_etiqueta('Delta presion min')
		self.entrada_dpmin = Gtk.Entry()
		self.entrada_dpmin.set_text(Recursos.dpmin)
		#self.entrada_dpmin.connect('activate',self.cambio_entradas_configuraciones)
		self.entrada_dpmin.set_valign(Gtk.Align.CENTER)

		label8=self.poner_etiqueta('Delta presion max')
		self.entrada_dpmax = Gtk.Entry()
		self.entrada_dpmax.set_text(Recursos.dpmax)
		#self.entrada_dpmax.connect('activate',self.cambio_entradas_configuraciones)
		self.entrada_dpmax.set_valign(Gtk.Align.CENTER)

		grid_configuraciones.attach(label, 0, 0, 1, 1)
		grid_configuraciones.attach_next_to(self.entrada_empresa,label,Gtk.PositionType.RIGHT,1,1)

		grid_configuraciones.attach_next_to(label2,label,Gtk.PositionType.BOTTOM,1,1)
		grid_configuraciones.attach_next_to(self.entrada_planta,label2,Gtk.PositionType.RIGHT,1,1)

		grid_configuraciones.attach_next_to(label3,label2,Gtk.PositionType.BOTTOM,1,1)
		grid_configuraciones.attach_next_to(self.entrada_linea,label3,Gtk.PositionType.RIGHT,1,1)

		grid_configuraciones.attach_next_to(label4,label3,Gtk.PositionType.BOTTOM,1,1)
		grid_configuraciones.attach_next_to(self.entrada_proceso,label4,Gtk.PositionType.RIGHT,1,1)

		grid_configuraciones2.attach(label5, 0, 0, 1, 1)
		#grid_configuraciones.attach_next_to(label5,label4,Gtk.PositionType.BOTTOM,1,1)
		grid_configuraciones2.attach_next_to(self.spin_presion_min,label5,Gtk.PositionType.RIGHT,1,1)

		grid_configuraciones2.attach_next_to(label6,label5,Gtk.PositionType.BOTTOM,1,1)
		grid_configuraciones2.attach_next_to(self.spin_presion_max,label6,Gtk.PositionType.RIGHT,1,1)

		grid_configuraciones2.attach_next_to(label7,label6,Gtk.PositionType.BOTTOM,1,1)
		grid_configuraciones2.attach_next_to(self.spin_delta_min,label7,Gtk.PositionType.RIGHT,1,1)

		grid_configuraciones2.attach_next_to(label8,label7,Gtk.PositionType.BOTTOM,1,1)
		grid_configuraciones2.attach_next_to(self.spin_delta_max,label8,Gtk.PositionType.RIGHT,1,1)

		#grid_configuraciones.attach_next_to(label2,label8,Gtk.PositionType.BOTTOM,1,1)
		#grid_configuraciones.attach_next_to(self.entrada_planta,label2,Gtk.PositionType.RIGHT,1,1)

		grid_principal.attach(self.action_bar, 0, 0, 2, 1)
		grid_principal.attach_next_to(grid_configuraciones,self.action_bar,Gtk.PositionType.BOTTOM,1,1)
		grid_principal.attach_next_to(grid_configuraciones2,grid_configuraciones,Gtk.PositionType.RIGHT,1,1)

		#grid_principal.attach(self.action_bar, 0, 1, 2, 1)
		#self.box_configuraciones.pack_start(grid_configuraciones, True, False, 0)
		#self.box_configuraciones.pack_start(grid_configuraciones2, True, False, 0)

		self.box_configuraciones.pack_end(grid_principal, False, False, 0)
		#self.box_configuraciones.pack_start(self.entrada_empresa, True, False, 0)
		#self.box_configuraciones.pack_start(label2, True, False, 0)




		'''grid_plantas=Gtk.Grid()
		#grid_plantas.set_column_homogeneous(True)

		label=Gtk.Label()
		label.set_text('Plantas')
		label.set_valign(Gtk.Align.CENTER)

		self.entry_agregar_planta = Gtk.Entry()
		self.entry_agregar_planta.set_valign(Gtk.Align.CENTER)
		button_agregar_planta = Gtk.Button.new_with_label('Agregar')
		button_agregar_planta.set_valign(Gtk.Align.CENTER)
		button_agregar_planta.connect("clicked", self.agregar_planta)
		self.plantas_liststore = Gtk.ListStore(str)
		for planta,valor in Recursos.menu_lineas_por_plantas.items():
			self.plantas_liststore.append([planta])
		self.treeview = Gtk.TreeView.new_with_model(self.plantas_liststore)
		renderer = Gtk.CellRendererText()
		renderer.set_alignment(0.5,0)
		column = Gtk.TreeViewColumn('', renderer, text=0)
		self.treeview.append_column(column)
		self.tree_selection=self.treeview.get_selection()
		self.tree_selection.connect('changed',self.seleccion_planta_configuraciones)
		grid_plantas.attach(label, 0, 0, 2, 1)
		grid_plantas.attach_next_to(self.entry_agregar_planta, label, Gtk.PositionType.BOTTOM, 1, 1)
		grid_plantas.attach_next_to(button_agregar_planta,self.entry_agregar_planta, Gtk.PositionType.RIGHT, 1, 1)
		grid_plantas.attach_next_to(self.treeview,self.entry_agregar_planta, Gtk.PositionType.BOTTOM, 2, 1)
		#self.box_configuraciones.attach(grid_plantas,0,0,1,1)

		#grid_configuraciones.attach(grid_plantas, 0, 0, 1, 1)
		self.box_configuraciones.pack_start(grid_plantas, True, False, 0)

		grid_lineas=Gtk.Grid()
		#grid_lineas.set_column_homogeneous(True)
		label=Gtk.Label()
		label.set_text('Lineas')
		label.set_valign(Gtk.Align.CENTER)
		self.entry_agregar_linea = Gtk.Entry()
		self.entry_agregar_linea.set_valign(Gtk.Align.CENTER)
		button_agregar_linea = Gtk.Button.new_with_label('Agregar')
		button_agregar_linea.set_valign(Gtk.Align.CENTER)
		button_agregar_linea.connect("clicked", self.agregar_linea_planta)
		self.lineas_liststore = Gtk.ListStore(str)
		self.treeview = Gtk.TreeView.new_with_model(self.lineas_liststore)
		renderer = Gtk.CellRendererText()
		renderer.set_alignment(0.5,0)
		column = Gtk.TreeViewColumn('', renderer, text=0)
		self.treeview.append_column(column)
		self.treeview.expand_all()
		self.tree_selection=self.treeview.get_selection()
		self.tree_selection.connect('changed',self.seleccion_linea_configuraciones)
		grid_lineas.attach(label, 0, 0, 2, 1)
		grid_lineas.attach_next_to(self.entry_agregar_linea, label, Gtk.PositionType.BOTTOM, 1, 1)
		grid_lineas.attach_next_to(button_agregar_linea,self.entry_agregar_linea, Gtk.PositionType.RIGHT, 1, 1)
		grid_lineas.attach_next_to(self.treeview,self.entry_agregar_linea, Gtk.PositionType.BOTTOM, 2, 1)
		#self.box_configuraciones.attach_next_to(grid_lineas, grid_plantas, Gtk.PositionType.RIGHT, 1, 1)

		#grid_configuraciones.attach_next_to(grid_lineas, grid_plantas, Gtk.PositionType.RIGHT, 1, 1)
		self.box_configuraciones.pack_start(grid_lineas, True,False, 0)

		grid_proceso=Gtk.Grid()
		#grid_proceso.set_column_homogeneous(True)
		label=Gtk.Label()
		label.set_text('Procesos')
		label.set_valign(Gtk.Align.CENTER)
		self.entry_agregar_proceso = Gtk.Entry()
		self.entry_agregar_proceso.set_valign(Gtk.Align.CENTER)
		button_agregar_proceso = Gtk.Button.new_with_label('Agregar')
		button_agregar_proceso.set_valign(Gtk.Align.CENTER)
		button_agregar_proceso.connect("clicked", self.agregar_proceso_planta)
		self.proceso_liststore = Gtk.ListStore(str)
		self.treeview = Gtk.TreeView.new_with_model(self.proceso_liststore)
		renderer = Gtk.CellRendererText()
		renderer.set_alignment(0.5,0)
		column = Gtk.TreeViewColumn('', renderer, text=0)
		self.treeview.append_column(column)
		grid_proceso.attach(label, 0, 0, 2, 1)
		grid_proceso.attach_next_to(self.entry_agregar_proceso, label, Gtk.PositionType.BOTTOM, 1, 1)
		grid_proceso.attach_next_to(button_agregar_proceso,self.entry_agregar_proceso, Gtk.PositionType.RIGHT, 1, 1)
		grid_proceso.attach_next_to(self.treeview,self.entry_agregar_proceso, Gtk.PositionType.BOTTOM, 2, 1)
		self.box_configuraciones.pack_end(grid_proceso, True, False, 0)'''

		#grid___=Gtk.Grid()

		#grid_configuraciones.attach_next_to(grid___,grid_configuraciones, Gtk.PositionType.BOTTOM, 1, 1)

		#self.box_configuraciones.pack_start(grid_configuraciones, True, False, 0)
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
		
	def agregar_planta(self, widget):
		if self.entry_agregar_planta.get_text() != "":
			self.plantas_liststore.append([self.entry_agregar_planta.get_text()])
			Recursos.plantas.append(self.entry_agregar_planta.get_text())
	def agregar_linea_planta(self, widget):
		if self.entry_agregar_linea.get_text() != "":
			self.lineas_liststore.append([self.entry_agregar_linea.get_text()])
	def agregar_proceso_planta(self, widget):
		if self.entry_agregar_proceso.get_text() != "":
			self.proceso_liststore.append([self.entry_agregar_proceso.get_text()])
	def seleccion_planta_configuraciones(self,selection):
		try:
			(self.modelo_arbol,self.numero_iter)=selection.get_selected()
			self.planta_seleccionada_configuraciones=self.modelo_arbol[self.numero_iter][0]
			self.lineas_liststore.clear()
			if self.ventana_actual!=(len(self.menu_principal)-1):
				for linea,valor in Recursos.menu_lineas_por_plantas[self.planta_seleccionada_configuraciones].items():
					self.lineas_liststore.append([linea])
		except:
			pass
	def seleccion_linea_configuraciones(self,selection):
		try:
			(self.modelo_arbol,self.numero_iter)=selection.get_selected()
			self.linea_seleccionada_configuraciones=self.modelo_arbol[self.numero_iter][0]
			self.proceso_liststore.clear()
			if self.ventana_actual!=2:
				for proceso,valor in Recursos.menu_lineas_por_plantas[self.planta_seleccionada_configuraciones][self.linea_seleccionada_configuraciones].items():
					self.proceso_liststore.append([proceso])
		except:
			pass
	def cambio_ventanas_combo(self, combo):
		self.ventana_actual = combo.get_active_iter()
		self.liststore_lineas.clear()
		if self.ventana_actual is not None:
			model = combo.get_model()
			self.ventana_actual = model[self.ventana_actual][0]
			for linea,valor in Recursos.menu_lineas_por_plantas[self.ventana_actual].items():
				self.liststore_lineas.append([linea])
		self.lineas_combo.set_active(0)
	def cambio_lineas_combo(self, combo):
		self.linea_actual = combo.get_active_iter()
		self.liststore_procesos.clear()
		if self.linea_actual is not None:
			model = combo.get_model()
			self.linea_actual = model[self.linea_actual][0]
		try:
			for proceso,valor in Recursos.menu_lineas_por_plantas[self.ventana_actual][self.linea_actual].items():
				self.liststore_procesos.append([proceso])
		except:
			pass
		self.procesos_combo.set_active(0)
	def cambio_procesos_combo(self, combo):
		self.proceso_actual = combo.get_active_iter()
		if self.proceso_actual is not None:
			model = combo.get_model()
			self.proceso_actual = model[self.proceso_actual][0]
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
			for valor in sorted(Recursos.base_de_datos.keys(),reverse=True):
				self.liststore_base_datos.append(Recursos.base_de_datos[valor])
		else:
			self.liststore_base_datos.clear()
			for valor in sorted(Recursos.base_de_datos.keys(),reverse=True):
				if Recursos.base_de_datos[valor][7]==str(self.weeknum):	
					self.liststore_base_datos.append(Recursos.base_de_datos[valor])
		self.current_filter_language = widget.get_text()
		self.language_filter.refilter()




	def cambio_entradas_configuraciones(self,widget):
		Recursos.nombre_empresa=self.entrada_empresa.get_text()
		Recursos.planta=self.entrada_planta.get_text()
		Recursos.linea=self.entrada_linea.get_text()
		Recursos.proceso=self.entrada_proceso.get_text()
		Recursos.pimin=self.entrada_pimin.get_text()
		Recursos.pimax=self.entrada_pimax.get_text()
		Recursos.dpmin=self.entrada_dpmin.get_text()
		Recursos.dpmax=self.entrada_dpmax.get_text()
		Recursos.guardar_configuraciones()
		self.hb.props.subtitle = Recursos.nombre_empresa
		self.url_estacion.set_text('	'+Recursos.planta+'  -  '+Recursos.linea+'  -  '+Recursos.proceso)
	def entrada_escaner_enter(self,widget):
		print(widget.get_text())
		print('FlexFlow', self.ff_switch.get_state())

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