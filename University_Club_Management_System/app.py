from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='password',  
        database='UCMS'
    )
    return conn

# Direct the root route ('/') to the login page
@app.route('/')
def root():
    return redirect(url_for('login'))

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']  
        conn = get_db_connection()
        cursor = conn.cursor()
        # Check if the user already exists
        cursor.execute('SELECT * FROM User WHERE username = %s', (username,))
        user = cursor.fetchone()
        if user:
            flash('Username already exists! Please log in or use a different username.')
            return redirect(url_for('login'))
        # Check if there is already a club head
        if user_type == 'club_head':
            cursor.execute('SELECT * FROM User WHERE user_type = %s', ('club_head',))
            existing_club_head = cursor.fetchone()
            if existing_club_head:
                flash('A club head already exists! You cannot register another club head.')
                return redirect(url_for('login'))
        hashed_password = generate_password_hash(password)
        cursor.execute("INSERT INTO User (username, password, user_type) VALUES (%s, %s, %s)", 
                       (username, hashed_password, user_type))
        conn.commit()
        conn.close()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type'] 
        conn = get_db_connection()
        cursor = conn.cursor()
        # Check if the user exists
        cursor.execute('SELECT * FROM User WHERE username = %s', (username,))
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = username
            session['user_type'] = user_type
            if user_type == 'club_head':
                return redirect(url_for('index1'))
            else:
                return redirect(url_for('index'))
        flash('Incorrect username or password. Please try again.')
        return redirect(url_for('login'))
    return render_template('login.html')

# Index route for normal users
@app.route('/index')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

# Index route for club heads
@app.route('/index1')
def index1():
    if 'user_id' not in session or session.get('user_type') != 'club_head':
        return redirect(url_for('login'))
    return render_template('index1.html')

# Add Event route
@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if 'user_id' not in session or session.get('user_type') != 'club_head':
        return redirect(url_for('login'))
    if request.method == 'POST':
        event_name = request.form['event_name']
        date_of_conduction = request.form['date_of_conduction']
        venue = request.form['venue']
        building = request.form['building']
        conn = get_db_connection()
        cursor = conn.cursor()
        # Insert the new event into the Events table
        cursor.execute("INSERT INTO Events (event_name, date_of_conduction, venue, building) VALUES (%s, %s, %s, %s)",
                       (event_name, date_of_conduction, venue, building))
        conn.commit()
        conn.close()
        flash('Event added successfully!')
        return redirect(url_for('index1'))
    return render_template('addevents.html')

# Profile route (allows user to view and edit their profile)
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)   
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        srn = request.form.get('SRN')
        gender = request.form.get('gender')
        email = request.form.get('email')
        dob = request.form.get('DOB')
        phone = request.form.get('phone_no')        
        try:
            # Check if profile exists
            cursor.execute('SELECT * FROM Profile WHERE user_id = %s', (session['user_id'],))
            existing_profile = cursor.fetchone()            
            if existing_profile:
                # Update existing profile
                cursor.execute('''UPDATE Profile 
                                  SET name = %s, SRN = %s, gender = %s, email = %s, DOB = %s, phone_no = %s 
                                  WHERE user_id = %s''',
                               (name, srn, gender, email, dob, phone, session['user_id']))
            else:
                # Create new profile
                cursor.execute('''INSERT INTO Profile (user_id, name, SRN, gender, email, DOB, phone_no) 
                                  VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                               (session['user_id'], name, srn, gender, email, dob, phone))            
            conn.commit()
            flash('Profile updated successfully!')
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            flash('An error occurred while updating the profile')
            conn.rollback()
    # Get current profile data
    cursor.execute('SELECT * FROM Profile WHERE user_id = %s', (session['user_id'],))
    profile = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('profile.html', profile=profile)

# Events route
@app.route('/events')
def events():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT event_name, date_of_conduction, venue, building FROM events")
    events = cursor.fetchall()
    conn.close()
    return render_template('Events.html', events=events)

@app.route('/members')
def members():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT member_id, name, domain, role FROM Members")
    members_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('members.html', members=members_list)

# Route to display add members form
@app.route('/addmembers')
def addmembers():
    return render_template('addmembers.html')

# Route to add a member
@app.route('/add_member', methods=['POST'])
def add_member():
    member_id = request.form['member_id']
    name = request.form['name']
    domain = request.form['domain']
    role = request.form['role']
    conn = get_db_connection()
    cursor = conn.cursor()
    # Check if member_id already exists
    cursor.execute("SELECT * FROM Members WHERE member_id = %s", (member_id,))
    existing_member = cursor.fetchone()
    if existing_member:
        flash("Member ID already exists.", "error")
        cursor.close()
        conn.close()
        return redirect(url_for('addmembers'))
    # Add new member to database
    cursor.execute("INSERT INTO Members (member_id, name, domain, role) VALUES (%s, %s, %s, %s)", 
                   (member_id, name, domain, role))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Member added successfully!", "success")
    return redirect(url_for('addmembers'))

# Route to delete a member
@app.route('/delete_member', methods=['POST'])
def delete_member():
    member_id = request.form['delete_member_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    # Delete member by ID
    cursor.execute("DELETE FROM Members WHERE member_id = %s", (member_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Member deleted successfully!", "success")
    return redirect(url_for('addmembers'))

# Route to display announcements
@app.route('/announce')
def announce():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, content, date_posted FROM Announcement")
    announcements = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('announce.html', announcements=announcements)

# Route to display add announcement form
@app.route('/addannounce')
def addannounce():
    return render_template('addannounce.html')

# Route to add a new announcement
@app.route('/add_announcement', methods=['GET', 'POST'])
def add_announcement():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        # Fetch the current date and time
        date_posted = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Announcement (title, content, date_posted) VALUES (%s, %s, %s)", 
                       (title, content, date_posted))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Announcement added successfully!", "success")
        return redirect(url_for('addannounce'))
    return render_template('addannounce.html') 

# Route for adding feedback
@app.route('/add_feedback')
def add_feedback():
    return render_template('add_feedback.html')

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    userid = request.form['userid']
    eventname = request.form['eventname']
    eventdate = request.form['eventdate']
    rating = request.form['rating']
    content = request.form['content']
    conn = get_db_connection()
    cursor = conn.cursor()
    # Check if the event name and date are valid
    cursor.execute("SELECT * FROM Events WHERE event_name = %s AND date_of_conduction = %s", (eventname, eventdate))
    event = cursor.fetchone()
    if event:
        # Event is valid, insert feedback
        cursor.execute("INSERT INTO Event_Feedback (userid, eventname, eventdate, rating, content) VALUES (%s, %s, %s, %s, %s)",
                       (userid, eventname, eventdate, rating, content))
        conn.commit()
        feedback_message = "Feedback submitted successfully."
    else:
        feedback_message = "Invalid event name or date."
    cursor.close()
    conn.close()
    return render_template('add_feedback.html', feedback_message=feedback_message)


@app.route('/view_feedback')
def view_feedback():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT userid, eventname, eventdate, rating, content FROM Event_Feedback")
        feedbacks = cursor.fetchall()
        cursor.close()
        conn.close()
        print(feedbacks)
        if not feedbacks:
            return "<h2>No feedback found</h2>"
        return render_template('view_feedback.html', feedbacks=feedbacks)
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)