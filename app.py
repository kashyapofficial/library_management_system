# -*- coding:utf-8 -*-

import gtk
import psycopg2
import sys


class BookBox(gtk.HBox):

    def __init__(self, homogeneous, spacing, book_info, reader_id):
        super(BookBox, self).__init__(homogeneous, spacing)

        self.reader_id = reader_id
        try:
            self.book = gtk.gdk.pixbuf_new_from_file("book.svg")
        except Exception, e:
            print e.message
            sys.exit(1)

        book_image = gtk.Image()
        book_image.set_from_pixbuf(self.book)
        self.pack_start(book_image, False, False, 0)

        info_vbox = gtk.VBox(False, 5)

        (book_id, book_name, press, author, isbn, amount, order_amount, borrow_amount) = book_info

        self.book_id = book_id

        name_label = gtk.Label()
        name_label.set_markup('<span size="15000"><b>' + book_name + '</b></span>')
        info_vbox.pack_start(name_label, False, False, 0)

        press_label = gtk.Label("出版社：" + press)
        press_label.set_alignment(0, 0.5)
        author_label = gtk.Label("作者：" + author)
        author_label.set_alignment(0, 0.5)
        isbn_label = gtk.Label("ISBN：" + isbn)
        isbn_label.set_alignment(0, 0.5)
        info_vbox.pack_start(press_label, False, False, 0)
        info_vbox.pack_start(author_label, False, False, 0)
        info_vbox.pack_start(isbn_label, False, False, 0)

        self.pack_start(info_vbox, False, False, 20)

        amount_vbox = gtk.VBox(False, 6)
        amount_label = gtk.Label("馆藏复本:" + str(amount) + "，已出借复本:" + str(borrow_amount))
        amount_vbox.pack_end(amount_label, False, False, 0)

        self.pack_start(amount_vbox, False, False, 20)

        button_vbox = gtk.VBox(False, 6)
        if (amount - borrow_amount) == order_amount:
            order_button = gtk.Button("已预约完")
        else:
            order_button = gtk.Button("预约")
            order_button.connect("clicked", self.on_order_button_clicked)
        if amount == borrow_amount:
            borrow_button = gtk.Button("已借完")
        else:
            borrow_button = gtk.Button("借阅")
            borrow_button.connect("clicked", self.on_borrow_button_clicked)
        button_vbox.pack_end(order_button, False, False, 0)
        button_vbox.pack_end(borrow_button, False, False, 0)

        self.pack_end(button_vbox, False, False, 20)

    def on_order_button_clicked(self, widget):

        con = None
        try:

            con = psycopg2.connect("dbname='librarydb' user='dbuser' host='127.0.0.1' password='dbuser'")
            cur = con.cursor()

            cur.execute("SELECT amount, order_amount, borrow_amount FROM book WHERE book_id=%s", (self.book_id, ))

            (amount, order_amount, borrow_amount) = cur.fetchone()
            if (amount - borrow_amount) == order_amount:
                md = gtk.MessageDialog(self.get_toplevel(),
                    gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
                    gtk.BUTTONS_CLOSE, "已预约完!")
                md.run()
                md.destroy()
            else:
                cur.execute("SELECT reader_id, book_id FROM order_book WHERE reader_id=%s AND book_id=%s", (self.reader_id, self.book_id))
                # print cur.fetchall()
                if cur.fetchall() == []:
                    cur.execute("INSERT INTO order_book VALUES (%s, %s, CURRENT_DATE, CURRENT_DATE + INTERVAL '7 day')", (self.book_id, self.reader_id))
                    cur.execute("UPDATE book SET order_amount=order_amount + 1 WHERE book_id=%s", (self.book_id, ))
                    con.commit()
                    md = gtk.MessageDialog(self.get_toplevel(),
                        gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO,
                        gtk.BUTTONS_CLOSE, "预约成功!")
                    md.run()
                    md.destroy()
                else:
                    md = gtk.MessageDialog(self.get_toplevel(),
                        gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
                        gtk.BUTTONS_CLOSE, "你已预约过!")
                    md.run()
                    md.destroy()

        except psycopg2.DatabaseError, e:
            print 'Error %s' % e
            sys.exit(1)

        finally:
            if con:
                con.close()

    def on_borrow_button_clicked(self, widget):

        con = None
        try:

            con = psycopg2.connect("dbname='librarydb' user='dbuser' host='127.0.0.1' password='dbuser'")
            cur = con.cursor()

            cur.execute("SELECT amount, order_amount, borrow_amount FROM book WHERE book_id=%s", (self.book_id, ))

            (amount, order_amount, borrow_amount) = cur.fetchone()
            if amount == borrow_amount:
                md = gtk.MessageDialog(self.get_toplevel(),
                    gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
                    gtk.BUTTONS_CLOSE, "已借完!")
                md.run()
                md.destroy()
            else:
                cur.execute("SELECT reader_id, book_id FROM borrow_book WHERE reader_id=%s AND book_id=%s", (self.reader_id, self.book_id))
                if cur.fetchall() == []:
                    cur.execute("INSERT INTO borrow_book VALUES (%s, %s, CURRENT_DATE, CURRENT_DATE + INTERVAL '30 day')", (self.book_id, self.reader_id))
                    cur.execute("UPDATE book SET borrow_amount=borrow_amount + 1 WHERE book_id=%s", (self.book_id, ))
                    con.commit()
                    md = gtk.MessageDialog(self.get_toplevel(),
                        gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO,
                        gtk.BUTTONS_CLOSE, "借阅成功!")
                    md.run()
                    md.destroy()
                else:
                    md = gtk.MessageDialog(self.get_toplevel(),
                        gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
                        gtk.BUTTONS_CLOSE, "你已借过!")
                    md.run()
                    md.destroy()

        except psycopg2.DatabaseError, e:
            print 'Error %s' % e
            sys.exit(1)

        finally:
            if con:
                con.close()


class BorrowBookBox(gtk.HBox):

    def __init__(self, homogeneous, spacing, book_info, reader_id):
        super(BorrowBookBox, self).__init__(homogeneous, spacing)

        self.reader_id =reader_id

        try:
            self.book = gtk.gdk.pixbuf_new_from_file("book.svg")
        except Exception, e:
            print e.message
            sys.exit(1)

        book_image = gtk.Image()
        book_image.set_from_pixbuf(self.book)
        self.pack_start(book_image, False, False, 0)

        info_vbox = gtk.VBox(False, 5)

        (book_id, book_name, press, author, isbn, borrow_time, expire_time) = book_info

        self.book_id = book_id

        name_label = gtk.Label()
        name_label.set_markup('<span size="15000"><b>' + book_name + '</b></span>')
        info_vbox.pack_start(name_label, False, False, 0)

        press_label = gtk.Label("出版社：" + press)
        press_label.set_alignment(0, 0.5)
        author_label = gtk.Label("作者：" + author)
        author_label.set_alignment(0, 0.5)
        isbn_label = gtk.Label("ISBN：" + isbn)
        isbn_label.set_alignment(0, 0.5)
        info_vbox.pack_start(press_label, False, False, 0)
        info_vbox.pack_start(author_label, False, False, 0)
        info_vbox.pack_start(isbn_label, False, False, 0)

        self.pack_start(info_vbox, False, False, 20)

        time_vbox = gtk.VBox(False, 10)
        borrow_time_label = gtk.Label("借书日期：" + str(borrow_time))
        expire_time_label = gtk.Label("应还日期：" + str(expire_time))

        time_vbox.pack_end(expire_time_label, False, False, 0)
        time_vbox.pack_end(borrow_time_label, False, False, 0)

        self.pack_start(time_vbox, False, False, 50)

        button_vbox = gtk.VBox(False, 6)
        self.return_button = gtk.Button("还书")
        self.return_button.set_size_request(70, 35)
        self.return_button.connect("clicked", self.on_clicked)
        button_vbox.pack_end(self.return_button, False, False, 0)
        self.pack_end(button_vbox, False, False, 20)

    def on_clicked(self, widget):

        con = None
        try:

            con = psycopg2.connect("dbname='librarydb' user='dbuser' host='127.0.0.1' password='dbuser'")
            cur = con.cursor()

            cur.execute("SELECT reader_id, book_id FROM borrow_book WHERE reader_id=%s AND book_id=%s", (self.reader_id, self.book_id))
            
            if cur.fetchall() == []:
                
                md = gtk.MessageDialog(self.get_toplevel(),
                    gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
                    gtk.BUTTONS_CLOSE, "你已还书!")
                md.run()
                md.destroy()
            else:
                cur.execute("DELETE FROM borrow_book WHERE book_id=%s AND reader_id=%s", (self.book_id, self.reader_id))
                cur.execute("UPDATE book SET borrow_amount=borrow_amount - 1 WHERE book_id=%s", (self.book_id, ))
                con.commit()
                md = gtk.MessageDialog(self.get_toplevel(),
                    gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO,
                    gtk.BUTTONS_CLOSE, "还书成功!")
                md.run()
                md.destroy()
                self.return_button.set_label("已还书")


        except psycopg2.DatabaseError, e:
            print 'Error %s' % e
            sys.exit(1)

        finally:
            if con:
                con.close()


class OrderBookBox(gtk.HBox):

    def __init__(self, homogeneous, spacing, book_info, reader_id):
        super(OrderBookBox, self).__init__(homogeneous, spacing)

        self.reader_id = reader_id

        try:
            self.book = gtk.gdk.pixbuf_new_from_file("book.svg")
        except Exception, e:
            print e.message
            sys.exit(1)

        book_image = gtk.Image()
        book_image.set_from_pixbuf(self.book)
        self.pack_start(book_image, False, False, 0)

        info_vbox = gtk.VBox(False, 5)

        (book_id, book_name, press, author, isbn, order_time, expire_time) = book_info

        self.book_id = book_id

        name_label = gtk.Label()
        name_label.set_markup('<span size="15000"><b>' + book_name + '</b></span>')
        info_vbox.pack_start(name_label, False, False, 0)

        press_label = gtk.Label("出版社：" + press)
        press_label.set_alignment(0, 0.5)
        author_label = gtk.Label("作者：" + author)
        author_label.set_alignment(0, 0.5)
        isbn_label = gtk.Label("ISBN：" + isbn)
        isbn_label.set_alignment(0, 0.5)
        info_vbox.pack_start(press_label, False, False, 0)
        info_vbox.pack_start(author_label, False, False, 0)
        info_vbox.pack_start(isbn_label, False, False, 0)

        self.pack_start(info_vbox, False, False, 20)

        time_vbox = gtk.VBox(False, 10)
        order_time_label = gtk.Label("预约日期：" + str(order_time))
        expire_time_label = gtk.Label("失效日期：" + str(expire_time))

        time_vbox.pack_end(expire_time_label, False, False, 0)
        time_vbox.pack_end(order_time_label, False, False, 0)

        self.pack_start(time_vbox, False, False, 50)

        button_vbox = gtk.VBox(False, 6)
        self.cancel_order_button = gtk.Button("取消预约")
        self.cancel_order_button.set_size_request(90, 35)
        self.cancel_order_button.connect("clicked", self.on_clicked)
        button_vbox.pack_end(self.cancel_order_button, False, False, 0)
        self.pack_end(button_vbox, False, False, 20)

    def on_clicked(self, widget):

        con = None
        try:

            con = psycopg2.connect("dbname='librarydb' user='dbuser' host='127.0.0.1' password='dbuser'")
            cur = con.cursor()

            cur.execute("SELECT reader_id, book_id FROM order_book WHERE reader_id=%s AND book_id=%s", (self.reader_id, self.book_id))
           
            if cur.fetchall() == []:
                
                md = gtk.MessageDialog(self.get_toplevel(),
                    gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
                    gtk.BUTTONS_CLOSE, "你已取消预约!")
                md.run()
                md.destroy()
            else:
                cur.execute("DELETE FROM order_book WHERE book_id=%s AND reader_id=%s", (self.book_id, self.reader_id))
                cur.execute("UPDATE book SET order_amount=order_amount - 1 WHERE book_id=%s", (self.book_id, ))
                con.commit()
                md = gtk.MessageDialog(self.get_toplevel(),
                    gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO,
                    gtk.BUTTONS_CLOSE, "取消预约成功!")
                md.run()
                md.destroy()
                self.cancel_order_button.set_label("已取消")


        except psycopg2.DatabaseError, e:
            print 'Error %s' % e
            sys.exit(1)

        finally:
            if con:
                con.close()


class MainWindow(gtk.Window):

    reader_id = None

    def __init__(self, reader_id):

        super(MainWindow, self).__init__()

        self.reader_id = reader_id

        print reader_id, "aaaa"

        self.set_title("图书管理系统")
        self.set_size_request(900, 600)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_border_width(10)
        self.set_icon_from_file("web.png")
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color('#fff'))

        notebook = gtk.Notebook()
        notebook.set_tab_pos(gtk.POS_LEFT)
        self.add(notebook)

        home_frame = gtk.Frame("主页")
        home_frame.set_border_width(10)

        home_vbox = gtk.VBox(False, 8)

        try:
            self.library = gtk.gdk.pixbuf_new_from_file("library2.png")
        except Exception, e:
            print e.message
            sys.exit(1)

        library_image = gtk.Image()
        library_image.set_from_pixbuf(self.library)
        library_image.set_size_request(400, 400)

        home_label = gtk.Label()
        home_label.set_markup('<span size="30000">欢迎使用图书管理系统！</span>')

        home_vbox.pack_start(library_image, False, False, 0)
        home_vbox.pack_start(home_label, False, False, 0)
        home_frame.add(home_vbox)
        notebook.append_page(home_frame, gtk.Label("主页"))



        me_borrow_frame = gtk.Frame("借阅信息")
        me_borrow_frame.set_border_width(10)
        self.borrow_sw = gtk.ScrolledWindow()

        self.borrow_vbox = gtk.VBox(False, 20)
        self.borrow_vbox.set_border_width(10)

        message_label = gtk.Label()
        message_label.set_markup('<span size="12000"><b>' + "我的借阅：" + '</b></span>')
        message_label.set_alignment(0, 0.5)
        self.borrow_vbox.pack_start(message_label, False, False, 0)

        borrow_book_list = self.get_borrow_book_list()

        for i in range(len(borrow_book_list)):
            book_box = BorrowBookBox(False, 8, borrow_book_list[i], self.reader_id)
            self.borrow_vbox.pack_start(book_box, False, False, 0)

        self.borrow_sw.add_with_viewport(self.borrow_vbox)

        if len(borrow_book_list) == 0:

            b_vbox = gtk.VBox(False, 8)

            try:
                self.library = gtk.gdk.pixbuf_new_from_file("library2.png")
            except Exception, e:
                print e.message
                sys.exit(1)

            library_image = gtk.Image()
            library_image.set_from_pixbuf(self.library)
            library_image.set_size_request(400, 400)

            borrow_label = gtk.Label()
            borrow_label.set_markup('<span size="30000">无借阅信息</span>')

            b_vbox.pack_start(library_image, False, False, 0)
            b_vbox.pack_start(borrow_label, False, False, 0)
            me_borrow_frame.add(b_vbox)

            
        else:
            me_borrow_frame.add(self.borrow_sw)

        notebook.append_page(me_borrow_frame, gtk.Label("借阅信息"))



        me_order_frame = gtk.Frame("预约信息")
        me_order_frame.set_border_width(10)

        self.order_sw = gtk.ScrolledWindow()

        self.order_vbox = gtk.VBox(False, 20)
        self.order_vbox.set_border_width(10)

        message_label = gtk.Label()
        message_label.set_markup('<span size="12000"><b>' + "我的预约：" + '</b></span>')
        message_label.set_alignment(0, 0.5)
        self.order_vbox.pack_start(message_label, False, False, 0)

        order_book_list = self.get_order_book_list()

        for i in range(len(order_book_list)):
            book_box = OrderBookBox(False, 8, order_book_list[i], self.reader_id)
            self.order_vbox.pack_start(book_box, False, False, 0)

        self.order_sw.add_with_viewport(self.order_vbox)

        if len(order_book_list) == 0:

            o_vbox = gtk.VBox(False, 8)

            try:
                self.library = gtk.gdk.pixbuf_new_from_file("library2.png")
            except Exception, e:
                print e.message
                sys.exit(1)

            library_image = gtk.Image()
            library_image.set_from_pixbuf(self.library)
            library_image.set_size_request(400, 400)

            order_label = gtk.Label()
            order_label.set_markup('<span size="30000">无预约信息</span>')

            o_vbox.pack_start(library_image, False, False, 0)
            o_vbox.pack_start(order_label, False, False, 0)
            me_order_frame.add(o_vbox)

            
        else:
            me_order_frame.add(self.order_sw)
        notebook.append_page(me_order_frame, gtk.Label("预约信息"))



        order_frame = gtk.Frame("预约图书")
        order_frame.set_border_width(10)

        self.sw = gtk.ScrolledWindow()

        self.vbox = gtk.VBox(False, 20)
        self.vbox.set_border_width(10)

        hbox = gtk.HBox(False, 8)
        hbox.set_border_width(10)
        self.search_entry = gtk.Entry()
        self.search_entry.set_size_request(10, 33)
        search_button = gtk.Button("搜索")
        search_button.set_size_request(80, 33)
        search_button.connect("clicked", self.on_search_button_clicked)
        hbox.pack_start(self.search_entry, True, True, 0)
        hbox.pack_end(search_button, False, False, 0)

        self.book_list = self.get_book()
        self.book_amount = 0

        message_label = gtk.Label()
        message_label.set_markup('<span size="12000"><b>' + "共有" + str(len(self.book_list)) + "本图书。" + '</b></span>')
        message_label.set_alignment(0, 0.5)
        self.vbox.pack_start(message_label, False, False, 0)

        for i in range(10):
            if self.book_amount > len(self.book_list) - 1:
                break
            else:
                book_box = BookBox(False, 8, self.book_list[self.book_amount], self.reader_id)
                self.vbox.pack_start(book_box, False, False, 0)
                self.book_amount += 1

        more_button = gtk.Button("更多图书")
        more_button.connect("clicked", self.on_clicked)
        self.vbox.pack_end(more_button, False, False, 0)

        self.sw.add_with_viewport(self.vbox)

        vbox = gtk.VBox(False, 20)
        vbox.pack_start(hbox, False, False, 0)
        vbox.pack_start(self.sw, True, True, 0)
        order_frame.add(vbox)
        notebook.append_page(order_frame, gtk.Label("预约图书"))

        self.connect("destroy", gtk.main_quit)
        self.show_all()

    def get_order_book_list(self):

        con = None
        try:

            con = psycopg2.connect("dbname='librarydb' user='dbuser' host='127.0.0.1' password='dbuser'")
            cur = con.cursor()

            cur.execute("SELECT book.book_id,book_name,press,author,ISBN,order_time,expire_time FROM book,order_book WHERE book.book_id=order_book.book_id AND reader_id=%s", (self.reader_id, ))

            order_book_list = cur.fetchall()
            return order_book_list

        except psycopg2.DatabaseError, e:
            print 'Error %s' % e
            sys.exit(1)

        finally:
            if con:
                con.close()

    def get_borrow_book_list(self):

        con = None
        try:

            con = psycopg2.connect("dbname='librarydb' user='dbuser' host='127.0.0.1' password='dbuser'")
            cur = con.cursor()

            cur.execute("SELECT book.book_id,book_name,press,author,ISBN,borrow_time,expire_time FROM book,borrow_book WHERE book.book_id=borrow_book.book_id AND reader_id=%s", (self.reader_id, ))

            borrow_book_list = cur.fetchall()
            return borrow_book_list

        except psycopg2.DatabaseError, e:
            print 'Error %s' % e
            sys.exit(1)

        finally:
            if con:
                con.close()

    def on_search_button_clicked(self, widget):

        text = self.search_entry.get_text()
        keyword = text.split()

        con = None
        self.search_result = []
        self.search_book_amount = 0
        try:

            con = psycopg2.connect("dbname='librarydb' user='dbuser' host='127.0.0.1' password='dbuser'")
            cur = con.cursor()

            for word in keyword:
                cur.execute("SELECT * FROM book WHERE book_name LIKE '%" +
                            word + "%' OR press LIKE '%" + word + "%' OR author LIKE '%" + word + "%'")
                self.search_result += cur.fetchall()

        except psycopg2.DatabaseError, e:
            print 'Error %s' % e
            sys.exit(1)

        finally:
            if con:
                con.close()

        self.vbox.destroy()

        self.vbox = gtk.VBox(False, 20)
        self.vbox.set_border_width(10)

        message_label = gtk.Label()
        message_label.set_markup('<span size="12000"><b>' + "搜索到" + str(len(self.search_result)) + "本图书。" + '</b></span>')
        message_label.set_alignment(0, 0.5)
        self.vbox.pack_start(message_label, False, False, 0)

        for i in range(10):
            if self.search_book_amount > len(self.search_result) - 1:
                break
            else:
                book_box = BookBox(False, 8, self.search_result[self.search_book_amount], self.reader_id)
                self.vbox.pack_start(book_box, False, False, 0)
                self.search_book_amount += 1

        more_button = gtk.Button("更多图书")
        more_button.connect("clicked", self.on_more_search_clicked)
        self.vbox.pack_end(more_button, False, False, 0)

        self.sw.add_with_viewport(self.vbox)

        self.show_all()

    def on_more_search_clicked(self, widget):

        for i in range(10):
            if self.search_book_amount > len(self.search_result) - 1:
                break
            else:
                book_box = BookBox(False, 8, self.search_result[self.search_book_amount], self.reader_id)
                self.vbox.pack_start(book_box, False, False, 0)
                self.search_book_amount += 1

        self.show_all()

    def on_clicked(self, widget):

        for i in range(10):
            if self.book_amount > len(self.book_list) - 1:
                break
            else:
                book_box = BookBox(False, 8, self.book_list[self.book_amount], self.reader_id)
                self.vbox.pack_start(book_box, False, False, 0)
                self.book_amount += 1

        self.show_all()

    def get_book(self):

        con = None
        try:

            con = psycopg2.connect("dbname='librarydb' user='dbuser' host='127.0.0.1' password='dbuser'")
            cur = con.cursor()
            cur.execute("SELECT * FROM book")

            book_list = cur.fetchall()
            return book_list


        except psycopg2.DatabaseError, e:
            print 'Error %s' % e
            sys.exit(1)

        finally:
            if con:
                con.close()


class LoginWindow(gtk.Window):

    name_entry = None
    password_entry = None

    """docstring for LoginWindow"""
    def __init__(self):

        super(LoginWindow, self).__init__()
        self.set_title("图书管理系统")
        self.set_size_request(600, 400)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_icon_from_file("web.png")
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color('#fff'))

        try:
            self.library = gtk.gdk.pixbuf_new_from_file("library3.png")
        except Exception, e:
            print e.message
            sys.exit(1)

        library_image = gtk.Image()
        library_image.set_from_pixbuf(self.library)
        library_image.set_size_request(100, 100)

        title_label = gtk.Label()
        title_label.set_markup('<span size="20000">欢迎使用图书管理系统!</span>')
        name_label = gtk.Label("账号")
        password_label = gtk.Label("密码")
        self.name_entry = gtk.Entry()
        self.name_entry.set_size_request(280, 30)
        self.password_entry = gtk.Entry()
        self.password_entry.set_size_request(280, 30)
        self.password_entry.set_visibility(False)

        login_button = gtk.Button("登录")
        login_button.set_size_request(280, 30)
        login_button.connect("clicked", self.on_clicked)

        fix = gtk.Fixed()

        fix.put(library_image, 250, 20)
        fix.put(title_label, 165, 147)
        fix.put(name_label, 160, 200)
        fix.put(self.name_entry, 160, 220)
        fix.put(password_label, 160, 260)
        fix.put(self.password_entry, 160, 280)
        fix.put(login_button, 160, 340)

        self.add(fix)

        self.connect("destroy", gtk.main_quit)
        self.show_all()

    def on_clicked(self, widget):

        con = None
        try:
            name = self.name_entry.get_text()
            password = self.password_entry.get_text()
            con = psycopg2.connect("dbname='librarydb' user='dbuser' host='127.0.0.1' password='dbuser'") 
            cur = con.cursor()
            cur.execute("SELECT reader_id,password FROM reader WHERE name = %s", (name, ))

            record = cur.fetchone()
            if record is None:
                md = gtk.MessageDialog(self,
                    gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
                    gtk.BUTTONS_CLOSE, "user not exist.")
                md.run()
                md.destroy()
            else:
                (reader_id, password_record, ) = record
                if password != password_record:
                    md = gtk.MessageDialog(self,
                        gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
                        gtk.BUTTONS_CLOSE, "password is wrong!")
                    md.run()
                    md.destroy()
                else:
                    print "password is true."
                    MainWindow(reader_id)
                    self.hide()

        except psycopg2.DatabaseError, e:
            print 'Error %s' % e    
            sys.exit(1)

        finally:
            if con:
                con.close()


LoginWindow()
gtk.main()
