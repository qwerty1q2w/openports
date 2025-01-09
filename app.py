from flask import Flask, request, render_template, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from config import Config
from models import db, ScanTask, ScanResult
from scanner import PortScanner

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
scheduler = BackgroundScheduler()
scanner = PortScanner(db)

def scan_with_context(task):
   with app.app_context():
       scanner.scan_ports(task)

@app.route('/')
def index():
   return render_template('index.html')

@app.route('/api/tasks', methods=['GET', 'POST'])
def tasks():
   if request.method == 'POST':
       data = request.json
       task = ScanTask(
           name=data['name'],
           ip_range=data['ip_range'],
           scan_interval=data['scan_interval'],
           scan_type=data['scan_type'],
           notifications=data['notifications']
       )
       db.session.add(task)
       db.session.commit()
       
       scheduler.add_job(
           scan_with_context,
           'interval',
           minutes=task.scan_interval,
           args=[task],
           id=f'task_{task.id}'
       )
       
       return jsonify({'id': task.id}), 201
   
   tasks = ScanTask.query.all()
   return jsonify([{
       'id': t.id,
       'name': t.name,
       'ip_range': t.ip_range,
       'scan_interval': t.scan_interval,
       'scan_type': t.scan_type,
       'notifications': t.notifications,
       'active': t.active
   } for t in tasks])

@app.route('/api/results')
def results():
   task_id = request.args.get('task_id')
   start_date = request.args.get('start_date')
   end_date = request.args.get('end_date')
   
   query = ScanResult.query
   if task_id:
       query = query.filter_by(task_id=task_id)
   if start_date:
       query = query.filter(ScanResult.timestamp >= datetime.fromisoformat(start_date))
   if end_date:
       query = query.filter(ScanResult.timestamp <= datetime.fromisoformat(end_date))
   
   results = query.all()
   return jsonify([{
       'id': r.id,
       'ip_address': r.ip_address,
       'port': r.port,
       'protocol': r.protocol,
       'status': r.status,
       'timestamp': r.timestamp.isoformat()
   } for r in results])

@app.route('/api/results/<int:result_id>', methods=['DELETE'])
def delete_result(result_id):
   result = ScanResult.query.get(result_id)
   if result:
       db.session.delete(result)
       db.session.commit()
       return jsonify({'success': True})
   return jsonify({'success': False}), 404

if __name__ == '__main__':
   with app.app_context():
       db.create_all()
       # Load existing tasks into scheduler
       tasks = ScanTask.query.filter_by(active=True).all()
       for task in tasks:
           scheduler.add_job(
               scan_with_context,
               'interval',
               minutes=task.scan_interval,
               args=[task],
               id=f'task_{task.id}'
           )
   scheduler.start()
   app.run(debug=True, host='0.0.0.0')
