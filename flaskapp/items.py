from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort
from flaskapp.db import get_db
from flask_apispec import marshal_with, doc, use_kwargs
from marshmallow import Schema, fields

# Swagger schemas
class ItemRequestSchema(Schema):
    api_type = fields.String(required=True, description="API type of awesome API")

class ItemResponseSchema(Schema):
    message = fields.Str(default='Success')

# Main Blueprint
bp = Blueprint('item', __name__)


@bp.route('/')
def index():
    '''Index returns a formatted HTML of all results'''
    db = get_db()
    items = db.execute('SELECT * FROM items').fetchall()
    return render_template('item/index.html', items=items)


def get_item(item_id):
    '''Helper function, finds and returns item from DB, used by UPDATE and DELETE'''
    # Check if ID exists in table
    db = get_db()
    
    items = db.execute(
        'SELECT id, item_name, item_description'
        ' FROM items'
        ' WHERE id = ?',
        (item_id,)
    ).fetchone()
    return items


@doc(description='POST Item', tags=['Item'])
@marshal_with(ItemResponseSchema)
@bp.route('/items', methods=['POST'])
def create():
    '''Creates a new item and auto generates an incremental ID'''
    item_name = request.form.get('item_name')
    item_description = request.form.get('item_description')
    db = get_db()
     
    # TODO: Check if inputs aren't actually empty
    if item_name is None:
        return jsonify({'message': 'Missing item_name'})
    if item_description is None:
        return jsonify({'message': 'Missing item_description'})
    
    try:
        db.execute("INSERT INTO items (item_name, item_description) VALUES (?, ?)",
            (item_name, item_description)
        )
        db.commit()
    except Exception as e:
        return jsonify({"Database Error": str(e)})
    
    # TODO: Broken
    #new_id = db.cursor().lastrowid
    #return jsonify({"id": new_id})
    
    return jsonify(success=True)


@doc(description='GET Item', tags=['Item'])
@marshal_with(ItemResponseSchema)
@bp.route('/items', methods=['GET'])
def read():
    '''Return item based on ID'''
    item_id = request.form.get('id')
    item = get_item(item_id)
    if item is None:
        return jsonify({'message': 'ID not found'})

    return jsonify(dict(item))


@doc(description='PUT or UPDATE Item', tags=['Item'])
@marshal_with(ItemResponseSchema)
@bp.route('/items', methods=('PUT', 'PATCH'))
def update():
    '''Update item name/description based on ID'''
    item_id = request.form.get('id')
    item_name = request.form.get('item_name')
    item_description = request.form.get('item_description')
    db = get_db()
    
    item = get_item(item_id)
    
    if item is None:
        return jsonify({'message': 'ID not found'})
    
    try:
        db.execute(
            'UPDATE items SET item_name = ?, item_description = ?'
            ' WHERE id = ?',
            (item_name, item_description, item_id)
        )
        db.commit()
    except Exception as e:
        return jsonify({"Database Error": str(e)})
    
    # Get the item again, and return as JSON dict
    update_item = get_item(item_id)
    return jsonify(dict(update_item))


@doc(description='DELETE Item', tags=['Item'])
@marshal_with(ItemResponseSchema)
@bp.route('/items', methods=['DELETE'])
def delete():
    '''Delete item by ID'''
    
    db = get_db()
    item_id = request.form.get('id')
    item = get_item(item_id)
    
    if item is None:
        return jsonify({'message': 'ID not found'})
        
    try:
        db.execute('DELETE FROM items WHERE id = ?', (item_id,))
        db.commit()
    except Exception as e:
        return jsonify({"Database Error": str(e)})
        
    
    
    return jsonify(success=True)
    