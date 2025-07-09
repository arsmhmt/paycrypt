from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import User
from app.models.role import Role
from app.models.audit import AuditTrail
from app.forms import UserForm, RoleForm
from app.decorators import admin_required
from datetime import datetime

# Create user blueprint
user_bp = Blueprint('user', __name__, url_prefix='/users')

def log_audit(action, model, model_id, description, old_values=None, new_values=None):
    """Helper function to log audit trail"""
    if not hasattr(current_user, 'id'):
        user_id = None
    else:
        user_id = current_user.id
        
    audit = AuditTrail(
        user_id=user_id,
        action=action,
        model=model,
        model_id=model_id,
        description=description,
        old_values=old_values or {},
        new_values=new_values or {},
        ip_address=request.remote_addr if request else None,
        user_agent=request.user_agent.string if request and hasattr(request, 'user_agent') else None
    )
    db.session.add(audit)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to log audit: {e}")
    return audit

@user_bp.route('')
@login_required
@admin_required
def list_users():
    """List all users"""
    users = User.query.order_by(User.username).all()
    return render_template('admin/users/index.html', users=users)

@user_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    """Create a new user"""
    form = UserForm()
    form.role_id.choices = [(str(r.id), r.name) for r in Role.query.order_by('name').all()]
    
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                is_active=form.is_active.data,
                role_id=form.role_id.data
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            log_audit(
                'create',
                'user',
                user.id,
                f'User {user.username} created',
                new_values={
                    'username': user.username,
                    'email': user.email,
                    'role_id': user.role_id
                }
            )
            
            flash('User created successfully!', 'success')
            return redirect(url_for('user.list_users'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating user: {str(e)}')
            flash('An error occurred while creating the user.', 'error')
    
    return render_template('admin/users/create.html', form=form)

@user_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit an existing user"""
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    form.role_id.choices = [(str(r.id), r.name) for r in Role.query.order_by('name').all()]
    
    if form.validate_on_submit():
        try:
            old_values = {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
                'role_id': user.role_id
            }
            
            user.username = form.username.data
            user.email = form.email.data
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.is_active = form.is_active.data
            user.role_id = form.role_id.data
            
            if form.password.data:
                user.set_password(form.password.data)
            
            db.session.commit()
            
            log_audit(
                'update',
                'user',
                user.id,
                f'User {user.username} updated',
                old_values=old_values,
                new_values={
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_active': user.is_active,
                    'role_id': user.role_id
                }
            )
            
            flash('User updated successfully!', 'success')
            return redirect(url_for('user.list_users'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating user: {str(e)}')
            flash('An error occurred while updating the user.', 'error')
    
    return render_template('admin/users/edit.html', form=form, user=user)

@user_bp.route('/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user"""
    if current_user.id == user_id:
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('user.list_users'))
    
    user = User.query.get_or_404(user_id)
    
    try:
        log_audit(
            'delete',
            'user',
            user.id,
            f'User {user.username} deleted',
            old_values={
                'username': user.username,
                'email': user.email,
                'role_id': user.role_id
            }
        )
        
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deleting user: {str(e)}')
        flash('An error occurred while deleting the user.', 'error')
    
    return redirect(url_for('user.list_users'))

@user_bp.route('/roles')
@login_required
@admin_required
def list_roles():
    """List all roles"""
    roles = Role.query.order_by(Role.name).all()
    return render_template('admin/users/roles.html', roles=roles)

@user_bp.route('/roles/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_role():
    """Create a new role"""
    form = RoleForm()
    
    if form.validate_on_submit():
        try:
            role = Role(
                name=form.name.data,
                description=form.description.data,
                permissions=form.permissions.data
            )
            
            db.session.add(role)
            db.session.commit()
            
            log_audit(
                'create',
                'role',
                role.id,
                f'Role {role.name} created',
                new_values={
                    'name': role.name,
                    'description': role.description,
                    'permissions': role.permissions
                }
            )
            
            flash('Role created successfully!', 'success')
            return redirect(url_for('user.list_roles'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating role: {str(e)}')
            flash('An error occurred while creating the role.', 'error')
    
    return render_template('admin/users/role_form.html', form=form, title='Create Role')

@user_bp.route('/roles/<int:role_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_role(role_id):
    """Edit an existing role"""
    role = Role.query.get_or_404(role_id)
    form = RoleForm(obj=role)
    
    if form.validate_on_submit():
        try:
            old_values = {
                'name': role.name,
                'description': role.description,
                'permissions': role.permissions
            }
            
            role.name = form.name.data
            role.description = form.description.data
            role.permissions = form.permissions.data
            
            db.session.commit()
            
            log_audit(
                'update',
                'role',
                role.id,
                f'Role {role.name} updated',
                old_values=old_values,
                new_values={
                    'name': role.name,
                    'description': role.description,
                    'permissions': role.permissions
                }
            )
            
            flash('Role updated successfully!', 'success')
            return redirect(url_for('user.list_roles'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating role: {str(e)}')
            flash('An error occurred while updating the role.', 'error')
    
    return render_template('admin/users/role_form.html', form=form, title='Edit Role', role=role)

@user_bp.route('/roles/<int:role_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_role(role_id):
    """Delete a role"""
    role = Role.query.get_or_404(role_id)
    
    # Check if the role is assigned to any users
    if role.users:
        flash('Cannot delete a role that is assigned to users!', 'danger')
        return redirect(url_for('user.list_roles'))
    
    try:
        log_audit(
            'delete',
            'role',
            role.id,
            f'Role {role.name} deleted',
            old_values={
                'name': role.name,
                'description': role.description,
                'permissions': role.permissions
            }
        )
        
        db.session.delete(role)
        db.session.commit()
        flash('Role deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deleting role: {str(e)}')
        flash('An error occurred while deleting the role.', 'error')
    
    return redirect(url_for('user.list_roles'))
