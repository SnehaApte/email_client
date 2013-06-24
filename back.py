import email
import imaplib
import datetime
import pickle


class backend:

	def __init__(self):
		self.up = {} #dictionary to store uname passwd
		self.date = (datetime.date.today() - datetime.timedelta(1)).strftime("%d-%b-%Y")
		self.l = [] #read server, username and pass from file into this list
		self.box = "INBOX" #default is inbox
		try:
			self.up = pickle.load(open("upass.txt", 'rb'))

			for i in self.up:
				t = (self.up[i][1], i, self.up[i][0]) #server, uname, pass in that order
				self.l.append(t)
	
	
			#connect to servers
			#list of servers init and login
			self.s = []
			for i in self.l:#i is a tuple (server, username, password)
			#create server and login
				server = imaplib.IMAP4_SSL(i[0])
				self.s.append((i[0], server))
				server.login(i[1].strip(), i[2].strip())

			#order of pages will be same as order of servers in this list
			#except, first page will be for priority

		except IOError: #this will happen when using app for first time, since uname, passwd file will not exist
			pass
	
	def get_page_list(self):
		#return names for labels of pages
		l = []
		for i in self.l:
			l.append(i[1])

		return l


	def select_folder(self, server_num = 0, box = "INBOX"): #server num is number of server ie page num. this will be used to offset into the self.s list
		
		boxlist = []
		
		#this will be called when a button for say 'inbox' is clicked
		#select server
		server = self.s[server_num -1][1]
		self.box = box
		#select box
		server.select(box)
		
		#serach for mails recd yesterday
		try:
			result, data = server.uid('search', None, '(SENTSINCE {date})'.format(date=self.date))
			ll = data[0].split()
		except IndexError:
			pass

		#fetch last day's mails
		if ll:
			
			#if have yest mails then show their subject and sender name
			for num in ll:
				#to get subject and sender name
				typ, data_header = server.uid('fetch', num, '(BODY.PEEK[HEADER.FIELDS (From Subject)] RFC822.SIZE)')
				boxlist.append((num, data_header[0][1]))
			

		else:
			#if no mails recd yesterday, then fetch last 10 messages from the box
			try:	
				result, data1 = server.uid('search', None, 'ALL')
				last_id = int(data1[0].split()[-1])
				#find last recd mail number
				if (last_id > 10):
					endr = last_id - 10
				else:
					endr = 0


				for num in range(last_id, endr, -1):
					typ, data_header = server.uid('fetch', num, '(BODY.PEEK[HEADER.FIELDS (From Subject)] RFC822.SIZE)')
					boxlist.append((num, data_header[0][1]))

			except IndexError:
				pass
		#return the list of mails to be displayed
		return boxlist 
	
	def show_mail(self, n, server_num = 0):
		
		#to show contents of selected mail

		#n is the number of the mail which will be used as part of string displayed on the button
		#courtesy: stackoverflow
		server = self.s[server_num-1][1]
		typ3, data3 = server.uid('fetch', n, '(RFC822)')
		msg = data3[0][1] #get entire mail into string


		main = email.message_from_string(msg) #main is an email message so multipart and walk work on it.

		#Finds the plain text version of the body of the message.

		if main.get_content_maintype() == 'multipart': #If message is multi part we only want the text version of the body, this walks the message and gets the body.

		    for part in main.walk():       
			if part.get_content_type() == "text/plain":
			    body = part.get_payload(decode=True)
			    mb = str(body)
			    return mb
			else:
			    continue

	def logout_all(self):
		#logout of all servers
		try:
			for server in self.s:
				server[1].logout()
		except AttributeError:
			pass


	def add_id(self, sname, uname, passwd):
		#add email id to upass.txt
		
		try:
			self.up = pickle.load(open("upass.txt", 'rb'))
		except IOError:
			pass

		self.up[str(uname).strip()] = (str(passwd).strip(), str(sname).strip())
		
		pickle.dump(self.up, open("upass.txt", 'wb'))


	def add_prio_id(self, emid):
		
		#add priority email id
		f = open("prio.txt", 'a')
		f.write((str(emid).strip() + '\n'))
		f.close()


	def get_prio_email(self):
		#get priority emails (ie emails recd from names listed in prio.txt)

		boxlist = []
		rev_list = []

		self.box = "INBOX"

		#get list of prio sender ids

		try:
			f = open("prio.txt", 'r')
			psend = f.readlines()
			f.close()
		except IOError: #file prio.txt does not exist - ie no priority email ids have been added
			psend = []
			pass

		psend = [ll.strip() for ll in psend]
#		

		#fetch emails recd from priority ids

		try:
			for s, d in [(s, d) for s in self.s for d in psend]:
				server = s[1]
				server.select(self.box)
				typ, data = server.uid('search', None, 'FROM', d )
				for num in data[0].split():
					typ, data2 = server.uid('fetch', num, '(BODY.PEEK[HEADER.FIELDS (From Subject)] RFC822.SIZE)')
					boxlist.append((num, data2[0][1]))

			#return last 10
			l = len(boxlist)
			if l > 10:
				for i in range(l-1, l-1-10, -1):
					rev_list.append(boxlist[i])
			else:

				for i in range (l-1, -1, -1):
					rev_list.append(boxlist[i])

			return rev_list


		except AttributeError: #servers not instantiated, ie when app launched for first time, no email ids saved, so no servers specified OR no priority email ids specified
			pass

if __name__ == "__main__":

	
	b = backend()
