import gi
from configparser  import ConfigParser
from Recursos import data as Recursos
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, GLib, Gdk, Gio

hb = Gtk.HeaderBar()
hb.set_show_close_button(True)
hb.props.title = Recursos.nombre_empresa
caja_headerbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

class MyWindow(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self)
		self.set_default_size(800, 500)
		self.set_titlebar(hb)
		self.ventana_actual,self.linea_actual,self.proceso_actual=[],[],[]

		self.menu_principal=Gtk.Notebook()
		#self.menu_principal.set_tab_pos(Gtk.PositionType.LEFT)
		self.menu_principal.set_show_tabs(False)
		self.add(self.menu_principal)

		self.liststore_lineas=Gtk.ListStore(str)
		self.liststore_procesos=Gtk.ListStore(str)

		button = Gtk.Button()
		icon = Gio.ThemedIcon(name="applications-system-symbolic")
		image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
		button.add(image)
		button.connect('clicked',self.ir_ventana_configuracion)

		button2 = Gtk.Button()
		icon = Gio.ThemedIcon(name="preferences-system-details-symbolic")
		image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
		button2.add(image)

		ventanas_combo = Gtk.ComboBoxText()
		ventanas_combo.set_entry_text_column(0)
		ventanas_combo.connect("changed", self.cambio_ventanas_combo)
		for ventana,valor in Recursos.menu_lineas_por_plantas.items():
			ventanas_combo.append_text(ventana)
		
		self.lineas_combo = Gtk.ComboBox.new_with_model(self.liststore_lineas)
		self.lineas_combo.connect("changed", self.cambio_lineas_combo)
		renderer_text = Gtk.CellRendererText()
		self.lineas_combo.pack_start(renderer_text, True)
		self.lineas_combo.add_attribute(renderer_text, "text", 0)
		
		self.procesos_combo = Gtk.ComboBox.new_with_model(self.liststore_procesos)
		self.procesos_combo.connect("changed", self.cambio_procesos_combo)
		renderer_text2 = Gtk.CellRendererText()
		self.procesos_combo.pack_start(renderer_text2, True)
		self.procesos_combo.add_attribute(renderer_text2, "text", 0)
		
		ventanas_combo.set_active(0)
		self.lineas_combo.set_active(0)
		self.procesos_combo.set_active(0)
		
		caja_headerbar.add(button)
		caja_headerbar.add(ventanas_combo)
		caja_headerbar.add(self.lineas_combo)
		caja_headerbar.add(self.procesos_combo)
	
		hb.pack_start(caja_headerbar)
		hb.pack_end(button2)

		pagina = Paginas_normal(self.menu_principal,'Planta 1')
		self.menu_principal.append_page(pagina)
		self.box_configuraciones=Gtk.Box(spacing=16)
		#self.box_configuraciones.set_column_homogeneous(True)
		self.ventana_configuracion()
		self.menu_principal.append_page(self.box_configuraciones)

	def ventana_configuracion(self):
		#grid_configuraciones=Gtk.Grid()


		grid_plantas=Gtk.Grid()
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
		#self.box_configuraciones.attach_next_to(grid_proceso, grid_lineas, Gtk.PositionType.RIGHT, 1, 1)

		#grid_configuraciones.attach_next_to(grid_proceso,grid_lineas, Gtk.PositionType.RIGHT, 1, 1)
		self.box_configuraciones.pack_end(grid_proceso, True, False, 0)

		#grid___=Gtk.Grid()

		#grid_configuraciones.attach_next_to(grid___,grid_configuraciones, Gtk.PositionType.BOTTOM, 1, 1)

		#self.box_configuraciones.pack_start(grid_configuraciones, True, False, 0)

		
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



	def ventana_pfmea(self):
		#self.page2=Gtk.Box()
		#self.page2.set_border_width(10)

		#456 000 000 000 * 20

		#self.grid = Gtk.Grid()
		#self.page2.add(self.grid)
		#self.grid.set_column_homogeneous(True)
		#self.grid.set_row_homogeneous(True)


		self.entry_filtro = Gtk.Entry()

		button_filtro = Gtk.Button.new_with_label('Filtro')
		#button_filtro
		button_borrar_filtro = Gtk.Button.new_with_label('Borrar')
		button_filtro.connect("clicked", self.filtro_boton)
		button_borrar_filtro.connect("clicked", self.filtro_boton_borrar)
		#button_filtro.set_text()

		#Creating the ListStore model
		self.software_liststore = Gtk.ListStore(str, int, str)
		for software_ref in software_list:	self.software_liststore.append(list(software_ref))
		self.current_filter_language = None

		#Creating the filter, feeding it with the liststore model
		self.language_filter = self.software_liststore.filter_new()
		#setting the filter function, note that we're not using the
		self.language_filter.set_visible_func(self.language_filter_func)
		#creating the treeview, making it use the filter as a model, and adding the columns
		self.treeview = Gtk.TreeView.new_with_model(self.language_filter)

		for i, column_title in enumerate(["Software", "Release Year", "Programming Language"]):
			#print(i, column_title)
			button = Gtk.Button.new_with_label(column_title)
			renderer = Gtk.CellRendererText()
			column = Gtk.TreeViewColumn(column_title, renderer, text=i)
			self.treeview.append_column(column)

		#creating buttons to filter by programming language, and setting up their events
		#self.buttons = list()
		#for prog_language in ["Java", "C", "C++", "Python", "None"]:
		#	button = Gtk.Button(prog_language)
		#	self.buttons.append(button)
		#	button.connect("clicked", self.on_selection_button_clicked)

		


		#vbox.pack_start(self.entry, True, True, 0)
		#setting up the layout, putting the treeview in a scrollwindow, and the buttons in a row
		self.scrollable_treelist = Gtk.ScrolledWindow()
		self.scrollable_treelist.set_vexpand(True)


		#self.grid.attach(self.scrollable_treelist, 0, 0, 8, 10)

		self.grid.attach(button_borrar_filtro, 0, 0, 1, 1)
		#self.grid.attach_next_to(self.entry, self.scrollable_treelist, Gtk.PositionType.BOTTOM, 1, 1)
		self.grid.attach_next_to(self.entry_filtro, button_borrar_filtro, Gtk.PositionType.RIGHT, 8, 1)
		self.grid.attach_next_to(button_filtro, self.entry_filtro, Gtk.PositionType.RIGHT, 1, 1)
		#self.grid.attach_next_to(self.buttons[0], self.entry, Gtk.PositionType.RIGHT, 1, 1)
		self.grid.attach_next_to(self.scrollable_treelist, self.entry_filtro, Gtk.PositionType.BOTTOM, 8, 10)
		
		#self.grid.attach_next_to(self.buttons[0], self.scrollable_treelist, Gtk.PositionType.BOTTOM, 1, 1)
		#for i, button in enumerate(self.buttons[1:]):
		#	self.grid.attach_next_to(button, self.buttons[i], Gtk.PositionType.RIGHT, 1, 1)

		self.scrollable_treelist.add(self.treeview)


		#self.texto=Gtk.Label()
		#self.texto.set_text('PFMEA')
		#self.menu_principal.append_page(self.page2,self.texto)



		

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

	def language_filter_func(self, model, iter, data):
		columna=0
		if self.current_filter_language is None or self.current_filter_language == "None":
			return True
		else:
			try:
				self.current_filter_language=int(self.current_filter_language)
			except:
				pass
			for i in range(3):
				if model[iter][i] == self.current_filter_language:
					columna=i
			return model[iter][columna] == self.current_filter_language

class Paginas_normal(Gtk.Box):
	def __init__(self, parent,planta_fin):
		super().__init__(spacing=10)
		self.__parent = parent
		grid_principal=Gtk.Grid()
		self.pack_start(grid_principal, True, True, 0)
		grid_principal.set_row_homogeneous(True)
if __name__ == '__main__':
	win = MyWindow()
	win.connect("destroy", Gtk.main_quit)
	win.show_all()
	Gtk.main()

