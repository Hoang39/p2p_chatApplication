import socket
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import pickle
from datetime import datetime
import os
import threading
import struct


try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

extensionImgSupport = ['ppm', 'png', 'jpg', 'jpeg', 'gif', 'tiff', 'bmp'];

class FirstScreen(tk.Tk):
    def __init__(self):
        super().__init__()

        screen_width, screen_height = self.winfo_screenwidth(), self.winfo_screenheight()

        self.x_sub = int((screen_width / 2) - (550 / 2))
        self.y_sub = int((screen_height / 2) - (400 / 2)) - 80
        self.geometry(f"550x400+{self.x_sub}+{self.y_sub}")
        self.title("Welcome to Chat Room")
        self.resizable(0, 0)

        self.user = None
        self.passOfUser = None
        self.image_extension = None
        self.image_path = None

        self.first_frame = tk.Frame(self, background="#8D72E1")
        self.first_frame.pack(fill="both", expand=True)

        app_logo = Image.open('images/chat_ca.png')
        app_logo = ImageTk.PhotoImage(app_logo)

        self.iconphoto(False, app_logo)

        background = Image.open("images/login_bg_ca.jpg")
        background = background.resize((550, 400), Image.Resampling.LANCZOS)
        background = ImageTk.PhotoImage(background)

        upload_image = Image.open('images/upload_ca.png')
        upload_image = upload_image.resize((38, 25), Image.Resampling.LANCZOS)
        upload_image = ImageTk.PhotoImage(upload_image)

        self.user_image = 'images/user.png'

        tk.Label(self.first_frame, image=background).place(x=0, y=0)

        head = tk.Label(self.first_frame, text="Chat Room", font="lucida 17 bold", bg="#6D9886")
        head.place(relwidth=1, y=24)

        self.profile_label = tk.Label(self.first_frame, bg="#ccc")
        self.profile_label.place(x=345, y=75, width=155, height=140)

        upload_button = tk.Button(self.first_frame, image=upload_image, compound="left", text="Upload Image",
                                  cursor="hand2", font="lucida 12 bold", padx=2, command=self.add_photo)
        upload_button.place(x=345, y=220)

        self.username = tk.Label(self.first_frame, text="Username: ", font="lucida 12 bold", bg="#6D9886")
        self.username.place(x=80, y=150)

        self.username_entry = tk.Entry(self.first_frame,  font="lucida 12 bold", width=10,
                                       highlightcolor="blue", highlightthickness=1)
        self.username_entry.place(x=195, y=150)

        self.username_entry.focus_set()

        self.password = tk.Label(self.first_frame, text="Password: ", font="lucida 12 bold", bg="#6D9886")
        self.password.place(x=80, y=180)

        self.password_entry = tk.Entry(self.first_frame,  font="lucida 12 bold", width=10,
                                       highlightcolor="blue", highlightthickness=1)
        self.password_entry.place(x=195, y=180)

        login_button = tk.Button(self.first_frame, text="Login", font="lucida 12 bold", padx=30, cursor="hand2",
                                  command=self.process_data_login, bg="#16cade", relief="solid", bd=2)
        login_button.place(x=280, y=275)

        signup_button = tk.Button(self.first_frame, text="Signup", font="lucida 12 bold", padx=30, cursor="hand2",
                                  command=self.process_data_signup, bg="#16cade", relief="solid", bd=2)
        signup_button.place(x=150, y=275)

        self.mainloop()

    def add_photo(self):
        self.image_path = filedialog.askopenfilename()
        image_name = os.path.basename(self.image_path)
        self.image_extension = image_name[image_name.rfind('.')+1:]

        if self.image_path:
            user_image = Image.open(self.image_path)
            user_image = user_image.resize((150, 140), Image.Resampling.LANCZOS)
            user_image.save('resized'+image_name)
            user_image.close()

            self.image_path = 'resized'+image_name
            user_image = Image.open(self.image_path)

            user_image = ImageTk.PhotoImage(user_image)
            self.profile_label.image = user_image
            self.profile_label.config(image=user_image)


    def process_data_login(self):
        if self.username_entry.get() and self.password_entry.get():
            self.profile_label.config(image="")

            if len((self.username_entry.get()).strip()) > 6:
                self.user = self.username_entry.get()[:6]+"."
            else:
                self.user = self.username_entry.get()

            self.passOfUser = self.password_entry.get()

            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            try:
                client_socket.connect(("localhost", 5000))
                status = client_socket.recv(1024).decode()
                if status == 'not_allowed':
                    client_socket.close()
                    messagebox.showinfo(title="Can't connect!", message='Sorry, server is completely occupied.'
                                                                         'Try again later')
                    return
                
                client_socket.send(self.user.encode('utf-8'))

                client_socket.send(self.passOfUser.encode('utf-8'))
                status = client_socket.recv(1024).decode()
                client_socket.send('loginStep'.encode())

                if status == 'wrong_name':
                    client_socket.close()
                    messagebox.showinfo(title="Error!", message='Wrong username\n' 
                                                                'Try again later')
                    return

                elif status == 'wrong_pass':
                    client_socket.close()
                    messagebox.showinfo(title="Error!", message='Wrong password\n' 
                                                                'Try again later')
                    return

            except ConnectionRefusedError:
                messagebox.showinfo(title="Can't connect!", message="Server is offline , try again later.")
                print("Server is offline , try again later.")
                return
            
            if not self.image_path:
                self.image_path = self.user_image
            with open(self.image_path, 'rb') as image_data:
                image_bytes = image_data.read()

            image_len = len(image_bytes)
            image_len_bytes = struct.pack('i', image_len)
            client_socket.send(image_len_bytes)

            if client_socket.recv(1024).decode() == 'received':
                client_socket.send(str(self.image_extension).strip().encode())

            client_socket.send(image_bytes)

            clients_data_size_bytes = client_socket.recv(1024*8)
            clients_data_size_int = struct.unpack('i', clients_data_size_bytes)[0]
            b = b''
            while True:
                clients_data_bytes = client_socket.recv(1024)
                b += clients_data_bytes
                if len(b) == clients_data_size_int:
                    break

            clients_connected = pickle.loads(b)

            client_socket.send('image_received'.encode())

            user_id = struct.unpack('i', client_socket.recv(1024))[0]
            print(f"{self.user} is user no. {user_id}")
            ChatScreen(self, self.first_frame, client_socket, clients_connected, user_id)

    def process_data_signup(self):
        if self.username_entry.get() and self.password_entry.get():
            self.profile_label.config(image="")

            if len((self.username_entry.get()).strip()) > 6:
                self.user = self.username_entry.get()[:6]+"."
            else:
                self.user = self.username_entry.get()

            self.passOfUser = self.password_entry.get()

            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            try:
                client_socket.connect(("localhost", 5000))
                status = client_socket.recv(1024).decode()
                if status == 'not_allowed':
                    client_socket.close()
                    messagebox.showinfo(title="Can't connect!", message='Sorry, server is completely occupied.'
                                                                         'Try again later')
                    return
                
                client_socket.send(self.user.encode('utf-8'))

                client_socket.send(self.passOfUser.encode('utf-8'))
                status = client_socket.recv(1024).decode()
                client_socket.send('signupStep'.encode())

                if status == 'true_pass' or status == 'wrong_pass':
                    client_socket.close()
                    messagebox.showinfo(title="Error!", message='Exist account\n' 
                                                                    'Try again later')
                    return

            except ConnectionRefusedError:
                messagebox.showinfo(title="Can't connect!", message="Server is offline , try again later.")
                print("Server is offline , try again later.")
                return
            
            if not self.image_path:
                self.image_path = self.user_image
            with open(self.image_path, 'rb') as image_data:
                image_bytes = image_data.read()

            image_len = len(image_bytes)
            image_len_bytes = struct.pack('i', image_len)
            client_socket.send(image_len_bytes)

            if client_socket.recv(1024).decode() == 'received':
                client_socket.send(str(self.image_extension).strip().encode())

            client_socket.send(image_bytes)

            clients_data_size_bytes = client_socket.recv(1024*8)
            clients_data_size_int = struct.unpack('i', clients_data_size_bytes)[0]
            b = b''
            while True:
                clients_data_bytes = client_socket.recv(1024)
                b += clients_data_bytes
                if len(b) == clients_data_size_int:
                    break

            clients_connected = pickle.loads(b)

            client_socket.send('image_received'.encode())

            user_id = struct.unpack('i', client_socket.recv(1024))[0]
            print(f"{self.user} is user no. {user_id}")
            ChatScreen(self, self.first_frame, client_socket, clients_connected, user_id)

class ChatScreen(tk.Canvas):
    def __init__(self, parent, first_frame, client_socket, clients_connected, user_id):
        super().__init__(parent, bg="#2b2b2b")

        self.window = 'ChatScreen'

        self.first_frame = first_frame
        self.first_frame.pack_forget()

        self.parent = parent
        self.parent.bind('<Return>', lambda e: self.sent_message_format(e))

        self.all_user_image = {}

        self.user_id = user_id

        self.clients_connected = clients_connected

        # self.parent.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(self.first_frame))
        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.client_socket = client_socket
        screen_width, screen_height = self.winfo_screenwidth(), self.winfo_screenheight()

        x_sub = int((screen_width / 2) - (680 / 2))
        y_sub = int((screen_height / 2) - (700 / 2)) - 80
        self.parent.geometry(f"680x660+{x_sub}+{y_sub}")
        self.parent.resizable(1, 1)

        user_image = Image.open(self.parent.image_path)
        user_image = user_image.resize((40, 40), Image.Resampling.LANCZOS)
        self.user_image = ImageTk.PhotoImage(user_image)

        # global background
        # background = Image.open("images/chat_bg_ca.jpg")
        # background = background.resize((1600, 1500), Image.Resampling.LANCZOS)
        # background = ImageTk.PhotoImage(background)

        global group_photo
        group_photo = Image.open('images/group_ca.png')
        group_photo = group_photo.resize((60, 60), Image.Resampling.LANCZOS)
        group_photo = ImageTk.PhotoImage(group_photo)

        self.y = 140
        self.clients_online_labels = {}

        # self.create_image(0, 0, image=background)

        self.create_text(530, 120, text="Online", font="lucida 12 bold", fill="#40C961")

        tk.Label(self, text="   ", font="lucida 15 bold", bg="#b5b3b3").place(x=4, y=29)

        tk.Label(self, text="Group Chat", font="lucida 15 bold", padx=20, fg="green",
                 bg="#b5b3b3", anchor="w", justify="left").place(x=88, y=29, relwidth=1)

        self.create_image(60, 40, image=group_photo)

        container = tk.Frame(self)
        
        container.place(x=40, y=120, width=450, height=480)
        self.canvas = tk.Canvas(container, bg="#595656")
        self.scrollable_frame = tk.Frame(self.canvas, bg="#595656")

        scrollable_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        def configure_scroll_region(e):
            self.canvas.configure(scrollregion=self.canvas.bbox('all'))

        def resize_frame(e):
            self.canvas.itemconfig(scrollable_window, width=e.width)

        self.scrollable_frame.bind("<Configure>", configure_scroll_region)

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.yview_moveto(1.0)

        scrollbar.pack(side="right", fill="y")

        self.canvas.bind("<Configure>", resize_frame)
        self.canvas.pack(fill="both", expand=True)

        # ---------------------------emoji-----------------------------------

        self.emoji_data = [('emojis/u0001f44a.png', '\U0001F44A'), ('emojis/u0001f44c.png', '\U0001F44C'), ('emojis/u0001f44d.png', '\U0001F44D'),
                      ('emojis/u0001f495.png', '\U0001F495'), ('emojis/u0001f496.png', '\U0001F496'), ('emojis/u0001f4a6.png', '\U0001F4A6'),
                      ('emojis/u0001f4a9.png', '\U0001F4A9'), ('emojis/u0001f4af.png', '\U0001F4AF'), ('emojis/u0001f595.png', '\U0001F595'),
                      ('emojis/u0001f600.png', '\U0001F600'), ('emojis/u0001f602.png', '\U0001F602'), ('emojis/u0001f603.png', '\U0001F603'),
                      ('emojis/u0001f605.png', '\U0001F605'), ('emojis/u0001f606.png', '\U0001F606'), ('emojis/u0001f608.png', '\U0001F608'),
                      ('emojis/u0001f60d.png', '\U0001F60D'), ('emojis/u0001f60e.png', '\U0001F60E'), ('emojis/u0001f60f.png', '\U0001F60F'),
                      ('emojis/u0001f610.png', '\U0001F610'), ('emojis/u0001f618.png', '\U0001F618'), ('emojis/u0001f61b.png', '\U0001F61B'),
                      ('emojis/u0001f61d.png', '\U0001F61D'), ('emojis/u0001f621.png', '\U0001F621'), ('emojis/u0001f624.png', '\U0001F621'),
                      ('emojis/u0001f631.png', '\U0001F631'), ('emojis/u0001f632.png', '\U0001F632'), ('emojis/u0001f634.png', '\U0001F634'),
                      ('emojis/u0001f637.png', '\U0001F637'), ('emojis/u0001f642.png', '\U0001F642'), ('emojis/u0001f64f.png', '\U0001F64F'),
                      ('emojis/u0001f920.png', '\U0001F920'), ('emojis/u0001f923.png', '\U0001F923'), ('emojis/u0001f928.png', '\U0001F928')]
        
        self.emoji_labels =[None] * 33

        self.flag_emoji = 1
        # -------------------end of emoji-------------------------------------

        send_button = tk.Button(self, text="Send", fg="#83eaf7", font="lucida 11 bold", bg="#7d7d7d", padx=10,
                                relief="solid", bd=2, cursor="hand2", command=self.sent_message_format)
        send_button.place(x=400, y=600)

        button_emojis = Image.open('emojis/u0001f642.png')
        button_emojis = button_emojis.resize((29, 28), Image.Resampling.LANCZOS)
        button_emojis = ImageTk.PhotoImage(button_emojis)

        button_emoji_unicode = '\U0001F642'
        button_emoji_label = tk.Label(self, image=button_emojis, text=button_emoji_unicode, bg="#7d7d7d", cursor="hand2", borderwidth=1, relief="solid")
        button_emoji_label.image = button_emojis
        button_emoji_label.place(x=370, y=601)
        button_emoji_label.bind('<Button-1>', self.display_emoji)

        insertImg_emojis = Image.open('emojis/insertImg.png')
        insertImg_emojis = insertImg_emojis.resize((29, 28), Image.Resampling.LANCZOS)
        insertImg_emojis = ImageTk.PhotoImage(insertImg_emojis)

        insertImg_emoji_unicode = '\U0001F642'
        insertImg_emoji_label = tk.Label(self, image=insertImg_emojis, text=insertImg_emoji_unicode, bg="#7d7d7d", cursor="hand2", borderwidth=1, relief="solid")
        insertImg_emoji_label.image = insertImg_emojis
        insertImg_emoji_label.place(x=340, y=601)
        insertImg_emoji_label.bind('<Button-1>', self.send_img_format)

        insertURL_emojis = Image.open('emojis/insertURL.png')
        insertURL_emojis = insertURL_emojis.resize((29, 28), Image.Resampling.LANCZOS)
        insertURL_emojis = ImageTk.PhotoImage(insertURL_emojis)

        insertURL_emoji_unicode = '\U0001F642'
        insertURL_emoji_label = tk.Label(self, image=insertURL_emojis, text=insertURL_emoji_unicode, bg="#7d7d7d", cursor="hand2", borderwidth=1, relief="solid")
        insertURL_emoji_label.image = insertURL_emojis
        insertURL_emoji_label.place(x=310, y=601)
        insertURL_emoji_label.bind('<Button-1>', self.send_file_format)

        self.entry = tk.Text(self, font="lucida 10 bold", width=38, height=2,
                             highlightcolor="blue", highlightthickness=1)
        self.entry.place(x=40, y=600)

        self.entry.focus_set()

        m_frame = tk.Frame(self.scrollable_frame, bg="#d9d5d4")

        t_label = tk.Label(m_frame, bg="#d9d5d4", text=datetime.now().strftime('%H:%M'), font="lucida 9 bold")
        t_label.pack()

        m_label = tk.Label(m_frame, wraplength=250, text=f"Happy Chatting {self.parent.user}",
                           font="lucida 10 bold", bg="orange")
        m_label.pack(fill="x")

        m_frame.pack(pady=10, padx=10, fill="x", expand=True, anchor="e")

        self.pack(fill="both", expand=True)

        self.clients_online([])

        t = threading.Thread(target=self.receive_data)
        t.daemon = True
        t.start()

    def display_emoji(self, event=None):
        if self.flag_emoji == 1:
            emoji_x_pos = 490
            emoji_y_pos = 450
            for Emoji in self.emoji_data:
                global emojis
                emojis = Image.open(Emoji[0])
                emojis = emojis.resize((20, 20), Image.Resampling.LANCZOS)
                emojis = ImageTk.PhotoImage(emojis)

                cur_index = self.emoji_data.index(Emoji)
                emoji_unicode = Emoji[1]
                self.emoji_labels[cur_index] = tk.Label(self, image=emojis, text=emoji_unicode, bg="#194548", cursor="hand2")
                self.emoji_labels[cur_index].image = emojis
                self.emoji_labels[cur_index].place(x=emoji_x_pos, y=emoji_y_pos)
                self.emoji_labels[cur_index].bind('<Button-1>', lambda x: self.insert_emoji(x))

                emoji_x_pos += 25
                
                if (cur_index + 1) % 6 == 0:
                    emoji_y_pos += 25
                    emoji_x_pos = 490
            self.flag_emoji = 0
        else:
            for emoji_label in self.emoji_labels:
                emoji_label.place_forget()
            self.flag_emoji = 1

    def send_img_format(self, event=None):
        self.image_path = filedialog.askopenfilename()
        image_name = os.path.basename(self.image_path)
        self.image_extension = image_name[image_name.rfind('.')+1:]

        if self.image_extension not in extensionImgSupport:
            messagebox.showinfo(title='Error File', message="The file is not supported!")
            return

        if self.image_path:
            text_image = Image.open(self.image_path)
            text_image = text_image.resize((150, 140), Image.Resampling.LANCZOS)
            text_image.save('resized'+image_name)
            text_image.close()

            self.image_path = 'resized'+image_name
            text_image = Image.open(self.image_path)
            text_image = ImageTk.PhotoImage(text_image)
            
            from_ = self.user_id

            data = {'from': from_, 'image': self.image_path}
            data_bytes = pickle.dumps(data)

            self.client_socket.send(data_bytes)

            m_frame = tk.Frame(self.scrollable_frame, bg="#595656")

            m_frame.columnconfigure(0, weight=1)

            t_label = tk.Label(m_frame, bg="#595656", fg="white", text=datetime.now().strftime('%H:%M'),
                               font="lucida 7 bold", justify="right", anchor="e")
            t_label.grid(row=0, column=0, padx=2, sticky="e")

            m_label = tk.Label(m_frame, wraplength=250, image=text_image, 
                                justify="left", anchor="e")
            m_label.image=text_image
            m_label.grid(row=1, column=0, padx=2, pady=2, sticky="e")

            i_label = tk.Label(m_frame, bg="#595656", image=self.user_image)
            i_label.image = self.user_image
            i_label.grid(row=0, column=1, rowspan=2, sticky="e")

            m_frame.pack(pady=10, padx=10, fill="x", expand=True, anchor="e")

            self.canvas.update_idletasks()
            self.canvas.yview_moveto(1.0)

    def send_file_format(self, event=None):
        self.file_path = filedialog.askopenfilename()
        file_name = os.path.basename(self.file_path)
        self.file_extension = file_name[file_name.rfind('.')+1:]
        
        if self.file_path:
            from_ = self.user_id

            data = {'from': from_, 'file': self.file_path}
            data_bytes = pickle.dumps(data)

            self.client_socket.send(data_bytes)

            m_frame = tk.Frame(self.scrollable_frame, bg="#595656")

            m_frame.columnconfigure(0, weight=1)

            t_label = tk.Label(m_frame, bg="#595656", fg="white", text=datetime.now().strftime('%H:%M'),
                               font="lucida 7 bold", justify="right", anchor="e")
            t_label.grid(row=0, column=0, padx=2, sticky="e")

            m_label = tk.Button(m_frame, wraplength=250, text=file_name, fg="black", bg="#40C961",
                               font="lucida 9 bold", justify="left",
                               anchor="e", command= lambda: self.openFile(self.file_path))
            m_label.grid(row=1, column=0, padx=2, pady=2, sticky="e")

            i_label = tk.Label(m_frame, bg="#595656", image=self.user_image)
            i_label.image = self.user_image
            i_label.grid(row=0, column=1, rowspan=2, sticky="e")

            m_frame.pack(pady=10, padx=10, fill="x", expand=True, anchor="e")

            self.canvas.update_idletasks()
            self.canvas.yview_moveto(1.0)

    def receive_data(self):
        while True:
            try:
                data_type = self.client_socket.recv(1024).decode()

                if data_type == 'notification':
                    data_size = self.client_socket.recv(1024*2)
                    data_size_int = struct.unpack('i', data_size)[0]

                    b = b''
                    while True:
                        data_bytes = self.client_socket.recv(1024)
                        b += data_bytes
                        if len(b) == data_size_int:
                            break
                    data = pickle.loads(b)
                    self.notification_format(data)

                elif data_type == 'message':
                    data_bytes = self.client_socket.recv(1024)
                    data = pickle.loads(data_bytes)
                    self.received_message_format(data)

                elif data_type == 'image':
                    data_bytes = self.client_socket.recv(1024)
                    data = pickle.loads(data_bytes)
                    self.received_image_format(data)

                else:
                    data_bytes = self.client_socket.recv(1024)
                    data = pickle.loads(data_bytes)
                    self.received_file_format(data)

            except ConnectionAbortedError:
                print("you disconnected ...")
                self.client_socket.close()
                break
            except ConnectionResetError:
                messagebox.showinfo(title='No Connection !', message="Server offline! Try connecting again later")
                self.client_socket.close()
                self.first_screen()
                break

    def on_closing(self):
        if self.window == 'ChatScreen':
            res = messagebox.askyesno(title='Warning!',message="Do you really want to disconnect ?")
            if res:
                import os
                os.remove(self.all_user_image[self.user_id])
                self.client_socket.close()
                self.first_screen()
        else:
            self.parent.destroy()

    def received_message_format(self, data):

        message = data['message']
        from_ = data['from']

        sender_image = self.clients_connected[from_][1]
        sender_image_extension = self.clients_connected[from_][2]

        # if not os.path.exists(f"{from_}.{sender_image_extension}"):
        with open(f"{from_}.{sender_image_extension}", 'wb') as f:
            f.write(sender_image)

        im = Image.open(f"{from_}.{sender_image_extension}")
        im = im.resize((40, 40), Image.Resampling.LANCZOS)
        im = ImageTk.PhotoImage(im)

        m_frame = tk.Frame(self.scrollable_frame, bg="#595656")

        m_frame.columnconfigure(1, weight=1)

        t_label = tk.Label(m_frame, bg="#595656",fg="white", text=datetime.now().strftime('%H:%M'), font="lucida 7 bold",
                           justify="left", anchor="w")
        t_label.grid(row=0, column=1, padx=2, sticky="w")

        m_label = tk.Label(m_frame, wraplength=250,fg="black", bg="#c5c7c9", text=message, font="lucida 9 bold", justify="left",
                           anchor="w")
        m_label.grid(row=1, column=1, padx=2, pady=2, sticky="w")

        i_label = tk.Label(m_frame, bg="#595656", image=im)
        i_label.image = im
        i_label.grid(row=0, column=0, rowspan=2)

        m_frame.pack(pady=10, padx=10, fill="x", expand=True, anchor="e")

        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def received_image_format(self, data):
    
        image_path = data['image']
        from_ = data['from']

        sender_image = self.clients_connected[from_][1]
        sender_image_extension = self.clients_connected[from_][2]

        # if not os.path.exists(f"{from_}.{sender_image_extension}"):
        with open(f"{from_}.{sender_image_extension}", 'wb') as f:
            f.write(sender_image)

        im = Image.open(f"{from_}.{sender_image_extension}")
        im = im.resize((40, 40), Image.Resampling.LANCZOS)
        im = ImageTk.PhotoImage(im)

        m_frame = tk.Frame(self.scrollable_frame, bg="#595656")

        m_frame.columnconfigure(1, weight=1)

        t_label = tk.Label(m_frame, bg="#595656",fg="white", text=datetime.now().strftime('%H:%M'), font="lucida 7 bold",
                           justify="left", anchor="w")
        t_label.grid(row=0, column=1, padx=2, sticky="w")

        text_image = Image.open(image_path)
        text_image = ImageTk.PhotoImage(text_image)
        m_label = tk.Label(m_frame, wraplength=250, image=text_image, 
                                justify="left", anchor="w")
        m_label.image=text_image
        m_label.grid(row=1, column=1, padx=2, pady=2, sticky="w")

        i_label = tk.Label(m_frame, bg="#595656", image=im)
        i_label.image = im
        i_label.grid(row=0, column=0, rowspan=2)

        m_frame.pack(pady=10, padx=10, fill="x", expand=True, anchor="e")

        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def received_file_format(self, data):
        
        file_path = data['file']
        from_ = data['from']

        sender_image = self.clients_connected[from_][1]
        sender_image_extension = self.clients_connected[from_][2]

        # if not os.path.exists(f"{from_}.{sender_image_extension}"):
        with open(f"{from_}.{sender_image_extension}", 'wb') as f:
            f.write(sender_image)

        im = Image.open(f"{from_}.{sender_image_extension}")
        im = im.resize((40, 40), Image.Resampling.LANCZOS)
        im = ImageTk.PhotoImage(im)

        m_frame = tk.Frame(self.scrollable_frame, bg="#595656")

        m_frame.columnconfigure(1, weight=1)

        t_label = tk.Label(m_frame, bg="#595656",fg="white", text=datetime.now().strftime('%H:%M'), font="lucida 7 bold",
                           justify="left", anchor="w")
        t_label.grid(row=0, column=1, padx=2, sticky="w")

        m_label = tk.Button(m_frame, wraplength=250,fg="black", bg="#c5c7c9", text=os.path.basename(file_path), font="lucida 9 bold", justify="left",
                           anchor="w", command= lambda: self.openFile(file_path))
        m_label.grid(row=1, column=1, padx=2, pady=2, sticky="w")

        i_label = tk.Label(m_frame, bg="#595656", image=im)
        i_label.image = im
        i_label.grid(row=0, column=0, rowspan=2)

        m_frame.pack(pady=10, padx=10, fill="x", expand=True, anchor="e")

        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def sent_message_format(self, event=None):

        message = self.entry.get('1.0', 'end-1c')

        if message != "":
            if event:
                message = message.strip()
            self.entry.delete("1.0", "end-1c")

            from_ = self.user_id

            data = {'from': from_, 'message': message}
            data_bytes = pickle.dumps(data)

            self.client_socket.send(data_bytes)

            m_frame = tk.Frame(self.scrollable_frame, bg="#595656")

            m_frame.columnconfigure(0, weight=1)

            t_label = tk.Label(m_frame, bg="#595656", fg="white", text=datetime.now().strftime('%H:%M'),
                               font="lucida 7 bold", justify="right", anchor="e")
            t_label.grid(row=0, column=0, padx=2, sticky="e")

            m_label = tk.Label(m_frame, wraplength=250, text=message, fg="black", bg="#40C961",
                               font="lucida 9 bold", justify="left",
                               anchor="e")
            m_label.grid(row=1, column=0, padx=2, pady=2, sticky="e")

            i_label = tk.Label(m_frame, bg="#595656", image=self.user_image)
            i_label.image = self.user_image
            i_label.grid(row=0, column=1, rowspan=2, sticky="e")

            m_frame.pack(pady=10, padx=10, fill="x", expand=True, anchor="e")

            self.canvas.update_idletasks()
            self.canvas.yview_moveto(1.0)

    def notification_format(self, data):
        if data['n_type'] == 'joined':

            name = data['name']
            image = data['image_bytes']
            extension = data['extension']
            message = data['message']
            client_id = data['id']
            self.clients_connected[client_id] = (name, image, extension)
            self.clients_online([client_id, name, image, extension])
            # print(self.clients_connected)

        elif data['n_type'] == 'left':
            client_id = data['id']
            message = data['message']
            self.remove_labels(client_id)
            del self.clients_connected[client_id]

        m_frame = tk.Frame(self.scrollable_frame, bg="#595656")

        t_label = tk.Label(m_frame, fg="white", bg="#595656", text=datetime.now().strftime('%H:%M'),
                           font="lucida 9 bold")
        t_label.pack()

        m_label = tk.Label(m_frame, wraplength=250, text=message, font="lucida 10 bold", justify="left", bg="sky blue")
        m_label.pack()

        m_frame.pack(pady=10, padx=10, fill="x", expand=True, anchor="e")

        self.canvas.yview_moveto(1.0)

    def clients_online(self, new_added):
        if not new_added:
            pass
            for user_id in self.clients_connected:
                name = self.clients_connected[user_id][0]
                image_bytes = self.clients_connected[user_id][1]
                extension = self.clients_connected[user_id][2]

                with open(f"{user_id}.{extension}", 'wb') as f:
                    f.write(image_bytes)

                self.all_user_image[user_id] = f"{user_id}.{extension}"

                user = Image.open(f"{user_id}.{extension}")
                user = user.resize((45, 45), Image.Resampling.LANCZOS)
                user = ImageTk.PhotoImage(user)

                b = tk.Label(self, image=user, text=name, compound="left",fg="white", bg="#2b2b2b", font="lucida 10 bold", padx=15)
                b.image = user
                self.clients_online_labels[user_id] = (b, self.y)

                b.place(x=500, y=self.y)
                self.y += 60


        else:
            user_id = new_added[0]
            name = new_added[1]
            image_bytes = new_added[2]
            extension = new_added[3]

            with open(f"{user_id}.{extension}", 'wb') as f:
                f.write(image_bytes)

            self.all_user_image[user_id] = f"{user_id}.{extension}"

            user = Image.open(f"{user_id}.{extension}")
            user = user.resize((45, 45), Image.Resampling.LANCZOS)
            user = ImageTk.PhotoImage(user)

            b = tk.Label(self, image=user, text=name, compound="left", fg="white", bg="#2b2b2b",
                         font="lucida 10 bold", padx=15)
            b.image = user
            self.clients_online_labels[user_id] = (b, self.y)

            b.place(x=500, y=self.y)
            self.y += 60

    def remove_labels(self, client_id):
        for user_id in self.clients_online_labels.copy():
            b = self.clients_online_labels[user_id][0]
            y_co = self.clients_online_labels[user_id][1]
            if user_id == client_id:
                print("yes")
                b.destroy()
                del self.clients_online_labels[client_id]
                import os
                # os.remove(self.all_user_image[user_id])

            elif user_id > client_id:
                y_co -= 60
                b.place(x=510, y=y_co)
                self.clients_online_labels[user_id] = (b, y_co)
                self.y -= 60

    def insert_emoji(self, x):
        self.entry.insert("end-1c", x.widget['text'])

    def openFile(self, file_path):
        os.startfile(os.path.abspath(file_path)) 

    def first_screen(self):
        self.destroy()
        self.parent.geometry(f"550x400+{self.parent.x_sub}+{self.parent.y_sub}")
        self.parent.first_frame.pack(fill="both", expand=True)
        self.window = None

FirstScreen()
