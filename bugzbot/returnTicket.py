from fogbugz import FogBugz
from datetime import datetime, timedelta
import creds

def returnTicket(ticketNum):
	fb = FogBugz(creds.URL, creds.TOKEN)
	retrieveTicket = fb.search(q=ticketNum, cols="ixBug,sTitle,sPersonAssignedTo,sLatestTextSummary")

	ticketTitle = retrieveTicket.cases.case.stitle.string
	ticketOwner = retrieveTicket.cases.case.spersonassignedto.string
	ticketURL   = "https://tenthwave.fogbugz.com/f/cases/"+ticketNum
	ticketLastUpdate = retrieveTicket.cases.case.sLatestTextSummary.string
	ticket = ticketURL + "\n\nTicket: " + ticketNum + "\n" + ticketTitle + "\n\n" + ticketLastUpdate

 	return ticket
