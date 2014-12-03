import cgi
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2

MAIN_PAGE_TEMPLATE = """\
		</p></p>
		<a href="/addrestaurant">Add a Restaurant to the datastore</a>
	</body>
</html>
"""

ADD_RESTAURANT_TEMPLATE = """\
<html>
	<body>
		<form action="/postrestaurant" method="post">
			Name:<div><input name="rest_name"></div>
			Cuisine:
			<div>
				<select name="rest_type">
					<option value="indian">Indian</option>
					<option value="pizza">Pizza</option>
					<option value="chinese">Chinese</option>
					<option value="kebab">Kebab</option>
					<option value="italian">Italian</option>
					<option value="fishandchips">Fish & Chips</option>
					<option value="america">American</option>
					<option value="chicken">Chicken</option>
					<option value="carribean">Carribean</option>
				</select>
			</div>
			City:<div><input name="rest_city"></div>
			Postcode:<div><input name="rest_postcode"></div>
			Phone Number:<div><input name="rest_phone"></div>
			<div><input type="submit" value="ADD RESTAURANT"></div>
		</form>
	</body>
</html>
"""

EDIT_RESTAURANT_TEMPLATE = """\
		<form action="/postrestaurant" method="post">
			Name:<div><input value="%s" name="rest_name"></div>
			Cuisine:
			<div>
				<select name="rest_type">
					<option value="indian">Indian</option>
					<option value="pizza">Pizza</option>
					<option value="chinese">Chinese</option>
					<option value="kebab">Kebab</option>
					<option value="italian">Italian</option>
					<option value="fishandchips">Fish & Chips</option>
					<option value="america">American</option>
					<option value="chicken">Chicken</option>
					<option value="carribean">Carribean</option>
				</select>
			</div>
			City:<div><input value="%s" name="rest_city"></div>
			Postcode:<div><input value="%s" name="rest_postcode"></div>
			Phone Number:<div><input value="%s" name="rest_phone"></div>
			<div><input type="submit" value="ADD RESTAURANT"></div>
		</form>
	</body>
</html>
"""

class Restaurant(ndb.Model):
	name = ndb.StringProperty(required=True)
	cuisine = ndb.StringProperty(required=True)
	city = ndb.StringProperty(required=True)
	postcode = ndb.StringProperty(required=False)
	phone = ndb.StringProperty(required=False)
	created = ndb.DateTimeProperty(auto_now_add=True)

class MainPage(webapp2.RequestHandler):
	def get(self):
		self.response.write('<html><body>')
		restaurants = Restaurant.query()
		
		for r in restaurants:
			self.response.write(r.name)
			self.response.write('<form action="/displayrestaurant" method="get"><input type="submit" value="View"></form>')
			
			self.response.write('<form action="/editrestaurant" method="get"><input type="submit" value="Edit"></form>')
			self.response.write('</p>')
		
		self.response.write(MAIN_PAGE_TEMPLATE) 

class AddRestaurant(webapp2.RequestHandler):
	def get(self):
		self.response.write(ADD_RESTAURANT_TEMPLATE)
	
class PostRestaurant(webapp2.RequestHandler):
	def post(self):
		r = Restaurant()
		r.name = self.request.get('rest_name')
		r.cuisine = self.request.get('rest_type')
		r.city = self.request.get('rest_city')
		r.postcode = self.request.get('rest_postcode')
		r.phone = self.request.get('rest_phone')
		r.put()
		self.redirect('/')
		
class DisplayRestaurant(webapp2.RequestHandler):
	def get(self):
		self.response.write('<html><body><b>')
		self.response.write(r.name)
		self.response.write('</b>')
		
class EditRestaurant(webapp2.RequestHandler):
	def get(self):
		self.response.write('<html><body>')
		self.response.write(EDIT_RESTAURANT_TEMPLATE)

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/addrestaurant', AddRestaurant),
	('/postrestaurant', PostRestaurant),
	('/displayrestaurant', MainPage),
	('/editrestaurant', MainPage),
], debug=True)