#! /usr/bin/env python

from flask import Flask, render_template, request, redirect, url_for, jsonify, flash    #import flask class

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem


app = Flask(__name__)        #create instance of class Flask

#  --------------------  instantiate DB engine ------------------------#

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# -----------------------  define URL routing and pages ------------ #

@app.route('/')
@app.route('/restaurant/')
#    return "This page will show all my restaurants"
def showRestaurants():
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants=restaurants)

@app.route('/restaurant/new', methods = ['GET','POST'])
#    return 'This page will be for creating new restaurant'
def newRestaurant():
    if request.method == 'POST':
        newRest = Restaurant(name = request.form['name'])
        session.add(newRest)
        session.commit()
        flash("new restaurant created!")
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('newRestaurant.html')

@app.route('/restaurant/<int:restaurant_id>/edit', methods = ['GET','POST'])
#   return 'This page will be for editing name of restaurant %s' %restaurant_id
def editRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        if request.form['name']:
          restaurant.name = request.form['name']
          session.add(restaurant)
          session.commit()
          flash("restaurant edited!")
          return redirect(url_for('showRestaurants'))
    else:
      return render_template('editRestaurant.html', restaurant=restaurant)

@app.route('/restaurant/<int:restaurant_id>/delete', methods = ['GET','POST'])
#    return 'This page will be for deleting menu item {0} for restaurant {1} <p> And by the way,<p><h1> Brian is bad Ass!</h1>'.format(menu_id,restaurant_id)
def deleteRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    restToDel = restaurant.name
    if request.method == 'POST':
      session.delete(restaurant)
      session.commit()
      flash("restaurant deleted!")
      return redirect(url_for('showRestaurants'))
    else:
      return render_template('deleteRestaurant.html', restaurant=restToDel)

@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu/')
#    return 'This page will show the menu for restaurant ID %s' %restaurant_id
def showMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return render_template('menu.html', restaurant=restaurant, items=items)

@app.route('/restaurant/<int:restaurant_id>/menu/new/', methods = ['GET','POST'])
#    return 'This page will be for adding a bad ass new menu item to restaurant %s' %restaurant_id
def newMenuItem(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        newItem = MenuItem(name=request.form['name'], description=request.form[
                           'description'], price=request.form['price'], course=request.form['course'], restaurant_id=restaurant_id)
        session.add(newItem)
        session.commit()
        flash ("new menu item created!")
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant=restaurant)

@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/edit', methods = ['GET','POST'])
#    return 'This page will be for editing menu item {0} for restaurant {1} <p> And by the way,<p><h1> Brian is Cool!</h1>'.format(menu_id,restaurant_id)
def editMenuItem(restaurant_id,menu_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    item = session.query(MenuItem).filter_by(id = menu_id).one()
    if request.method == 'POST':
        if request.form['name']:
            item.name = request.form['name']
        if request.form['description']:
            item.description = request.form['description']
        if request.form['price']:
            item.price = request.form['price']
        if request.form['course']:
            item.course = request.form['course']
        session.add(item)
        session.commit()
        flash("menu item succesfully edited!")
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('editmenuitem.html', restaurant =restaurant_id, item=item)

@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/delete', methods = ['POST','GET'])
#    return 'This page will be for deleting menu item {0} for restaurant {1} <p> </h1>'.format(menu_id,restaurant_id)
def deleteMenuItem(restaurant_id,menu_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    itemToDel = session.query(MenuItem).filter_by(id = menu_id).one()
    if request.method == 'POST':
      session.delete(itemToDel)
      session.commit()
      flash("menu item deleted!")
      return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
      return render_template('deletemenuitem.html', restaurant=restaurant, item=itemToDel)

#  --------------------  API enpoints ------------------------#

@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])

@app.route('/restaurant/JSON')
def restaurantJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(Restaurants=[item.serialize for item in restaurants])

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
    menuItem = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(MenuItem=menuItem.serialize)


#  --------------------  Call main  ------------------------#

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)