#!/usr/bin/python


'''
Author  : Corey Osman
Date    : 03/18/2010
Email   : corey@logicminds.biz
Purpose : ManageEngine Servicedesk plus software has a API (via POST) in order to create, change, delete tickets 
and perform other actions within the software.  This script basically wraps that ugly API into something
more useful and accessible via python command line.  This script will create a new ticket and return the
ticket number along with success/failure code and description of the action performed.  

'''
from httplib2 import Http
from urllib import urlencode
from optparse import OptionParser
from xml.dom import minidom


# Change the following url to suit the host
host="https://servicedesk.hostname.corp"
sdpurl="%s/servlets/RequestServlet" % host

# This is optional and should only be used if using Active Directory, leave blank if using local auth
domain_name='ADDOMAIN'
# Change to "AD_AUTH" for active directory or leave blank for local 
authtype="AD_AUTH"            



class sdobject:
    '''
    This class provides common functionality for creating, deleting, updating ... of supported servicedesk plus API
    '''
    def sethost(host):
        self.host = host
    
    def seturl(url):
        self.url = url
    
    def setdomain(dn):
        self.dn = dn
    
    def setauthtype(type):
        self.authtype(type)


    def __init__():
        pass

    def parseresults(content):
        pass

    def createbody(type, parser):
        pass

    def createcli():
        pass



def createbody(type, parser):
    '''
    Purpose: get the arguments from command line and create urlbody (POST) response.
    Output: string of http encoded parameters
    '''
    #https://helpdesk.mycompany.com/servlets/RequestServlet/operation='AddRequest'
    #/title='Test'/description='Test'/requester='requesterusername'/username='myusername'/password='mypassword'/DOMAIN_NAME='MYDOMAIN'/logonDomainName='AD_AUTH'
    data = dict(username="name", password="pass", subject=parser.subject, requester="NPM",
                 description=parser.description,
                 operation=type, 
                 priority=parser.priority,
                 logonDomainName=parser.logonDomainName,
                 DOMAIN_NAME=parser.DOMAIN_NAME)
    
    body=urlencode(data)   
    print body
    return body

def parseresults(content):
    '''
    The function will parse the returned content which should be xml data and get the results
    Input: an xml string
    Output: the status, ticket and message
    '''
# This is the returned content    
#    <operation>
#      <operationstatus>Success</operationstatus>
#      <workorderid>24</workorderid>
#      <message>Request created successfully with WorkOrderID : 24</message>
#    </operation>
    ticket = 0
    dom = minidom.parseString(content)
    status = dom.getElementsByTagName("operationstatus")
    status = status[0].firstChild.wholeText
    
    if status == "Success":
        ticket = dom.getElementsByTagName("workorderid")
        ticket = ticket[0].firstChild.wholeText
    message = dom.getElementsByTagName("message")
    message = message[0].firstChild.wholeText
    dom.unlink()
    return (status, ticket, message)

def createrequest(sdpurl, parser):
    '''
    This will create a servicedesk request based upon the given input.
    Output: success/failure response with ticket number
    '''
    urlbody=createbody("AddRequest", parser)
    h = Http()
    response, content = h.request(sdpurl, method="POST", body=urlbody, 
                                  headers={'Content-type': 'application/x-www-form-urlencoded'})
    
    return parseresults(content)


# create cli parser object

parser = OptionParser()
parser.add_option("-s", "--subject", dest="subject", default="test request through API",
                  help="the subject line of the ticket")
parser.add_option("-d", "--description", dest="description", default="Thanks for letting me test the API",
                  help="the description for the ticket")
parser.add_option("-g", "--group", dest="group",
                  help="the group assigned to the ticket")
parser.add_option("-p", "--priority", dest="priority", default='Normal',
                  help="the priority of the ticket: Low, Normal, Medium, High [default: %default]")
parser.add_option("--auth", dest="logonDomainName", default=authtype,
                  help="The type of autentication used  [AD_AUTH or Local Authentication]")
# If the user decides to pick local auth then make sure the domain doesnt' get set
if authtype == "":
    domain_name=""
parser.add_option("--domain", dest="DOMAIN_NAME", default=domain_name,
                  help="The domain name of the active directory server")



(options, args) = parser.parse_args()

# This is the "Main" part of the program

status, ticket, message = createrequest(sdpurl, options) 
print status
print ticket
print message

