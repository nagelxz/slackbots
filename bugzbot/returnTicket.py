from fogbugz import FogBugz
from datetime import datetime, timedelta
import creds

def returnTicket(ticketNum):
	fb = FogBugz(creds.URL, creds.TOKEN)
	retrieveTicket = fb.search(q=ticketNum, cols="ixBug,sTitle,sPersonAssignedTo")

	ticketTitle = retrieveTicket.cases.case.stitle.string
	ticketOwner = retrieveTicket.cases.case.spersonassignedto.string
	ticketURL   = "https://tenthwave.fogbugz.com/f/cases/"+ticketNum
	ticket = ticketURL + "\n\nTicket: " + ticketNum + "\n" + ticketTitle

 	return ticket
