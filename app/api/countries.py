from flask import jsonify, g
from app import db
from app.api import bp
from app.api.auth import basic_auth, token_auth
from app.models import Countries
from app.models import Song
from flask import request, jsonify, g
import json


@bp.route('/countries', methods=['GET'])
def get_countries():
    countries = Countries.query.all()


    return jsonify(
        {'countries': [county.to_dict() for county in countries]}
    )
