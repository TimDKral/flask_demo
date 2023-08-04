from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort
from flaskapp.db import get_db

bp = Blueprint('item', __name__)


@bp.route('/')
def index():
    db = get_db()
    items = db.execute('SELECT * FROM items').fetchall()
    return render_template('item/index.html', items=items)


def get_item(item_id):
    # Check if ID exists in table
    db = get_db()
    items = db.execute(
        'SELECT id, item_name, item_description'
        ' FROM items'
        ' WHERE id = ?',
        (item_id,)
    ).fetchone()
    return items


@bp.route('/items', methods=['POST'])
def create():
    item_name = request.form.get('item_name')
    item_description = request.form.get('item_description')
     
    # TODO: Check if inputs aren't actually empty
    if item_name is None:
        return jsonify({'message': 'Missing item_name'})
    if item_description is None:
        return jsonify({'message': 'Missing item_description'})


    db = get_db()
    db.execute("INSERT INTO items (item_name, item_description) VALUES (?, ?)",
        (item_name, item_description)
    )
    db.commit()
    
    # TODO: Broken
    #new_id = db.cursor().lastrowid
    #return jsonify({"id": new_id})
    
    return jsonify(success=True)

    
@bp.route('/items', methods=['GET'])
def read():
    item_id = request.form.get('id')
    item = get_item(item_id)
    if item is None:
        return jsonify({'message': 'ID not found'})
    print(item)
    return jsonify(dict(item))


@bp.route('/items', methods=('PUT', 'PATCH'))
def update():
    item_id = request.form.get('id')
    item_name = request.form.get('item_name')
    item_description = request.form.get('item_description')
    
    db = get_db()
    item = get_item(item_id)
    
    if item is None:
        return jsonify({'message': 'ID not found'})
    
    db.execute(
        'UPDATE items SET item_name = ?, item_description = ?'
        ' WHERE id = ?',
        (item_name, item_description, item_id)
    )
    db.commit()
    
    # Get the item again, and return as JSON dict
    update_item = get_item(item_id)
    return jsonify(dict(update_item))


@bp.route('/items', methods=['DELETE'])
def delete():
    db = get_db()
    item_id = request.form.get('id')
    item = get_item(item_id)
    
    if item is None:
        return jsonify({'message': 'ID not found'})
        
    db.execute('DELETE FROM items WHERE id = ?', (item_id,))
    db.commit()
    return jsonify(success=True)
    