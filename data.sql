CREATE TABLE book(
	book_id serial primary key,
	book_name text,
	press text,
	author text,
	ISBN varchar(15),
	amount int,
	order_amount int,
	borrow_amount int
);

CREATE TABLE reader(
	reader_id serial primary key,
	name text,
	password text
);

CREATE TABLE order_book(
	book_id int,
	reader_id int,
	order_time date,
	expire_time date,
	primary key(book_id, reader_id),
	foreign key(book_id)references book(book_id),
	foreign key(reader_id)references reader(reader_id)
);

CREATE TABLE borrow_book(
	book_id int,
	reader_id int,
	borrow_time date,
	expire_time date,
	primary key(book_id, reader_id),
	foreign key(book_id)references book(book_id),
	foreign key(reader_id)references reader(reader_id)
);
	
