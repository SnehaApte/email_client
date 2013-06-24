import pygtk
pygtk.require('2.0')
import gtk
from back import backend


class ui:

	def __init__(self):

		#create window and pack hboxes and vboxes into it to create basic layout of the gui
		
		self.w = gtk.Window()
		self.w.set_size_request(800, 600)
		self.w.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("lavender"))
		self.hbox = gtk.HBox()
		self.vbox1 = gtk.VBox()
		self.vbox1.set_size_request(200, 600)
		self.vbox2 = gtk.VBox()
		self.vbox2.set_size_request(600, 600)
		self.w.add(self.hbox)
		
		#create event box for vbox1 so that can change bg
		self.eb1 = gtk.EventBox()
		self.eb1.add(self.vbox1)
		self.eb1.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("pink"))
	
		self.hbox.pack_start(self.eb1, True, False, 0)
		self.hbox.pack_start(self.vbox2, True, False, 25)


		#list of vboxes
		self.lf = []
		#list of labels for pages
		self.ll = []
		#backup list maintained - to be used when back button is pressed
		self.last_list = []


		#text view to display body of email
		self.t = gtk.TextView()
		self.t.set_editable(False)
		self.t.set_cursor_visible(False)
		self.t.set_wrap_mode(gtk.WRAP_WORD)
	
		#create object of backend
		self.backend = backend()

		#create page_list - list of all email ids (NOT priority email ids)
		self.page_list = self.backend.get_page_list()
		#insert entry for priority emails - so this will be he 0th page
		self.page_list.insert(0, "Priority Emails")

	def cr_buttons(self):
		#create buttons on left
		self.b1 = gtk.Button("Add email id")
		self.b2 = gtk.Button("Add priority sender")
		self.vbox1.pack_start(self.b1, True, False, 10)
		self.vbox1.pack_start(self.b2, True, False, 10)


	def fill_rvbox(self):
		
		#right vbox will have 2 parts again, left will have pages, right will have inbox, sent mail buttons
		#when one of those buttons is clicked, it is important to first find which page is currently active

		self.inhbox = gtk.HBox()
		self.inv1 = gtk.VBox()#pages
		self.inv1.set_size_request(500, 600)
		self.inv2 = gtk.VBox()#buttons
		self.inv2.set_size_request(100, 600)

		self.vbox2.pack_start(self.inhbox, True, False, 10)

		self.inhbox.pack_start(self.inv1, True, False, 25)

		#to change color - put inv2 in an event box and change color and put evbox in hbox

		self.ineb = gtk.EventBox()
		self.ineb.add(self.inv2)
		self.ineb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("blue"))

		self.inhbox.pack_start(self.ineb, True, False, 25)



		#buttons on the right

		self.inb1 = gtk.Button("Inbox")
		self.inb2 = gtk.Button("Sent Mail")
		self.inb3 = gtk.Button("Back")
		self.inv2.pack_start(self.inb1, True, False, 10)#pack buttons in the right invbox
		self.inv2.pack_start(self.inb2, True, False, 10)
		self.inv2.pack_start(self.inb3, True, False, 10)

	def cr_nb(self):

		#create notebook of pages - one page for each id, 0th page for priority emails

		self.nb = gtk.Notebook()
		self.nb.set_size_request(500, 600)
		for i in self.page_list:
			#lf is list of vboxes
			#place a VBox in each page, inside VBox we will place buttons of individual emails
			self.lf.append(gtk.VBox())

			label = gtk.Label(i)
			self.ll.append(label)
			self.nb.append_page(self.lf[self.page_list.index(i)], label)

		self.inv1.pack_start(self.nb, True, False, 0)


	def link_all(self):
		#link various buttons to functions to be called when clicked
		
		self.w.connect("destroy", self.logout_end)
		self.inb1.connect("clicked", self.inbox_handler)
		self.inb2.connect("clicked", self.sentmail_handler)
		self.inb3.connect("clicked", self.back_handler)
		
		
		self.b1.connect("clicked", self.add_id)
		self.b2.connect("clicked", self.addprio)


	def add_id(self, widget):
		
		#function invoked when button "Add Email ID" is clicked


		#create and show dialog box, which will take input about uname, password, server
		self.t1 = gtk.Entry()
		self.t1.set_editable(True)
		self.t1.set_text("server: ")
		

		self.t2 = gtk.Entry()
		self.t2.set_editable(True)
		self.t2.set_text("email id: ")

		self.t3 = gtk.Entry()
		self.t3.set_editable(True)
		self.t3.set_text("password: ")

		okb = gtk.Button("OK")
		okb.connect("clicked", self.b_add_id)


		#pack the textviews and button into dialog box and display
		self.d = gtk.Dialog(title = "Add Email id")
		self.d.action_area.pack_start(self.t1, True, True, 5)
		self.d.action_area.pack_start(self.t2, True, True, 5)
		self.d.action_area.pack_start(self.t3, True, True, 5)

		self.d.action_area.pack_start(okb, True, True, 5)

		
		self.d.show_all()
		

	def b_add_id(self, widget):
		
		#invoked when OK button of dialog box pressed - dialog box for adding email id (NOT priority email id)

		#get server name, username, password
		s = self.t1.get_text()
		u = self.t2.get_text()
		p = self.t3.get_text()
		
		#add these details to file upass.txt by invoking function in backend
		self.backend.add_id(s, u, p)

		#close dialog box
		self.d.destroy()


		#create page for newly added id and display
		self.lf.append(gtk.VBox())

		label = gtk.Label(u)
		self.ll.append(label)
		self.nb.append_page(self.lf[-1], label)

		#re-instantiate backend to show new page
		self.backend = backend()
		self.w.show_all()


	def addprio(self, widget):
		
		#function invoked when button "Add Priority Sender Email ID" pressed


		#create dialog box and display
		self.ta1 = gtk.Entry()
		self.ta1.set_editable(True)
		self.ta1.set_text("Priority Email ID: ")
		
		okb = gtk.Button("OK")
		okb.connect("clicked", self.b_add_prio)

		self.dprio = gtk.Dialog(title = "Add Priority Email id")
		self.dprio.action_area.pack_start(self.ta1, True, True, 5)

		self.dprio.action_area.pack_start(okb, True, True, 5)

		self.dprio.show_all()

	def b_add_prio(self, widget):
		#function invoked when button OK pressed in dialog box for 'ADD Priority Email ID'

		s = self.ta1.get_text()
		self.backend.add_prio_id(s)
		self.dprio.destroy()
		self.get_prio_mail()



	def get_prio_mail(self):

		#get priority email ids to be placed in pg 0
		pgno = 0
		self.nb.set_current_page(0)
		disp_list = self.backend.get_prio_email()

		#find appropriate vbox - we have a vbox in each page. find vbox for the current page
		cnt_vbox = self.lf[pgno]
		
		#remove whatever was present in the vbox
		cnt_vbox.foreach(lambda w: cnt_vbox.remove(w))

		#delete ebtries in back-up list
		del self.last_list[:]		


		try:
			for i in disp_list:
				b = gtk.Button(str(i))
				b.connect("clicked", self.embutton_handler, pgno, i[0])
				cnt_vbox.pack_start(b, False, False, 0)
				self.last_list.append(b)
			cnt_vbox.show_all()

		except TypeError: #if no disp_list ie priority ids not set
			pass


	def inbox_handler(self, widget):

		#function invoked when inbox button is clicked
		#this will refresh every time button is clicked

		pgno = self.nb.get_current_page()
		if pgno > 0: #ie email ids have been set and this is the page of a particular email id
			#select folder and get list of mails
			disp_list = self.backend.select_folder(pgno, "INBOX")
			#select current page's vbox
			cnt_vbox = self.lf[pgno]
			try:	
				#clear current vbox
				cnt_vbox.foreach(lambda w: cnt_vbox.remove(w))

				#clear backup list
				del self.last_list[:]		
				
				

				for i in disp_list:
					b = gtk.Button(str(i))
					b.connect("clicked", self.embutton_handler, pgno, i[0])
					cnt_vbox.pack_start(b, False, False, 0)
					self.last_list.append(b)
				cnt_vbox.show_all()

			except IndexError:
				pass


		else:
			#this is the page for priority emails
			#display dialog box saying: "please choose email id. you are currently in priority folder"
			message = gtk.MessageDialog(flags = gtk.DIALOG_MODAL)
			message.set_markup("Please choose an email id. You are currently viewing Priority Emails.")
			message.show()



	def sentmail_handler(self, widget):
		#follows same pattern as inbox handler
		#this will refresh every time button is clicked
		pgno = self.nb.get_current_page()

		if pgno > 0:
			disp_list = self.backend.select_folder(pgno, "[Gmail]/Sent Mail")
			cnt_vbox = self.lf[pgno]

			try:
				cnt_vbox.foreach(lambda w: cnt_vbox.remove(w))
				del self.last_list[:]		
				for i in disp_list:
					b = gtk.Button(str(i))
					b.connect("clicked", self.embutton_handler, pgno, i[0])
					cnt_vbox.pack_start(b, False, False, 0)
					self.last_list.append(b)
				cnt_vbox.show_all()
			except IndexError:
				pass

		else:
			#display dialog box saying: "please choose email id. you are currently in priority folder"
			message = gtk.MessageDialog(flags = gtk.DIALOG_MODAL)
			message.set_markup("Please choose an email id. You are currently viewing Priority Emails.")
			message.show()




	def embutton_handler(self, widget, pgno, email_num):
		#function invoked when button for a particular email is pressed


		#get body of particular email
		txt = self.backend.show_mail(email_num, pgno)

		#if blank, do nothing
		if txt == None:
			return


		#self.t is the text view to display the body of the email
		buf = self.t.get_buffer()

		#error checking unicode
		t = []
		l = list(txt)
		for each in l:
			try:
				t.append(unicode(each))
			except UnicodeDecodeError:
				pass

		txt = "".join(t)
		buf.set_text(str(unicode(txt)))

		self.t.set_buffer(buf)


		#clear current vbox and add the textview
		cnt_vbox = self.lf[pgno]
		cnt_vbox.foreach(lambda w: cnt_vbox.remove(w))

		
		cnt_vbox.pack_start(self.t, False, False, 0)

		cnt_vbox.show_all()

	def back_handler(self, widget):

		#function invoked when back button is pressed
		#the app maintains a list of last visited box, and displays that list

		pgno = self.nb.get_current_page()
		cnt_vbox = self.lf[pgno]

		cnt_vbox.foreach(lambda w: cnt_vbox.remove(w))
		

		for i in self.last_list:
			cnt_vbox.pack_start(i, False, False, 0)

		cnt_vbox.show_all()




	def logout_end(self, widget):
		#function invoked when close button of app pressed
		#logout of all ids and close window et al.
		self.backend.logout_all()
		gtk.main_quit()



	def fmain(self):
		self.cr_buttons()
		self.fill_rvbox()
		self.cr_nb()
		self.link_all()
		self.get_prio_mail()
		self.w.show_all()
		gtk.main()

	
if __name__ == "__main__":
	
	f = ui()
	f.fmain()

