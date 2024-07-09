from flask import Flask, render_template, redirect, url_for,request
from flask_sqlalchemy import SQLAlchemy
#from flask import request


app =Flask(__name__, static_url_path='/static')  #instance of the flask class
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db=SQLAlchemy(app)

CATEGORIES=['Admin','Fundi@work','Fundi@Home','Fundi@School','FundiGirl','Guest','Helper']

class User(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    fingerprint_id=db.Column(db.Integer,unique=True,nullable=False)
    category=db.Column(db.String(50), nullable=False)
    attendance_records=db.relationship('Attendance',backref='user',lazy=True)

class Attendance(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    timestamp=db.Column(db.DateTime, default=db.func.current_timestamp())
    status=db.Column(db.String(10),nullable=False)

#decorator for defining route for the home page
@app.route('/')
def index():  #function to handle requests to the home page
    attendance_records=Attendance.query.all()
    return render_template('index.html', attendance=attendance_records)

#functions to help handling information
@app.route('/users')
def users():
    users=User.query.all()
    return render_template('users.html',users=users,categories=CATEGORIES)


@app.route('/add_user',methods=['POST'])
def add_user():
    name=request.form['name']
    fingerprint_id=request.form['fingerprint_id']
    category=request.form['category']
    new_user=User(name=name,fingerprint_id=fingerprint_id,category=category)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('users'))

@app.route('/update_user/<int:user_id>',methods=['GET','POST'])
def update_user(user_id):
    user=User.query.get(user_id)
    if request.method=='POST':
        user.name=request.form['name']
        user.fingerprint_id=request.form['fingerprint_id']
        user.category=request.form['category']
        db.session.commit()
        return redirect(url_for('users'))
    return render_template('update_user.html',user=user,categories=CATEGORIES)

@app.route('/delete_user/<int:user_id>',methods=['POST'])
def delete_user(user_id):
    user=User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('users'))

def add_attendance_record(fingerprint_id,status):
    user=User.query.filter_by(fingerprint_id=fingerprint_id).first()
    if user:
        new_record=Attendance(user_id=user.id,status=status)
        db.session.add(new_record)
        db.session.commit()

if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
