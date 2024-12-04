# login.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from datetime import date
import mysql.connector

app = Flask(__name__)
app.secret_key = 'tybca223hari'

# MySQL database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'typroj',
}

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/admin_login', methods=['POST', 'GET'])
def admin_login():
    username = request.form['adminUsername']
    password = request.form['adminPassword']

    conn = None  # Define conn outside try block and set it to None

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM admin_login WHERE admin_username = %s AND password = %s"
        cursor.execute(query, (username, password))
        admin = cursor.fetchone()

        if admin:
            session['admin_username'] = admin['admin_username']  # Set admin username in session
            flash('Login successful', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Wrong credentials. Please try again.', 'error')
            return redirect(url_for('index'))

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash('Error connecting to the database. Please try again later.', 'error')
        return redirect(url_for('index'))

    finally:
        if conn is not None and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/admin_profile')
def admin_profile():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        query = "SELECT admin_username, password FROM admin_login WHERE admin_username = %s"
        cursor.execute(query, (session.get('admin_username'),))  # Use session.get() to avoid KeyError
        admin_profile = cursor.fetchone()

        if admin_profile:
            return render_template('admin_profile.html', admin_profile=admin_profile)
        else:
            flash('Error fetching admin profile.', 'error')
            return redirect(url_for('admin_dashboard'))

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash('Error connecting to the database. Please try again later.', 'error')
        return redirect(url_for('admin_dashboard'))

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            
@app.route('/member_login', methods=['POST', 'GET'])
def member_login():
    username = request.form['memberUsername']
    password = request.form['memberPassword']

    conn = None  # Define conn outside try block and set it to None

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM master_table WHERE member_username = %s AND password = %s"
        cursor.execute(query, (username, password))
        member = cursor.fetchone()

        if member:
            session['member_username'] = member['member_username']
            flash('Login successful', 'success')
            return redirect(url_for('member_dashboard'))
        else:
            flash('Wrong credentials. Please try again.', 'error')
            return redirect(url_for('index'))

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash('Error connecting to the database. Please try again later.', 'error')
        return redirect(url_for('index'))

    finally:
        if conn is not None and conn.is_connected():
            cursor.close()
            conn.close()
            
@app.route('/member_profile')
def member_profile():
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Query to fetch member profile
        profile_query = "SELECT owner_name, wing, flat_number, flat_type, member_username FROM master_table WHERE member_username = %s"
        cursor.execute(profile_query, (session.get('member_username'),))
        member_profile = cursor.fetchone()

        if member_profile:
            # Query to fetch parking slot
            parking_query = "SELECT parking_slot FROM parking_info WHERE wing = %s AND flat_no = %s"
            cursor.execute(parking_query, (member_profile['wing'], member_profile['flat_number']))
            parking_slot = cursor.fetchone()
            member_profile['parking_slot'] = parking_slot['parking_slot'] if parking_slot else 'N/A'

            return render_template('member_profile.html', member_profile=member_profile)
        else:
            flash('Error fetching member profile.', 'error')
            return redirect(url_for('member_dashboard'))

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash('Error connecting to the database. Please try again later.', 'error')
        return redirect(url_for('member_dashboard'))

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()



@app.route('/admin_dashboard')
def admin_dashboard():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Query to fetch total number of flats
        cursor.execute("SELECT COUNT(*) FROM flats")
        total_flats = cursor.fetchone()[0]

        # Query to fetch total number of notices
        cursor.execute("SELECT COUNT(*) FROM notice")
        total_notices = cursor.fetchone()[0]

        # Query to fetch total number of staff
        cursor.execute("SELECT COUNT(*) FROM staff_info")
        total_staff = cursor.fetchone()[0]

        # Query to fetch total number of committee members
        cursor.execute("SELECT COUNT(*) FROM committee_info")
        total_committee = cursor.fetchone()[0]

        # Query to fetch total number of complaints
        cursor.execute("SELECT COUNT(*) FROM complaint")
        total_complaints = cursor.fetchone()[0]

        # Query to fetch total number of owners
        cursor.execute("SELECT COUNT(*) FROM owner_info")
        total_owners = cursor.fetchone()[0]

        # Query to fetch total number of tenants
        cursor.execute("SELECT COUNT(*) FROM tenant_info")
        total_tenants = cursor.fetchone()[0]

        return render_template('admin_dashboard.html', total_flats=total_flats, total_notices=total_notices,
                               total_staff=total_staff, total_committee=total_committee,
                               total_complaints=total_complaints, total_owners=total_owners,
                               total_tenants=total_tenants)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash('Error connecting to the database. Please try again later.', 'error')
        return redirect(url_for('index'))

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# Route for fetching and displaying notices in member dashboard
@app.route('/member_dashboard')
def member_dashboard():
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Fetch notices from the database
        cursor.execute("SELECT id, title, content, date FROM notice")
        notices = cursor.fetchall()

        # Fetch maintenance records from the database
        cursor.execute("SELECT maintenance_id, name, wing, flat_no, status FROM maintenance")
        maintenances = cursor.fetchall()

        # Render member dashboard template with notices and maintenance records
        return render_template('member_dashboard.html', notices=notices, maintenances=maintenances)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash('Error fetching data. Please try again later.', 'error')
        return redirect(url_for('index'))  # Redirect to login page or appropriate route

    finally:
        # Close database connection
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/flat_info', methods=['GET'])
def flat_info():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        query = "SELECT flat_id, wing, floor_no, flat_no, flat_type FROM flats LIMIT %s, %s"
        cursor.execute(query, (offset, per_page))
        flats = cursor.fetchall()

        return render_template('flat_info.html', flats=flats, page=page)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash('Error connecting to the database. Please try again later.', 'error')
        return redirect(url_for('admin_dashboard'))

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/update_flat', methods=['POST'])
def update_flat():
    flat_id = request.form['editFlatId']
    wing = request.form['editWing']
    floor_no = request.form['editFloorNo']
    flat_no = request.form['editFlatNo']
    flat_type = request.form['editFlatType']

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = "UPDATE flats SET wing = %s, floor_no = %s, flat_no = %s, flat_type = %s WHERE flat_id = %s"
        cursor.execute(query, (wing, floor_no, flat_no, flat_type, flat_id))
        conn.commit()

        flash('Flat updated successfully!', 'success')

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash('Error updating flat. Please try again later.', 'error')

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

    return redirect(url_for('flat_info'))

from flask import render_template, request, redirect, url_for, flash
import mysql.connector

#add notice
@app.route('/notice_info', methods=['GET', 'POST'])
def notice_info():
    current_date = datetime.now().strftime('%Y-%m-%d')

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        date = request.form['date']

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            query = "INSERT INTO notice (title, content, date) VALUES (%s, %s, %s)"
            cursor.execute(query, (title, content, date))
            
            conn.commit()

        # Reset auto-increment value
            reset_query = "ALTER TABLE notice AUTO_INCREMENT = 1"
            cursor.execute(reset_query)

            flash('Notice added successfully!', 'success')

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            flash('Error adding notice. Please try again later.', 'error')

        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        query = "SELECT id, title, content, date FROM notice LIMIT %s, %s"
        cursor.execute(query, (offset, per_page))
        notices = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) AS count FROM notice")
        total_count = cursor.fetchone()['count']
        has_next = offset + per_page < total_count

        return render_template('notice_info.html', notices=notices, page=page, has_next=has_next, current_date=current_date)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash('Error fetching notices. Please try again later.', 'error')
        return redirect(url_for('admin_dashboard'))

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/update_notice', methods=['POST'])
def update_notice():
    notice_id = request.form['editNoticeId']
    title = request.form['editTitle']
    content = request.form['editContent']
    date = request.form['editDate']

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = "UPDATE notice SET title = %s, content = %s, date = %s WHERE id = %s"
        cursor.execute(query, (title, content, date, notice_id))
            
        conn.commit()

        # Reset auto-increment value
        reset_query = "ALTER TABLE notice AUTO_INCREMENT = 1"
        cursor.execute(reset_query)
        
        conn.commit()

        flash('Notice updated successfully!', 'success')

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash('Error updating notice. Please try again later.', 'error')

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

    return redirect(url_for('notice_info'))


# Route for deleting notice
@app.route('/delete_notice', methods=['GET'])
def delete_notice():
    notice_id = request.args.get('id')

    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Delete notice from the database
        delete_query = "DELETE FROM notice WHERE id = %s"
        cursor.execute(delete_query, (notice_id,))
        conn.commit()

        # Reset auto-increment value
        reset_query = "ALTER TABLE notice AUTO_INCREMENT = 1"
        cursor.execute(reset_query)
        
        conn.commit()

        flash('Notice deleted successfully!', 'success')

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash('Error deleting notice. Please try again later.', 'error')

    finally:
        # Close database connection
        if conn.is_connected():
            cursor.close()
            conn.close()

    return redirect(url_for('notice_info'))

# Member notice route
@app.route('/member_notice')
def member_notice():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        page = request.args.get('page', 1, type=int)
        per_page = 10
        offset = (page - 1) * per_page

        cursor.execute("SELECT id, title, content, date FROM notice LIMIT %s OFFSET %s", (per_page, offset))
        notices = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) AS count FROM notice")
        total_count = cursor.fetchone()['count']
        has_next = (offset + per_page) < total_count

        return render_template('member_notice.html', notices=notices, page=page, has_next=has_next)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash('Error fetching notices. Please try again later.', 'error')
        return redirect(url_for('index'))

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/admin_password', methods=['GET', 'POST'])
def admin_password():
    if request.method == 'GET':
        # Retrieve the current logged-in username from the session
        admin_username = session.get('admin_username')
        if admin_username:
            return render_template('admin_password.html', admin_username=admin_username)
        else:
            flash('Please log in to change your password.', 'error')
            return redirect(url_for('login'))
    elif request.method == 'POST':
        admin_username = request.form['username']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        # Validate if new password matches the confirm password
        if new_password != confirm_password:
            flash('New password and confirm password do not match.', 'error')
            return redirect(url_for('admin_password'))
        
        # Validate password length
        if len(new_password) > 8:
            flash('Password length should not exceed 8 characters.', 'error')
            return redirect(url_for('admin_password'))
        
        try:
            # Connect to the database
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            
            # Update password in admin_login table
            cursor.execute("UPDATE admin_login SET password = %s WHERE admin_username = %s", (new_password, admin_username))
            conn.commit()
            
            # Close database connection
            cursor.close()
            conn.close()
            
            flash('Password changed successfully!', 'success')
            return redirect(url_for('admin_password'))
        
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            flash('Error changing password. Please try again later.', 'error')
            return redirect(url_for('admin_password'))
        
@app.route('/member_password', methods=['GET', 'POST'])
def member_password():
    if request.method == 'GET':
        # Retrieve the current logged-in username from the session
        member_username = session.get('member_username')
        if member_username:
            return render_template('member_password.html', member_username=member_username)
        else:
            flash('Please log in to change your password.', 'error')
            return redirect(url_for('login'))
    elif request.method == 'POST':
        member_username = request.form['username']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        # Validate if new password matches the confirm password
        if new_password != confirm_password:
            flash('New password and confirm password do not match.', 'error')
            return redirect(url_for('member_password'))
        
        # Validate password length
        if len(new_password) > 8:
            flash('Password length should not exceed 8 characters.', 'error')
            return redirect(url_for('member_password'))
        
        try:
            # Connect to the database
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            
            # Update password in master_table
            cursor.execute("UPDATE master_table SET password = %s WHERE member_username = %s", (new_password, member_username))
            conn.commit()
            
            # Update password in owner_info
            cursor.execute("UPDATE owner_info SET password = %s WHERE member_username = %s", (new_password, member_username))
            conn.commit()
            
            # Close database connection
            cursor.close()
            conn.close()
            
            flash('Password changed successfully!', 'success')
            return redirect(url_for('member_password'))
        
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            flash('Error changing password. Please try again later.', 'error')
            return redirect(url_for('member_password'))
        
@app.route('/owner_form')
def owner_form():
    conn = mysql.connector.connect(**db_config)
    if conn is None:
        flash('Error connecting to the database. Please try again later.', 'error')
        return redirect(url_for('index'))

    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT member_username, password, member_id, owner_name, flat_number, wing FROM master_table WHERE member_username = %s"
        cursor.execute(query, (session['member_username'],))
        data = cursor.fetchone()
        if data:
            return render_template('owner_form.html', existing_data=data)
        else:
            flash('Data not found for the specified username.', 'error')
            return redirect(url_for('index'))
    except mysql.connector.Error as err:
        flash(f'Error fetching data: {err}', 'error')
        return redirect(url_for('index'))
    finally:
        cursor.close()
        conn.close()

@app.route('/submit_owner', methods=['POST'])
def submit_owner():
    conn = mysql.connector.connect(**db_config)
    if conn is None:
        flash('Error connecting to the database. Please try again later.', 'error')
        return redirect(url_for('owner_form'))

    try:
        cursor = conn.cursor()
        # Extract form data
        member_username = request.form['memberUsername']
        password = request.form['password']
        owner_name = request.form['ownerName']
        wing = request.form['wing']
        flat_no = request.form['flatNo']
        contact_no = request.form['contactNo']
        email_id = request.form['email']
        no_adult = request.form['noAdult']
        no_children = request.form['noChildren']
        no_pet = request.form['noPet']
        current_status = request.form['currentStatus']
        alternate_name = request.form['altName']
        alternate_contact_no = request.form['altContactNo']
        alternate_email = request.form['altEmail']
        four_wheelers = request.form['fourWheelers']
        four_wheelers_numberplate = request.form['fourWheelersNumberplate']
        two_wheelers = request.form['twoWheelers']
        two_wheelers_numberplate = request.form['twoWheelersNumberplate']
        
        duplicate_query = "SELECT COUNT(*) FROM owner_info WHERE member_username = %s"
        cursor.execute(duplicate_query, (member_username,))
        count = cursor.fetchone()[0]

        if count > 0:
            flash('Duplicate entry found. Please update the existing record instead.', 'error')
            return render_template('owner_form.html', existing_data=request.form)

        # Insert data into owner_info table
        insert_query = """
                       INSERT INTO owner_info (member_username, password, owner_name, wing, flat_no, contact_no, email_id,
                            no_adult, no_children, no_pet, current_status, alternate_name, alternate_contact_no,
                            alternate_email, four_wheelers, four_wheelers_numberplate, two_wheelers, two_wheelers_numberplate)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
        # Adjusted data tuple with additional password field
        data = (member_username, password, owner_name, wing, flat_no, contact_no, email_id,
               no_adult, no_children, no_pet, current_status, alternate_name, alternate_contact_no,
               alternate_email, four_wheelers, four_wheelers_numberplate, two_wheelers, two_wheelers_numberplate)

        cursor.execute(insert_query, data)
        conn.commit()

        flash('Owner form submitted successfully', 'success')
        # Reset the auto-increment value
        sql_reset_auto_increment = "ALTER TABLE owner_info AUTO_INCREMENT = 1"
        cursor.execute(sql_reset_auto_increment)
        
        return redirect(url_for('member_dashboard'))  # Redirect to member dashboard after successful form submission
    except mysql.connector.Error as err:
        error_message = str(err)  # Convert the error object to a string
        flash(f"Error executing query: {error_message}", 'error')
        flash('Error submitting form. Please try again later.', 'error')
        return render_template('owner_form.html', existing_data=request.form)
    finally:
        cursor.close()
        conn.close()
        
@app.route('/tenant_form')
def tenant_form():
    conn = mysql.connector.connect(**db_config)
    if conn is None:
        flash('Error connecting to the database. Please try again later.', 'error')
        return redirect(url_for('index'))

    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT member_id, member_username, owner_name, flat_number, wing FROM master_table WHERE member_username = %s"
        cursor.execute(query, (session['member_username'],))
        data = cursor.fetchone()
        cursor.close()  # Close the cursor after consuming all the results
        conn.close()
        if data:
            return render_template('tenant_form.html', existing_data=data)
        else:
            flash('Data not found for the specified username.', 'error')
            return redirect(url_for('member_dashboard'))
    except mysql.connector.Error as err:
        flash(f'Error fetching data: {err}', 'error')
        return redirect(url_for('index'))

@app.route('/submit_tenant', methods=['POST'])
def submit_tenant():
    conn = mysql.connector.connect(**db_config)
    if conn is None:
        flash('Error connecting to the database. Please try again later.', 'error')
        return redirect(url_for('tenant_form')) 

    try:
        cursor = conn.cursor()
        # Extract form data
        member_id = request.form['MemberId']
        username = request.form['memberUsername']
        owner_name = request.form['OwnerName']
        wing = request.form['wing']
        flat_no = request.form['flatNo']
        tenant_name = request.form['TenantName']
        tenant_contact = request.form['tenantContact']
        tenant_email = request.form['tenantEmail']
        no_adult = request.form['noAdult']
        no_children = request.form['noChildren']
        no_pet = request.form['noPet']
        
        # Insert data into tenant_info table
        insert_query = """
        INSERT INTO tenant_info (member_id, member_username, owner_name, wing, flat_no, tenant_name, tenant_contact,
                                 tenant_email, no_adult, no_children, no_pet)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        data = (member_id, username, owner_name, wing, flat_no, tenant_name, tenant_contact, tenant_email,
                no_adult, no_children, no_pet)

        cursor.execute(insert_query, data)
        conn.commit()
        
        update_query = """
        UPDATE master_table
        SET tenant_name = %s
        WHERE member_id = %s
        """
        cursor.execute(update_query, (tenant_name, member_id))
        conn.commit()

        flash('Tenant form submitted successfully', 'success')
        
         # Reset the auto-increment value
        sql_reset_auto_increment = "ALTER TABLE tenant_info AUTO_INCREMENT = 1"
        cursor.execute(sql_reset_auto_increment)
        
        return redirect(url_for('member_dashboard'))
    except mysql.connector.Error as err:
        error_message = str(err)  # Convert the error object to a string
        flash(f"Error executing query: {error_message}", 'error')
        flash('Error submitting tenant form. Please try again later.', 'error')
        return redirect(url_for('tenant_form'))
    finally:
        cursor.close()
        conn.close()

# Route to fetch and display owner information
@app.route('/owner_info')
def owner_info():
    try:
        # Retrieve page number from the request arguments or default to 1
        page = int(request.args.get('page', 1))

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Fetch owners for the current page
        per_page = 10  # Set the number of owners per page
        offset = (page - 1) * per_page
        cursor.execute("SELECT * FROM owner_info LIMIT %s OFFSET %s", (per_page, offset))
        owners = cursor.fetchall()
        
        # Fetch total number of owners for pagination
        cursor.execute("SELECT COUNT(*) AS count FROM owner_info")
        total_owners = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        # Calculate pagination parameters
        total_pages = (total_owners + per_page - 1) // per_page
        
        return render_template('owner_info.html', owners=owners, page=page, total_pages=total_pages)
    except mysql.connector.Error as err:
        return f"Error fetching data: {err}"

@app.route('/tenant_info')
def tenant_info():
    try:
        # Retrieve page number from the request arguments or default to 1
        page = int(request.args.get('page', 1))

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Fetch tenants for the current page
        per_page = 10  # Set the number of tenants per page
        offset = (page - 1) * per_page
        cursor.execute("SELECT * FROM tenant_info LIMIT %s OFFSET %s", (per_page, offset))
        tenants = cursor.fetchall()
        
        # Fetch total number of tenants for pagination
        cursor.execute("SELECT COUNT(*) AS count FROM tenant_info")
        total_tenants = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        # Calculate pagination parameters
        total_pages = (total_tenants + per_page - 1) // per_page
        
        return render_template('tenant_info.html', tenants=tenants, page=page, total_pages=total_pages)
    except mysql.connector.Error as err:
        return f"Error fetching data: {err}"
    
@app.route('/maintenance_info', methods=['GET', 'POST'])
def maintenance_info():
    if request.method == 'POST':
        name = request.form['name']
        wing = request.form['wing']
        flat_no = request.form['flat_no']
        status = request.form['status']

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            query = "INSERT INTO maintenance (name, wing, flat_no, status) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (name, wing, flat_no, status))
            conn.commit()

            flash('Maintenance information added successfully!', 'success')
            
         # Reset the auto-increment value
            sql_reset_auto_increment = "ALTER TABLE your_table AUTO_INCREMENT = 1"
            cursor.execute(sql_reset_auto_increment)

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            flash('Error adding maintenance information. Please try again later.', 'error')

        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        query = "SELECT maintenance_id, name, wing, flat_no, status FROM maintenance LIMIT %s, %s"
        cursor.execute(query, (offset, per_page))
        maintenances = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) AS count FROM maintenance")
        total_count = cursor.fetchone()['count']
        has_next = offset + per_page < total_count

        return render_template('maintenance_info.html', maintenances=maintenances, page=page, has_next=has_next)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash('Error fetching maintenance information. Please try again later.', 'error')
        return redirect(url_for('admin_dashboard'))

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/update_maintenance', methods=['POST'])
def update_maintenance():
    maintenance_id = request.form['editMaintenanceId']
    name = request.form['editName']
    wing = request.form['editWing']
    flat_no = request.form['editFlatNo']
    status = request.form['editStatus']

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = "UPDATE maintenance SET name = %s, wing = %s, flat_no = %s, status = %s WHERE maintenance_id = %s"
        cursor.execute(query, (name, wing, flat_no, status, maintenance_id))
        conn.commit()

        flash('Maintenance information updated successfully!', 'success')
        
         # Reset the auto-increment value
        sql_reset_auto_increment = "ALTER TABLE your_table AUTO_INCREMENT = 1"
        cursor.execute(sql_reset_auto_increment)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash('Error updating maintenance information. Please try again later.', 'error')

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

    return redirect(url_for('maintenance_info'))

@app.route('/delete_maintenance', methods=['GET'])
def delete_maintenance():
    maintenance_id = request.args.get('id')

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        delete_query = "DELETE FROM maintenance WHERE maintenance_id = %s"
        cursor.execute(delete_query, (maintenance_id,))
        conn.commit()

        flash('Maintenance information deleted successfully!', 'success')
        
         # Reset the auto-increment value
        sql_reset_auto_increment = "ALTER TABLE your_table AUTO_INCREMENT = 1"
        cursor.execute(sql_reset_auto_increment)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash('Error deleting maintenance information. Please try again later.', 'error')

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

    return redirect(url_for('maintenance_info'))

@app.route('/clubhouse_booking_form', methods=['GET', 'POST'])
def clubhouse_booking_form():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    try:
        if conn is None:
            flash('Error connecting to the database. Please try again later.', 'error')
            return redirect(url_for('index'))

        query = "SELECT member_id, owner_name, flat_number, wing FROM master_table WHERE member_username = %s"
        cursor.execute(query, (session['member_username'],))
        data = cursor.fetchone()
        
        # Fetch booked dates for the current member
        cursor.execute("SELECT booking_date FROM clubhouse_booking_details WHERE member_id = %s", (data['member_id'],))
        booked_dates = [row['booking_date'].strftime('%Y-%m-%d') for row in cursor.fetchall()]

        if data:
            return render_template('clubhouse_booking_form.html', existing_data=data, booked_dates=booked_dates)
        else:
            flash('Data not found for the specified username.', 'error')
            return redirect(url_for('member_dashboard'))

    except mysql.connector.Error as err:
        flash(f'Error fetching data: {err}', 'error')
        return redirect(url_for('index'))

    finally:
        cursor.close()
        conn.close()

@app.route('/submit_booking', methods=['GET','POST'])
def submit_booking():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    try:
        if conn is None:
            flash('Error connecting to the database. Please try again later.', 'error')
            return redirect(url_for('clubhouse_booking_form'))
        if request.method == 'POST':
            # Extract form data
            member_id = request.form.get('MemberId')
            owner_name = request.form.get('OwnerName')
            flat_no = request.form.get('flatNo')
            wing = request.form.get('wing')
            alternate_contact_no = request.form.get('alternate_contact_no')
            booking_date_str = request.form.get('booking_date')
            booking_date = datetime.strptime(booking_date_str, '%Y-%m-%d').date()
            current_date = datetime.now().date()

            # Check if booking date is in the past
            if booking_date < current_date:
                flash('Cannot book for a past date. Please select a future date.', 'error')
                return redirect(url_for('clubhouse_booking_form'))

            cursor.execute("SELECT booking_date FROM clubhouse_booking_details WHERE booking_date = %s", (booking_date,))
            existing_booking = cursor.fetchone()
            if existing_booking:
                flash('This date is already booked. Please select another date.', 'error')
                cursor.fetchall()
                return redirect(url_for('clubhouse_booking_form'))

            # Extract remaining form data
            time = request.form.get('time')
            reason = request.form.get('reason')
            preference = request.form.get('preference')
            payment_type = ', '.join(request.form.getlist('payment_type'))

            # Insert data into clubhouse_booking_details table
            insert_query = """
            INSERT INTO clubhouse_booking_details (member_id, owner_name, flat_no, wing, alternate_contact_no, 
                                                    booking_date, time, reason, preference, payment_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            data = (member_id, owner_name, flat_no, wing, alternate_contact_no, booking_date, time,
                    reason, preference, payment_type)

            cursor.execute(insert_query, data)
            conn.commit()

            flash('Clubhouse booking details submitted successfully', 'success')

    except mysql.connector.Error as err:
        error_message = str(err)
        flash(f"Error executing query: {error_message}", 'error')
        flash('Error submitting clubhouse booking details form. Please try again later.', 'error')

    finally:
        cursor.close()
        conn.close()

    # Redirect to the form page
    return redirect(url_for('clubhouse_booking_form'))
     
@app.route('/clubhouse_report')
def clubhouse_report():
    bookings = []

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Fetch clubhouse booking details
        query = "SELECT * FROM clubhouse_booking_details"
        cursor.execute(query)
        bookings = cursor.fetchall()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash('Error retrieving clubhouse booking details. Please try again later.', 'error')

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

    return render_template('clubhouse_report.html', bookings=bookings)


@app.route('/parking_info', methods=['GET', 'POST'])
def parking_info():
    if request.method == 'POST':
        # Insert parking details into parking_info table
        owner_name = request.form['owner_name']
        flat_no = request.form['flat_no']
        parking_slot = request.form['parking_slot']
        wing = request.form['wing']
        car_number_plate = request.form['car_number_plate']

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # Check for duplicate entry before inserting
            query_check_duplicate = "SELECT * FROM parking_info WHERE owner_name = %s OR parking_slot = %s OR car_number_plate = %s"
            cursor.execute(query_check_duplicate, (owner_name, parking_slot, car_number_plate))
            duplicate_entry = cursor.fetchone()

            # Consume the results of the SELECT query
            cursor.fetchall()

            if duplicate_entry:
                flash('Duplicate entry found. Please check the details and try again.', 'error')
            else:
                query_insert_parking = "INSERT INTO parking_info (owner_name, flat_no, parking_slot, wing, car_number_plate) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(query_insert_parking, (owner_name, flat_no, parking_slot, wing, car_number_plate))
                
                conn.commit()
            
            flash('Parking details added successfully!', 'success')
            
            # Reset the auto-increment value
            sql_reset_auto_increment = "ALTER TABLE parking_info AUTO_INCREMENT = 1"
            cursor.execute(sql_reset_auto_increment)
         
        except mysql.connector.Error as err:
            flash('Error adding parking details. Please try again later.', 'error')

        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    # Retrieve and display parking details
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        query_select_parking = "SELECT parking_id, owner_name, flat_no, parking_slot, wing, car_number_plate FROM parking_info LIMIT %s, %s"
        cursor.execute(query_select_parking, (offset, per_page))
        parking_info = cursor.fetchall()

        return render_template('parking_info.html', parking_info=parking_info, page=page)

    except mysql.connector.Error as err:
        flash('Error connecting to the database. Please try again later.', 'error')
        return redirect(url_for('admin_dashboard'))

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/update_parking', methods=['POST'])
def update_parking():
    parking_id = request.form['editParkingId']
    owner_name = request.form['editOwnerName']
    flat_no = request.form['editFlatNo']
    parking_slot = request.form['editParkingSlot']
    wing = request.form['editWing']
    car_number_plate = request.form['editCarNumberPlate']

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Check for duplicate entry
        query = "SELECT * FROM parking_info WHERE (owner_name = %s OR parking_slot = %s OR car_number_plate = %s) AND parking_id != %s"
        cursor.execute(query, (owner_name, parking_slot, car_number_plate, parking_id))
        duplicate_entry = cursor.fetchone()

        if duplicate_entry:
            flash('Duplicate entry found. Please check the details and try again.', 'error')
        else:
            # Update parking information
            query = "UPDATE parking_info SET owner_name = %s, flat_no = %s, parking_slot = %s, wing = %s, car_number_plate = %s WHERE parking_id = %s"
            cursor.execute(query, (owner_name, flat_no, parking_slot, wing, car_number_plate, parking_id))
            conn.commit()

        flash('Parking information updated successfully!', 'success')
        
        # Reset the auto-increment value
        sql_reset_auto_increment = "ALTER TABLE parking_info AUTO_INCREMENT = 1"
        cursor.execute(sql_reset_auto_increment)
            

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash('Error updating parking information. Please try again later.', 'error')

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

    return redirect(url_for('parking_info'))

@app.route('/complaint')
def complaint():
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Fetch complaints data
        cursor.execute("SELECT * FROM complaint")
        complaints = cursor.fetchall()

        # Close database connection
        cursor.close()
        conn.close()

        return render_template('complaint.html', complaints=complaints)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash('Error fetching complaints data. Please try again later.', 'error')
        return redirect(url_for('index'))

@app.route('/admin_update_complaint', methods=['POST'])
def admin_update_complaint():
    try:
        complaint_id = request.form['complaint_id']
        status = request.form['status']
        resolved_date = request.form['resolved_date']

        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Update complaint status and resolved date
        cursor.execute("UPDATE complaint SET status = %s, resolved_date = %s WHERE complaint_id = %s", (status, resolved_date, complaint_id))
        conn.commit()

        # Close database connection
        cursor.close()
        conn.close()

        flash('Complaint status updated successfully!', 'success')
        
        # Reset the auto-increment value
        sql_reset_auto_increment = "ALTER TABLE complaint AUTO_INCREMENT = 1"
        cursor.execute(sql_reset_auto_increment)
            
        return redirect(url_for('complaint'))

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash('Error updating complaint status. Please try again later.', 'error')
        return redirect(url_for('complaint'))
    
@app.route('/member_complaint_form', methods=['GET','POST'])
def member_complaint_form():
    if request.method == 'GET':
    # Retrieve the username from the session
     username = session.get('member_username')
    if username:
        try:
            # Connect to the database
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)

            # Fetch complaint data
            cursor.execute("SELECT * FROM complaint")
            complaints = cursor.fetchall()

            # Close database connection
            cursor.close()
            conn.close()

            current_date = date.today().isoformat()  # Get today's date in ISO format (YYYY-MM-DD)
            return render_template('member_complaint_form.html', username=username, current_date=current_date, complaints=complaints)
        
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            flash('Error fetching complaint data. Please try again later.', 'error')
            return redirect(url_for('member_dashboard'))
    
    else:
        # Redirect to the login page if the user is not logged in
        return redirect(url_for('admin_login'))

@app.route('/submit_complaint', methods=['POST'])
def submit_complaint():
    if request.method == 'POST':
        try:
            wing = request.form['wing']
            flat_no = request.form['flat_no']
            date_of_complaint = request.form['date_of_complaint']
            reason = request.form['reason']
            status = 'Pending'  # Initial status when submitting complaint
            
            # Validate the date to ensure it is the current date
            current_date = date.today().isoformat()  # Get today's date in ISO format (YYYY-MM-DD)
            if date_of_complaint != current_date:
                flash('Invalid complaint date. Please select the current date.', 'error')
                return redirect(url_for('member_complaint_form'))            

            # Connect to the database
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # Insert complaint into the database
            cursor.execute("INSERT INTO complaint (wing, flat_no, date_of_complaint, reason, status) VALUES (%s, %s, %s, %s, %s)",
                           (wing, flat_no, date_of_complaint, reason, status))
            conn.commit()

            # Reset the auto-increment value
            cursor.execute("ALTER TABLE complaint AUTO_INCREMENT = 1")
            
            # Close database connection
            cursor.close()
            conn.close()

            flash('Complaint submitted successfully!', 'success')
            return redirect(url_for('member_complaint_form'))

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            flash('Error submitting complaint. Please try again later.', 'error')
            return redirect(url_for('member_complaint_form'))

@app.route('/update_complaint', methods=['POST'])
def update_complaint():
    if request.method == 'POST':
        try:
            complaint_id = request.form['editComplaintId']
            status = request.form['editStatus']
            resolved_date = datetime.now().date() if status == 'Resolved' else None

            # Connect to the database
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # Update complaint status and resolved date
            cursor.execute("UPDATE complaint SET status = %s, resolved_date = %s WHERE complaint_id = %s", (status, resolved_date, complaint_id))
            conn.commit()

            # Reset the auto-increment value
            cursor.execute("ALTER TABLE complaint AUTO_INCREMENT = 1")
            
            # Close database connection
            cursor.close()
            conn.close()

            flash('Complaint status updated successfully!', 'success')
            return redirect(url_for('committee_info'))

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            flash('Error updating complaint status. Please try again later.', 'error')
            return redirect(url_for('committee_info'))
        
# Function to calculate duration
def calculate_duration(start, end):
    if end:
        start_date = datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.strptime(end, '%Y-%m-%d')
        duration = end_date - start_date
        return f"{duration.days} days / {duration.days // 30} months / {duration.days // 365} years"
    else:
        return "Currently Working"


@app.route('/staff_info', methods=['GET', 'POST'])
def staff_info():
    if request.method == 'POST':
        name = request.form['staffName']
        work = request.form['staffWork']
        contact = request.form['staffContact']
        address = request.form['staffAddress']
        start = request.form['staffStartDate']
        end = request.form['staffEndDate']
        duration = calculate_duration(start, end)

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            query = "INSERT INTO staff_info (name, work, contact, address, start, end, duration) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (name, work, contact, address, start, end, duration))
            conn.commit()

            flash('Staff member added successfully!', 'success')
            
            # Reset the auto-increment value
            sql_reset_auto_increment = "ALTER TABLE staff_info AUTO_INCREMENT = 1"
            cursor.execute(sql_reset_auto_increment)
            

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            flash('Error adding staff member. Please try again later.', 'error')

        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM staff_info LIMIT %s, %s"
        cursor.execute(query, (offset, per_page))
        staff_members = cursor.fetchall()

        return render_template('staff_info.html', staff_members=staff_members, page=page)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash('Error connecting to the database. Please try again later.', 'error')
        return redirect(url_for('admin_dashboard'))

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Route for updating staff information
@app.route('/update_staff', methods=['POST'])
def update_staff():
    if request.method == 'POST':
        staff_id = request.form['editStaffId']
        name = request.form['editStaffName']
        work = request.form['editStaffWork']
        contact = request.form['editStaffContact']
        address = request.form['editStaffAddress']
        start = request.form['editStaffStartDate']
        end = request.form['editStaffEndDate']
        duration = calculate_duration(start, end)

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            query = "UPDATE staff_info SET name=%s, work=%s, contact=%s, address=%s, start=%s, end=%s, duration=%s WHERE id=%s"
            cursor.execute(query, (name, work, contact, address, start, end, duration, staff_id))
            conn.commit()

            flash('Staff member updated successfully!', 'success')
            
            # Reset the auto-increment value
            sql_reset_auto_increment = "ALTER TABLE staff_info AUTO_INCREMENT = 1"
            cursor.execute(sql_reset_auto_increment)
            

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            flash('Error updating staff member. Please try again later.', 'error')

        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    return redirect(url_for('staff_info'))

@app.route('/staff_report', methods=['GET', 'POST'])
def staff_report():
    staff_members = []

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Fetch all staff members ordered by id in descending order (latest first)
        query_all_staff = "SELECT * FROM staff_info ORDER BY id DESC"
        cursor.execute(query_all_staff)
        staff_members = cursor.fetchall()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash('Error retrieving staff information. Please try again later.', 'error')

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

    return render_template('staff_report.html', staff_members=staff_members)


# Route for managing committee information
@app.route('/committee_info', methods=['GET', 'POST'])
def committee_info():
    if request.method == 'POST':
        name = request.form['name']
        position = request.form['position']
        contact = request.form['contact']
        wing = request.form['wing']
        flat_no = request.form['flat_no']
        joined = request.form['joined']
        resigned = request.form['resigned']
        duration = calculate_duration(joined, resigned)

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            query = "INSERT INTO committee_info (name, position, contact, wing, flat_no, joined, resigned, duration) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (name, position, contact, wing, flat_no, joined, resigned, duration))
            conn.commit()

            flash('Committee member added successfully!', 'success')
            
            # Reset the auto-increment value
            sql_reset_auto_increment = "ALTER TABLE committee_info AUTO_INCREMENT = 1"
            cursor.execute(sql_reset_auto_increment)
            
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            flash('Error adding committee member. Please try again later.', 'error')

        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM committee_info LIMIT %s, %s"
        cursor.execute(query, (offset, per_page))
        committee_members = cursor.fetchall()

        return render_template('committee_info.html', committee_members=committee_members, page=page)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash('Error connecting to the database. Please try again later.', 'error')
        return redirect(url_for('admin_dashboard'))  # Update this route with your actual route

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Route for updating committee information
@app.route('/update_committee', methods=['POST'])
def update_committee():
    if request.method == 'POST':
        committee_id = request.form['editCommitteeId']
        name = request.form['editName']
        position = request.form['editPosition']
        contact = request.form['editContact']
        wing = request.form['editWing']
        flat_no = request.form['editFlatNo']
        joined = request.form['editJoined']
        resigned = request.form['editResigned']
        duration = calculate_duration(joined, resigned)

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            query = "UPDATE committee_info SET name=%s, position=%s, contact=%s, wing=%s, flat_no=%s, joined=%s, resigned=%s, duration=%s WHERE committee_id=%s"
            cursor.execute(query, (name, position, contact, wing, flat_no, joined, resigned, duration, committee_id))
            conn.commit()

            flash('Committee member updated successfully!', 'success')
            
            # Reset the auto-increment value
            sql_reset_auto_increment = "ALTER TABLE committee_info AUTO_INCREMENT = 1"
            cursor.execute(sql_reset_auto_increment)
            

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            flash('Error updating committee member. Please try again later.', 'error')

        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

        return redirect(url_for('committee_info'))

def calculate_duration(joined, resigned):
    if resigned:
        joined_date = datetime.strptime(joined, '%Y-%m-%d')
        resigned_date = datetime.strptime(resigned, '%Y-%m-%d')
        duration_days = (resigned_date - joined_date).days
        duration_months = duration_days // 30
        duration_years = duration_days // 365
        return f"{duration_days} days / {duration_months} months / {duration_years} years"
    else:
        return "Currently Active"
    
@app.route('/committee_report', methods=['GET', 'POST'])
def committee_report():
    if request.method == 'POST':
        if 'show_past_members' in request.form:
            show_past_members = True
        elif 'hide_past_members' in request.form:
            show_past_members = False
    else:
        show_past_members = False

    active_members = []
    inactive_members = []

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Fetch active members
        query_active = "SELECT * FROM committee_info WHERE duration = 'Currently Active'"
        cursor.execute(query_active)
        active_members = cursor.fetchall()

        # Fetch inactive members if requested
        if show_past_members:
            query_inactive = "SELECT * FROM committee_info WHERE resigned IS NOT NULL"
            cursor.execute(query_inactive)
            inactive_members = cursor.fetchall()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash('Error retrieving committee information. Please try again later.', 'error')

    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conn' in locals() and conn is not None and conn.is_connected():
            conn.close()

    return render_template('committee_report.html', active_members=active_members, inactive_members=inactive_members, show_past_members=show_past_members)


if __name__ == '__main__':
    app.run(debug=True)

