from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, time
import pymysql

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

# Models
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100))
    position = db.Column(db.String(100))
    hire_date = db.Column(db.Date)
    contact = db.Column(db.String(100))
    status = db.Column(db.Enum('Active', 'Inactive'), default='Active')
    attendances = db.relationship('Attendance', backref='employee', lazy=True)
    leave_requests = db.relationship('LeaveRequest', backref='employee', lazy=True)
    assigned_items = db.relationship('Inventory', backref='employee', lazy=True)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    date = db.Column(db.Date, nullable=False)
    check_in = db.Column(db.Time)
    check_out = db.Column(db.Time)
    hours_worked = db.Column(db.Numeric(5,2))
    logged_by = db.Column(db.String(100))

class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    leave_type = db.Column(db.Enum('Annual', 'Sick', 'Emergency'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.Enum('Pending', 'Approved', 'Rejected'), default='Pending')
    applied_on = db.Column(db.DateTime, default=datetime.utcnow)

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    item_type = db.Column(db.Enum('Uniform', 'Radio', 'Boots', 'Other'), nullable=False)
    serial_number = db.Column(db.String(100), unique=True)
    assigned_to = db.Column(db.Integer, db.ForeignKey('employee.id'))
    date_assigned = db.Column(db.Date)
    condition = db.Column(db.Enum('New', 'Good', 'Fair', 'Poor'), default='New')

# Helper function to generate employee_id
def generate_employee_id():
    last_emp = Employee.query.order_by(Employee.id.desc()).first()
    if last_emp:
        num = int(last_emp.employee_id[3:]) + 1
    else:
        num = 1
    return f"EMP{num:03d}"

# Routes
@app.route('/')
def dashboard():
    total_employees = Employee.query.count()
    pending_leaves = LeaveRequest.query.filter_by(status='Pending').count()
    return render_template('dashboard.html', total_employees=total_employees, pending_leaves=pending_leaves)

@app.route('/employees', methods=['GET', 'POST'])
def employees():
    if request.method == 'POST':
        employee_id = generate_employee_id()
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        department = request.form['department']
        position = request.form['position']
        hire_date = datetime.strptime(request.form['hire_date'], '%Y-%m-%d').date() if request.form['hire_date'] else None
        contact = request.form['contact']
        status = request.form['status']
        emp = Employee(employee_id=employee_id, first_name=first_name, last_name=last_name,
                       department=department, position=position, hire_date=hire_date,
                       contact=contact, status=status)
        db.session.add(emp)
        db.session.commit()
        return redirect(url_for('employees'))
    employees = Employee.query.all()
    return render_template('employees.html', employees=employees)

@app.route('/employee/<int:id>')
def employee_detail(id):
    emp = Employee.query.get_or_404(id)
    assigned_items = Inventory.query.filter_by(assigned_to=id).all()
    attendance_history = Attendance.query.filter_by(employee_id=id).order_by(Attendance.date.desc()).limit(10).all()
    return render_template('employee_detail.html', employee=emp, items=assigned_items, attendance=attendance_history)

@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if request.method == 'POST':
        employee_id = request.form['employee_id']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        check_in = datetime.strptime(request.form['check_in'], '%H:%M').time() if request.form['check_in'] else None
        check_out = datetime.strptime(request.form['check_out'], '%H:%M').time() if request.form['check_out'] else None
        logged_by = request.form['logged_by']
        hours_worked = None
        if check_in and check_out:
            from datetime import datetime, timedelta
            check_in_dt = datetime.combine(date, check_in)
            check_out_dt = datetime.combine(date, check_out)
            if check_out_dt > check_in_dt:
                hours_worked = (check_out_dt - check_in_dt).total_seconds() / 3600
        att = Attendance(employee_id=employee_id, date=date, check_in=check_in,
                         check_out=check_out, hours_worked=hours_worked, logged_by=logged_by)
        db.session.add(att)
        db.session.commit()
        return redirect(url_for('attendance'))
    employees = Employee.query.all()
    records = Attendance.query.order_by(Attendance.date.desc()).all()
    return render_template('attendance.html', employees=employees, records=records)

@app.route('/leave', methods=['GET', 'POST'])
def leave():
    if request.method == 'POST':
        if 'submit_request' in request.form:
            employee_id = request.form['employee_id']
            leave_type = request.form['leave_type']
            start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
            reason = request.form['reason']
            leave_req = LeaveRequest(employee_id=employee_id, leave_type=leave_type,
                                     start_date=start_date, end_date=end_date, reason=reason)
            db.session.add(leave_req)
            db.session.commit()
            return redirect(url_for('leave'))
        elif 'update_status' in request.form:
            leave_id = request.form['leave_id']
            status = request.form['status']
            leave_req = LeaveRequest.query.get(leave_id)
            if leave_req:
                leave_req.status = status
                db.session.commit()
            return redirect(url_for('leave'))
    employees = Employee.query.all()
    requests = LeaveRequest.query.order_by(LeaveRequest.applied_on.desc()).all()
    return render_template('leave.html', employees=employees, requests=requests)

@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    if request.method == 'POST':
        if 'add_item' in request.form:
            item_name = request.form['item_name']
            item_type = request.form['item_type']
            serial_number = request.form['serial_number']
            condition = request.form['condition']
            item = Inventory(item_name=item_name, item_type=item_type,
                             serial_number=serial_number, condition=condition)
            db.session.add(item)
            db.session.commit()
            return redirect(url_for('inventory'))
        elif 'assign_item' in request.form:
            item_id = request.form['item_id']
            assigned_to = request.form['assigned_to']
            date_assigned = datetime.strptime(request.form['date_assigned'], '%Y-%m-%d').date() if request.form['date_assigned'] else None
            item = Inventory.query.get(item_id)
            if item:
                item.assigned_to = assigned_to
                item.date_assigned = date_assigned
                db.session.commit()
            return redirect(url_for('inventory'))
    items = Inventory.query.all()
    employees = Employee.query.all()
    return render_template('inventory.html', items=items, employees=employees)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5007)