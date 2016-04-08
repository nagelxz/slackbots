import yaml
from fogbugz import FogBugz
from datetime import datetime, timedelta

def returnTicket(ticket_num, option, config):
	fb = FogBugz(config['FOGBUGZ_URL'], config['FOGBUGZ_TOKEN'])

	if option == "short":
	
		retrieve_ticket = fb.search(q=ticket_num, cols='ixBug,sTitle,sProject')

		if retrieve_ticket.cases['count'] == str(1):
		
			ticket_title = retrieve_ticket.cases.case.stitle.string
			ticket_project = retrieve_ticket.cases.case.sproject.string
			ticket_URL   = "https://tenthwave.fogbugz.com/f/cases/"+ticket_num
		
			ticket = "Ticket: " + ticket_num + "  |  " + ticket_title + "\n\n" + ticket_URL

			return ticket
		else:
			return "Something went wrong! Either Fogbugz is down, you're a magician calling a number that does not exist yet, or it somehow returned more than one ticket."
	else:
		
		retrieve_ticket = fb.search(q=ticket_num, cols="ixBug,sTitle,sLatestTextSummary,sArea,sProject")

		if retrieve_ticket.cases['count'] == str(1):
		
			ticket_title = retrieve_ticket.cases.case.stitle.string
			ticket_area = retrieve_ticket.cases.case.sarea.string
			ticket_project = retrieve_ticket.cases.case.sproject.string
			ticket_URL   = "https://tenthwave.fogbugz.com/f/cases/"+ticket_num
			ticket_last_update = retrieve_ticket.cases.case.slatesttextsummary.string
	
			ticket = ticket_URL + "\n\nTicket: " + ticket_num + "\n" + ticket_project + " : " + ticket_area + "\n*" + ticket_title + "*\n\n" + ticket_last_update
		
			return ticket
		else:
			return "Something went wrong! Either Fogbugz is down, you're a magician calling a number that does not exist yet, or it somehow returned more than one ticket."
		
	