# utils.py
from flask import session, redirect, url_for, flash, abort, request, jsonify
from functools import wraps
from models import User # Import User model here to resolve circular dependency

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to be logged in to access this page.', 'error')
            # 'login_api' is a global route defined in app.py
            return redirect(url_for('login_api'))

        user = User.query.get(session.get('user_id'))
        if not user or not user.is_active:
            session.pop('user_id', None)
            flash('Your session has expired or account is inactive.', 'error')
            return redirect(url_for('login_api'))

        request.current_user = user # Attach the current user to the request object
        return f(*args, **kwargs)
    return decorated_function

def roles_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('You need to be logged in to access this page.', 'error')
                return redirect(url_for('login_api'))

            user = User.query.get(session.get('user_id'))
            if not user or not user.is_active:
                session.pop('user_id', None)
                flash('Your session has expired or account is inactive.', 'error')
                return redirect(url_for('login_api'))

            request.current_user = user # Ensure current_user is set for role checking

            if not request.current_user.has_roles(*roles):
                flash('You do not have the required permissions.', 'error')
                return abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return wrapper