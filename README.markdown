OpenNMS Severe Weather addon
================
* getWeather.py   
 --- main app that gets weather events from weatherbug and sends the alert to opennms.  Edit this file to suit your environment.
* Weather.events.xml   
 --- event definitions for opennms

Opennms [wiki site](http://www.opennms.org/wiki/Severe_Weather_Alerts_with_opennms "Title") with instructions on setting up severe weather alerts.

OpenNMS Manage Engine API
================
* A python wrapper that makes using the service desk api easy.
* sdpapi.py  -- main program that talks to the 
[Manage Engine API](http://www.manageengine.com/products/service-desk/help-desk-integration.html)

Note:  This was a prototype I built a while ago so it may not work 100% as the api may have changed.

License
========

    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

