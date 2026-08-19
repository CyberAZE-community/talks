reputation = check_ip_reputation(IP)
if reputation > 50:
	allow_email(email_id)
else 
	quarantine_email(email_id)