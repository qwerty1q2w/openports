import nmap
import requests
import os
from models import db, ScanResult

class PortScanner:
   def __init__(self, db):
       self.nm = nmap.PortScanner()
       self.db = db
       self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')

   def scan_ports(self, task):
       args = '-sS' if task.scan_type == 'TCP' else '-sU' if task.scan_type == 'UDP' else '-sS -sU'
       
       try:
           self.nm.scan(task.ip_range, arguments=args)
           new_findings = []

           for host in self.nm.all_hosts():
               for proto in self.nm[host].all_protocols():
                   ports = self.nm[host][proto].keys()
                   for port in ports:
                       # Check if port is not already in database
                       existing = ScanResult.query.filter_by(
                           task_id=task.id,
                           ip_address=host,
                           port=port,
                           protocol=proto
                       ).first()

                       if not existing:
                           result = ScanResult(
                               task_id=task.id,
                               ip_address=host,
                               port=port,
                               protocol=proto,
                               status=self.nm[host][proto][port]['state']
                           )
                           self.db.session.add(result)
                           new_findings.append(result)

           self.db.session.commit()
           
           if new_findings:
               self.send_notifications(task, new_findings)

       except Exception as e:
           print(f"Scan error: {str(e)}")

   def send_notifications(self, task, findings):
       message = f"New open ports found for task '{task.name}':\n"
       for finding in findings:
           message += f"IP: {finding.ip_address}, Port: {finding.port}, Protocol: {finding.protocol}\n"

       notifications = task.notifications

       # Discord notifications
       if 'discord' in notifications:
           for webhook in notifications['discord']:
               try:
                   requests.post(webhook, json={'content': message})
               except Exception as e:
                   print(f"Discord notification error: {str(e)}")

       # Slack notifications
       if 'slack' in notifications:
           for webhook in notifications['slack']:
               try:
                   requests.post(webhook, json={'text': message})
               except Exception as e:
                   print(f"Slack notification error: {str(e)}")

       # Telegram notifications
       if 'telegram' in notifications:
           for chat_id in notifications['telegram']:
               try:
                   url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
                   requests.post(url, json={'chat_id': chat_id, 'text': message})
               except Exception as e:
                   print(f"Telegram notification error: {str(e)}")
