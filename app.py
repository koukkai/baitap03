# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Database connection function
def connect_db(dbname='postgres'):
    try:
        conn = psycopg2.connect(
            dbname="227480201IS002",
            user="postgres",
            password="koukkai21",
            host="localhost",
            port='5432'
        )
        print(f"Connection to {dbname} successful")
        return conn
    except Exception as e:
        print(f"Error while connecting to database {dbname}:", e)
        raise

def create_table():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Create books table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255) NOT NULL,
                year INTEGER NOT NULL,
                genre VARCHAR(100) NOT NULL
            );
        """)
        conn.commit()
        print("Table 'books' has been created successfully.")
        
    except Exception as e:
        print("Error while creating table:", e)
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Routes
@app.route('/')
def index():
    try:
        conn = connect_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM books ORDER BY id DESC")
        books = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('index.html', books=books)
    except Exception as e:
        flash(f'Lỗi kết nối database: {str(e)}', 'error')
        return render_template('index.html', books=[])

@app.route('/add_book', methods=['POST'])
def add_book():
    if request.method == 'POST':
        try:
            title = request.form['title']
            author = request.form['author']
            year = request.form['year']
            genre = request.form['genre']
            
            if not all([title, author, year, genre]):
                flash('Vui lòng điền đầy đủ thông tin!', 'error')
                return redirect(url_for('index'))
            
            conn = connect_db()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO books (title, author, year, genre) VALUES (%s, %s, %s, %s)",
                (title, author, year, genre)
            )
            conn.commit()
            cur.close()
            conn.close()
            
            flash('Thêm sách thành công!', 'success')
        except Exception as e:
            flash(f'Lỗi khi thêm sách: {str(e)}', 'error')
        
        return redirect(url_for('index'))

@app.route('/update_book/<int:id>', methods=['POST'])
def update_book(id):
    try:
        title = request.form['title']
        author = request.form['author']
        year = request.form['year']
        genre = request.form['genre']
        
        conn = connect_db()
        cur = conn.cursor()
        cur.execute(
            """UPDATE books 
               SET title=%s, author=%s, year=%s, genre=%s 
               WHERE id=%s""",
            (title, author, year, genre, id)
        )
        conn.commit()
        cur.close()
        conn.close()
        
        flash('Cập nhật sách thành công!', 'success')
    except Exception as e:
        flash(f'Lỗi khi cập nhật sách: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/delete_book/<int:id>')
def delete_book(id):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM books WHERE id=%s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        
        flash('Xóa sách thành công!', 'success')
    except Exception as e:
        flash(f'Lỗi khi xóa sách: {str(e)}', 'error')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    try:
        create_table()
    except Exception as e:
        print(f"Error during initialization: {e}")
    app.run(debug=True)
