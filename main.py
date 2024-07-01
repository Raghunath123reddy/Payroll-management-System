import datetime
import re

from bson import ObjectId
from flask import Flask, request, session, render_template, redirect, app
import pymongo
my_client = pymongo.MongoClient("mongodb://localhost:27017")
my_database = my_client["salary"]
admin_collection = my_database["admin"]
supervisors_collection = my_database["supervisors"]
employee_collection = my_database["employees"]
departments_collection = my_database["departments"]
leaves_collection = my_database["leaves"]
contract_collection = my_database["contract"]
transactions_collection = my_database["transactions"]
pay_check_collection = my_database["pay_check"]

app = Flask(__name__)
app.secret_key = "mojesh"

query = {}
count = admin_collection.count_documents(query)
if count == 0:
    query = {"username": 'admin', "password": 'admin'}
    admin_collection.insert_one(query)



@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin_login")
def admin_login():
    return render_template("admin_login.html")


@app.route("/admin_login_action", methods=['post'])
def admin_login_action():
    username = request.form.get("username")
    password = request.form.get("password")
    query = {"username": username, "password": password}
    count = admin_collection.count_documents(query)
    if count > 0:
        admin = admin_collection.find_one(query)
        session["admin_id"] = str(admin["_id"])
        session["role"] = 'admin'
        return redirect("/admin_home")
    else:
        return render_template("message.html", message="Invalid Login Details")


@app.route("/admin_home")
def admin_home():
    return render_template("admin_home.html")


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/supervisor_login")
def supervisor_login():
    return render_template("supervisor_login.html")


@app.route("/supervisor_login_action",methods=['post'])
def supervisor_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    query = {"email": email, "password": password}
    count = supervisors_collection.count_documents(query)
    if count > 0:
        supervisor = supervisors_collection.find_one(query)
        if supervisor['is_logged']:
            session["supervisor_id"] = str(supervisor['_id'])
            session['role'] = 'supervisor'
            return redirect("/supervisor_home")
        else:
            return render_template("change_password.html", supervisor_id=supervisor['_id'])
    else:
        return render_template("message.html", message="invalid login details")

@app.route("/change_password_action", methods=['post'])
def change_password_action():
    supervisor_id = request.form.get("supervisor_id")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")
    if password != confirm_password:
        return render_template("message.html", message="password and confirm_password should be same")
    query1 = {"_id":ObjectId(supervisor_id)}
    query2 = {"$set":{"password":password, "is_logged": True}}
    supervisor = supervisors_collection.update_one(query1,query2)
    supervisor = supervisors_collection.find_one(query1)
    session['supervisor_id'] = str(supervisor['_id'])
    session['role'] = "supervisor"
    return redirect("/supervisor_home")


@app.route("/supervisor_home")
def supervisor_home():
    return render_template("supervisor_home.html")



@app.route("/employee_login")
def employee_login():
    return render_template("employee_login.html")


@app.route("/employee_login_action", methods=['post'])
def employee_login_action():
    username = request.form.get("username")
    password = request.form.get("password")
    query = {"username": username, "password": password}
    count = employee_collection.count_documents(query)
    if count > 0:
        employee = employee_collection.find_one(query)
        if employee['is_logged']:
            session["employee_id"] = str(employee['_id'])
            session['role'] = 'employee'
            return redirect("/employee_home")
        else:
            return render_template("change_password2.html", employee_id=employee['_id'])
    else:
        return render_template("message.html", message="invalid login details")


@app.route("/change_password2_action", methods=['post'])
def change_password2_action():
    employee_id = request.form.get("employee_id")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")
    if password != confirm_password:
        return render_template("message.html", message="password and confirm_password should be same")
    query1 = {"_id":ObjectId(employee_id)}
    query2 = {"$set":{"password":password, "is_logged": True}}
    employee = employee_collection.update_one(query1,query2)
    employee = employee_collection.find_one(query1)
    session['employee_id'] = str(employee['_id'])
    session['role'] = "employee"
    return redirect("/employee_home")



@app.route("/employee_home")
def employee_home():
    return render_template("employee_home.html")



@app.route("/departments")
def departments():
    message = request.args.get("message")
    if message == None:
        message =""
    query={}
    departments = departments_collection.find(query)
    departments = list(departments)
    return render_template("departments.html", departments=departments,message=message)


@app.route("/departments_action", methods=['post'])
def departments_action():
    department_name = request.form.get("department_name")
    query = {"department_name": department_name}
    count = departments_collection.count_documents(query)
    if count == 0:
        departments_collection.insert_one(query)
        return redirect("departments?message=departments added successfully")
    else:
        return redirect("departments? message=departments already exits")


@app.route("/edit_department")
def edit_department():
    department_id = request.args.get("department_id")
    query = {"_id": ObjectId(department_id)}
    department = departments_collection.find_one(query)
    return render_template("edit_department.html", department=department)


@app.route("/edit_departments_action", methods=['post'])
def edit_departments_action():
    department_id = request.form.get("department_id")
    department_name = request.form.get("department_name")
    query1 = {'_id': ObjectId(department_id)}
    query2 = {"$set":{"department_name":department_name}}
    departments_collection.update_one(query1,query2)
    return redirect("departments")




@app.route("/supervisor")
def supervisor():
    message = request.args.get("message")
    departments = departments_collection.find({})
    departments = list(departments)
    department_id = request.args.get("department_id")
    if department_id == None:
        department_id = ""
    if department_id == "":
        supervisors = supervisors_collection.find({})
    else:
        query = {"department_id": ObjectId(department_id)}
        supervisors = supervisors_collection.find(query)
    supervisors = list(supervisors)
    print(supervisor)
    return render_template("supervisor.html", departments=departments, supervisors=supervisors, department_id=department_id, message=message, get_departments_by_department_id=get_departments_by_department_id, str=str)

@app.route("/add_supervisor_action",methods=['post'])
def add_supervisor_action():
    name = request.form.get("name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    password2 = request.form.get("password2")
    if password!=password2:
        return render_template("message2.html", message="Password and Confirm Password Did not match")
    zipcode = request.form.get("zipcode")
    state = request.form.get("state")
    city = request.form.get("city")
    experience = request.form.get("experience")
    department_id = request.form.get("department_id")
    print("***"+ str(department_id))
    query = {"email": email, "phone": phone}
    count = supervisors_collection.count_documents(query)
    if count == 0:
        query = {"department_id": ObjectId(department_id), "name": name, "last_name":last_name, "email": email, "phone": phone, "password": password,"password2":password2, "city": city,"state":state,"zipcode":zipcode, "experience": experience, "is_logged": False}
        supervisors_collection.insert_one(query)
        return redirect("supervisor?message=supervisor added successfully")
    else:
        return redirect("supervisor?message=supervisor already exits")


def get_departments_by_department_id(department_id):
    query = {"_id": department_id}
    department = departments_collection.find_one(query)
    return department






@app.route("/employee")
def employee():
    keyword = request.args.get("keyword")
    if session["role"] == "admin":
        if keyword == None:
            keyword = ""
        if keyword == "":
            query = {}
        else:
            keyword2 = re.compile(".*"+str(keyword)+".*", re.IGNORECASE)
            query = {"$or": [{"name": keyword2}, {"email": keyword2}, {"employee_id": keyword2}, {"phone": keyword}]}
    elif session["role"] == "supervisor":
        supervisor_id = session["supervisor_id"]
        if keyword == None:
            keyword = ""
        if keyword == "":
            query = {"supervisor_id": ObjectId(supervisor_id)}
        else:
            keyword2 = re.compile(".*"+str(keyword)+".*", re.IGNORECASE)
            query = {"$or": [{"name": keyword2, "supervisor_id": ObjectId(supervisor_id)}, {"email": keyword2, "supervisor_id": ObjectId(supervisor_id)}, {"employee_id": keyword2, "supervisor_id": ObjectId(supervisor_id)}, {"phone": keyword, "supervisor_id": ObjectId(supervisor_id)}]}
    employees = employee_collection.find(query)
    employees = list(employees)
    print(employees)
    return render_template("employee.html", employees=employees, keyword=keyword, get_contract_by_employee_id=get_contract_by_employee_id, get_supervisor_by_supervisor_id=get_supervisor_by_supervisor_id)



@app.route("/employee_action",methods=['post'])
def employee_action():
    employee_id = request.form.get("employee_id")
    name = request.form.get("name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    gender = request.form.get("gender")
    phone = request.form.get("phone")
    password = request.form.get("password")
    password2 = request.form.get("password2")
    if password!=password2:
        return render_template("message2.html", message="Password and Confirm Password Did not match")
    city = request.form.get("city")
    state = request.form.get("state")
    zipcode = request.form.get("zipcode")
    role = request.form.get("role")
    wage_type = request.form.get("wage_type")
    joining_date = request.form.get("joining_date")
    joining_date = datetime.datetime.strptime(joining_date, "%Y-%m-%d")
    supervisor_id = session["supervisor_id"]
    query = {"email": email}
    print(query)
    count = employee_collection.count_documents(query)
    if count > 0:
        return redirect("employee?message=email already exits")
    query = {"employee_id": employee_id}
    print(query)
    count = employee_collection.count_documents(query)
    if count > 0:
        return redirect("employee?message=employee_id already assigned")
    query = {"supervisor_id": ObjectId(supervisor_id), "name": name,"last_name":last_name, "email": email,"phone": phone, "password": password,"password2": password2, "city":city, "state": state,"zipcode":zipcode, "gender": gender, "role": role,"wage_type": wage_type, "joining_date": joining_date, "employee_id": employee_id, "is_logged": False}
    employee_collection.insert_one(query)
    return redirect("employee?message=employee added successfully")


def get_contract_by_employee_id(employee_id):
    query = {"employee_id" : employee_id}
    print(query)
    contract = contract_collection.find_one(query)
    return contract

def get_supervisor_by_supervisor_id(supervisor_id):
    query = {"_id" : supervisor_id}
    supervisor = supervisors_collection.find_one(query)
    return supervisor




@app.route("/add_contract")
def add_contract():
    employee_id = request.args.get("employee_id")
    query = {"_id": ObjectId(employee_id)}
    employee = employee_collection.find_one(query)
    return render_template("add_contract.html", employee_id=employee_id, employee=employee)

@app.route("/add_contract_action",methods=['post'])
def add_contract_action():
    employee_id = request.form.get("employee_id")
    pay_per_hour = request.form.get("pay_per_hour")
    over_time_pay_per_hour = request.form.get("over_time_pay_per_hour")
    food_allows = request.form.get("food_allows")
    travelling_allows = request.form.get("travelling_allows")
    house_rent_allows = request.form.get("house_rent_allows")
    health_insurance = request.form.get("health_insurance")
    state_tax = request.form.get("state_tax")
    monthly_salary = request.form.get("monthly_salary")
    income_tax = request.form.get("income_tax")
    query = {"employee_id": ObjectId(employee_id), "pay_per_hour": pay_per_hour, "over_time_pay_per_hour": over_time_pay_per_hour, "food_allows": food_allows, "travelling_allows": travelling_allows, "house_rent_allows": house_rent_allows, "health_insurance": health_insurance, "state_tax": state_tax, "monthly_salary": monthly_salary, "income_tax": income_tax}
    print(query)
    contract_collection.insert_one(query)
    return redirect("/employee")

@app.route("/transactions")
def transactions():
    employee_id = request.args.get("employee_id")
    if session['role'] == 'employee':
        employee_id = session['employee_id']
    query = {"employee_id": ObjectId(employee_id)}
    transactions = transactions_collection.find(query)
    transactions = list(transactions)
    transactions.reverse()
    print(transactions)
    return render_template("transactions.html",employee_id=employee_id, transactions=transactions, datetime=datetime)
@app.route("/clock_in")
def clock_in():
    month = datetime.datetime.now().strftime("%h")
    year = datetime.datetime.now().strftime("%Y")
    month_year = str(month) + "-" + str(year)
    query = {"employee_id": ObjectId(session['employee_id']), "clock_in_date_time": datetime.datetime.now(),
             "attendance_date": datetime.datetime.now().strftime("%d-%m-%Y"), "date": datetime.datetime.now(), "number_of_days": 1, "month_year": month_year}
    transactions_collection.insert_one(query)
    return redirect("transactions")

@app.route("/transactions_action", methods=['post'])
def transactions_action():
    clock_in_date_time = request.form.get("clock_in_date_time")
    clock_in_date_time = datetime.datetime.strptime(clock_in_date_time, "%Y-%m-%dT%H:%M")
    clock_out_date_time = request.form.get("clock_out_date_time")
    clock_out_date_time = datetime.datetime.strptime(clock_out_date_time, "%Y-%m-%dT%H:%M")
    diff = clock_out_date_time - clock_in_date_time
    seconds = diff.seconds
    total_hours = seconds/3600
    total_hours =int(total_hours)
    month = clock_in_date_time.strftime("%h")
    year = clock_in_date_time.strftime("%Y")
    month_year = str(month)+"-"+str(year)
    over_time = request.form.get("over_time")
    date = clock_in_date_time.strftime("%Y-%m-%d")
    date = datetime.datetime.strptime(date, "%Y-%m-%d")
    employee_id = request.form.get("employee_id")
    if session['role'] == 'employee':
        employee_id = session['employee_id']
    attendance_date = clock_in_date_time.strftime("%d-%m-%Y")
    query = {"$or":[
            {"clock_in_date_time": {"$gte": clock_in_date_time, "$lte": clock_out_date_time}, "clock_out_date_time":{"$gte": clock_in_date_time, "$gte":clock_out_date_time}, "employee_id": ObjectId(employee_id)},
        {"clock_in_date_time": {"$lte": clock_in_date_time, "$lte": clock_out_date_time},"clock_out_date_time": {"$lte": clock_in_date_time, "$gte": clock_out_date_time},"employee_id": ObjectId(employee_id)},
        {"clock_in_date_time": {"$lte": clock_in_date_time, "$lte": clock_out_date_time},"clock_out_date_time": {"$gte": clock_in_date_time, "$gte": clock_out_date_time},"employee_id": ObjectId(employee_id)},
        {"clock_in_date_time": {"$gte": clock_in_date_time, "$lte": clock_out_date_time},"clock_out_date_time": {"$gte": clock_in_date_time, "$lte": clock_out_date_time},"employee_id": ObjectId(employee_id)}
    ]}
    count = transactions_collection.count_documents(query)
    if count == 0:
        status = ['Cancelled', 'Rejected', 'Applied']
        query = {"$or": [
            {"start_date": {"$gte": clock_in_date_time, "$lte": clock_out_date_time},
             "end_date": {"$gte": clock_in_date_time, "$gte": clock_out_date_time},
             "employee_id": ObjectId(employee_id), "status": {"$nin": status}},
            {"start_date": {"$lte": clock_in_date_time, "$lte": clock_out_date_time},
             "end_date": {"$lte": clock_in_date_time, "$gte": clock_out_date_time},
             "employee_id": ObjectId(employee_id), "status": {"$nin": status}},
            {"start_date": {"$lte": clock_in_date_time, "$lte": clock_out_date_time},
             "end_date": {"$gte": clock_in_date_time, "$gte": clock_out_date_time},
             "employee_id": ObjectId(employee_id), "status": {"$nin": status}},
            {"start_date": {"$gte": clock_in_date_time, "$lte": clock_out_date_time},
             "end_date": {"$gte": clock_in_date_time, "$lte": clock_out_date_time},
             "employee_id": ObjectId(employee_id), "status": {"$nin": status}}
        ]}
        count = leaves_collection.count_documents(query)
        if count > 0:
            return redirect("leaves?message=Employee On Leave, You can not add Transaction")
        transaction_id = request.form.get("transaction_id")
        if transaction_id !=None:
            query1 = {"_id": ObjectId(transaction_id)}
            query2 = {"$set": {"employee_id": ObjectId(employee_id), "clock_in_date_time": clock_in_date_time,"attendance_date":attendance_date, "clock_out_date_time": clock_out_date_time,"total_hours": total_hours, "over_time": over_time, "date": date, "number_of_days": 1, "month_year": month_year}}
            transactions_collection.update_one(query1, query2)
        else:
            query = {"employee_id": ObjectId(employee_id), "clock_in_date_time": clock_in_date_time,"attendance_date":attendance_date, "clock_out_date_time": clock_out_date_time,"total_hours": total_hours, "over_time": over_time, "date": date, "number_of_days": 1, "month_year": month_year}
            transactions_collection.insert_one(query)
        return redirect("/transactions?employee_id="+str(employee_id))
    else:
        return render_template("smessage.html",message="transactions already added")


@app.route("/leaves")
def leaves():
    if session['role'] == 'employee':
        employee_id = session['employee_id']
        query = {"employee_id": ObjectId(employee_id)}
    elif session['role'] =='admin':
        employee_id = request.args.get("employee_id")
        if employee_id == None:
            query = {}
        else:
            query = {"employee_id": ObjectId(employee_id)}
    elif session['role'] == 'supervisor':
        employee_id = request.args.get("employee_id")
        supervisor_id = session['supervisor_id']
        if employee_id == None:
            query ={"supervisor_id":ObjectId(supervisor_id)}
            employees = employee_collection.find(query)
            employee_id = []
            for employee in employees:
                employee_id.append(employee['_id'])
            query = {"employee_id": {"$in": employee_id}}
        else:
            query = {"employee_id": ObjectId(employee_id)}
    print(query)
    leaves = leaves_collection.find(query)
    leaves = list(leaves)
    leaves.reverse()
    return render_template("leaves.html", leaves=leaves, get_employee_by_employee_id=get_employee_by_employee_id)


def get_employee_by_employee_id(employee_id):
    query = {"_id": employee_id}
    employee = employee_collection.find_one(query)
    return employee



@app.route("/leaves_action", methods=['post'])
def leaves_action():
    start_date = request.form.get("start_date")
    start_date = datetime.datetime.strptime(start_date,"%Y-%m-%d")
    end_date = request.form.get("end_date")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    diff = end_date - start_date
    days = diff.days
    days =  days + 1
    hours = days * 8
    reason = request.form.get("reason")
    status = 'applied'
    date = datetime.datetime.now()
    employee_id = session["employee_id"]
    dates = []
    start_date2 = start_date
    while start_date2 <= end_date:
        dates.append(start_date2.strftime("%d-%m-%Y"))
        start_date2 = start_date2 + datetime.timedelta(days=1)
        status2 = ['Cancelled', 'Rejected']
        query = {"$or": [
            {"start_date": {"$gte": start_date, "$lte": end_date},
             "end_date": {"$gte": start_date, "$gte": end_date},
             "employee_id": ObjectId(employee_id), "status": {"$nin" :status2}},
            {"start_date": {"$lte": start_date, "$lte": end_date},
             "end_date": {"$lte": start_date, "$gte": end_date},
             "employee_id": ObjectId(employee_id), "status": {"$nin" :status2}},
            {"start_date": {"$lte": start_date, "$lte": end_date},
             "end_date": {"$gte": start_date, "$gte": end_date},
             "employee_id": ObjectId(employee_id), "status": {"$nin" :status2}},
            {"start_date": {"$gte": start_date, "$lte": end_date},
             "end_date": {"$gte": start_date, "$lte": end_date},
             "employee_id": ObjectId(employee_id), "status": {"$nin" :status2}}
        ]}
    count = leaves_collection.count_documents(query)
    if count > 0:
        return redirect("leaves?message=Leave Already Applied for these dates")
    query = {"start_date": start_date, "end_date": end_date,"dates":dates, "reason": reason, "status": status, "date": date, "employee_id": ObjectId(employee_id), "days":days, "hours": hours}
    print(query)
    leaves_collection.insert_one(query)
    return redirect("leaves?message=applied for leave")


@app.route("/set_status")
def set_status():
    leave_id = request.args.get("leave_id")
    status = request.args.get("status")
    query1 = {"_id": ObjectId(leave_id)}
    query2 = {"$set": {"status": status}}
    leaves_collection.update_one(query1, query2)
    if session['role'] == 'supervisor':
        return render_template("smessage.html", message=status)
    else:
        return render_template("emessage.html", message=status)


@app.route("/reject_leave")
def reject_leave():
    leave_id = request.args.get("leave_id")
    status = request.args.get("status")
    return render_template("reject_leave.html",leave_id=leave_id, status=status)


@app.route("/reject_leave_action", methods=['post'])
def reject_leave_action():
    leave_id = request.form.get("leave_id")
    status = request.form.get("status")
    reason = request.form.get("reason")
    query1 = {"_id": ObjectId(leave_id)}
    query2 = {"$set": {"status": status, "reason": reason}}
    leaves_collection.update_one(query1, query2)
    if session['role'] == 'supervisor':
        return render_template("smessage.html", message=status)
    else:
        return render_template("emessage.html", message=status)




@app.route("/paychecks")
def paychecks():
    employee_id = request.args.get("employee_id")
    query = {"employee_id": ObjectId(employee_id)}
    paychecks = pay_check_collection.find(query)
    paychecks = list(paychecks)
    paychecks.reverse()
    return render_template("paychecks.html", paychecks=paychecks, employee_id=employee_id, round=round)



@app.route("/generate_pay_check")
def generate_pay_check():
    employee_id = request.args.get("employee_id")
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")
    if from_date == None:
        from_date = datetime.datetime.now()
        to_date = from_date + datetime.timedelta(days=30)
        from_date = from_date.strftime("%Y-%m-%d")
        to_date = to_date.strftime("%Y-%m-%d")
    from_date2 = datetime.datetime.strptime(from_date, "%Y-%m-%d")
    to_date2 = datetime.datetime.strptime(to_date, "%Y-%m-%d")
    dates = []
    while from_date2 <= to_date2:
        dates.append(from_date2.strftime("%d-%m-%Y"))
        from_date2 = from_date2 + datetime.timedelta(days=1)
    query = {"_id": ObjectId(employee_id)}
    employee = employee_collection.find_one(query)
    query = {"employee_id": ObjectId(employee_id)}
    contract = contract_collection.find_one(query)

    total_working_hours = 0
    total_overtime_hours = 0
    total_days = 0
    total_working_days = 0
    total_leave_days = 0
    for date in dates:
        transaction = get_transaction_by_date_and_employee_id(date, employee_id)
        if transaction != None:
            total_working_hours = total_working_hours + int(transaction["total_hours"])
            total_overtime_hours = total_overtime_hours + int(transaction["over_time"])
            total_days = total_days + 1
            total_working_days = total_working_days + 1
        else:
            leave = get_leave_by_date_and_employee_id(date, employee_id)
            if leave != None:
                total_days = total_days + 1
                total_leave_days = total_leave_days + 1
    total_leave_hours = total_leave_days * 8
    basic_salary = total_working_hours * int(contract['pay_per_hour']) + total_overtime_hours * int(contract['over_time_pay_per_hour'])
    state_tax = basic_salary * float(contract['state_tax'])/100
    income_tax = basic_salary * float(contract['income_tax']) / 100
    payable_amount = basic_salary - state_tax - income_tax - int(contract['health_insurance']) + int(contract['food_allows']) + int(contract['travelling_allows'])+ int(contract['house_rent_allows'])
    return render_template("generate_pay_check.html",employee=employee,contract=contract, dates=dates, employee_id=employee_id,from_date=from_date,to_date=to_date, get_transaction_by_date_and_employee_id=get_transaction_by_date_and_employee_id, get_leave_by_date_and_employee_id=get_leave_by_date_and_employee_id, int=int, round=round,
                           total_working_days=total_working_days,total_leave_days=total_leave_days,total_days=total_days,total_working_hours=total_working_hours, total_leave_hours=total_leave_hours, total_overtime_hours=total_overtime_hours,
                           basic_salary=basic_salary,state_tax=state_tax, income_tax=income_tax,
                           payable_amount=payable_amount)

def get_transaction_by_date_and_employee_id(date,employee_id):
    query = {"attendance_date": date, "employee_id": ObjectId(employee_id)}
    transaction = transactions_collection.find_one(query)
    return transaction
def get_leave_by_date_and_employee_id(date,employee_id):
    query = {"dates": date, "employee_id": ObjectId(employee_id), "status":"Approved"}
    leave = leaves_collection.find_one(query)
    return leave


@app.route("/generate_pay_check_action", methods=['post'])
def generate_pay_check_action():
    employee_id = request.form.get("employee_id")
    from_date = request.form.get("from_date")
    to_date = request.form.get("to_date")
    from_date =datetime.datetime.strptime(from_date, "%Y-%m-%d")
    to_date =datetime.datetime.strptime(to_date, "%Y-%m-%d")
    total_working_days = request.form.get("total_working_days")
    total_leave_days = request.form.get("total_leave_days")
    total_days = request.form.get("total_days")
    total_working_hours = request.form.get("total_working_hours")
    total_leave_hours = request.form.get("total_leave_hours")
    total_overtime_hours = request.form.get("total_overtime_hours")
    basic_salary = request.form.get("basic_salary")
    state_tax = request.form.get("state_tax")
    income_tax = request.form.get("income_tax")
    health_insurance = request.form.get("health_insurance")
    food_allows = request.form.get("food_allows")
    travelling_allows = request.form.get("travelling_allows")
    house_rent_allows = request.form.get("house_rent_allows")
    payable_amount = request.form.get("payable_amount")
    bonus = request.form.get("bonus")
    payable_amount = float(payable_amount) + int(bonus)
    query={"employee_id": ObjectId(employee_id), "from_date": from_date, "to_date": to_date, "total_working_days": total_working_days,"total_leave_days": total_leave_days,"total_days": total_days,"total_working_hours": total_working_hours,"total_leave_hours": total_leave_hours,"total_overtime_hours": total_overtime_hours,"basic_salary": basic_salary,"state_tax": state_tax,"income_tax": income_tax,"health_insurance": health_insurance,"food_allows": food_allows,"travelling_allows": travelling_allows,"house_rent_allows": house_rent_allows,"payable_amount": payable_amount,"bonus": bonus}
    print(query)
    pay_check_collection.insert_one(query)
    return redirect("paychecks?message=paychecks generated successfully&employee_id="+str(employee_id))



@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")



app.run(debug=True)