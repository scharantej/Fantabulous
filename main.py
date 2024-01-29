
# Import necessary libraries
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

# Initialize the Flask app
app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fantasy_football.db'
app.config['SECRET_KEY'] = 'supersecretkey'
db = SQLAlchemy(app)

# Define the User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

# Define the League model
class League(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    commissioner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    members = db.relationship('User', secondary='league_members')
    players = db.relationship('Player', secondary='league_players')

# Define the LeagueMembers model (join table for many-to-many relationship between users and leagues)
class LeagueMembers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'), nullable=False)

# Define the LeaguePlayers model (join table for many-to-many relationship between leagues and players)
class LeaguePlayers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)

# Define the Player model
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    position = db.Column(db.String(20), nullable=False)
    team = db.Column(db.String(30), nullable=False)

# Initialize the LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Define the User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create the database tables
db.create_all()

# Home page route
@app.route('/')
def index():
    return render_template('index.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('leagues'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('leagues'))
        flash('Login failed. Please check your username and password.')
    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Leagues page route
@app.route('/leagues')
@login_required
def leagues():
    leagues = current_user.leagues
    return render_template('leagues.html', leagues=leagues)

# Create league route
@app.route('/create_league', methods=['GET', 'POST'])
@login_required
def create_league():
    if request.method == 'POST':
        name = request.form['name']
        new_league = League(name=name, commissioner_id=current_user.id)
        db.session.add(new_league)
        db.session.commit()
        return redirect(url_for('leagues'))
    return render_template('create_league.html')

# Join league route
@app.route('/join_league', methods=['GET', 'POST'])
@login_required
def join_league():
    if request.method == 'POST':
        access_code = request.form['access_code']
        league = League.query.filter_by(access_code=access_code).first()
        if league:
            league.members.append(current_user)
            db.session.commit()
            return redirect(url_for('leagues'))
        flash('Invalid access code.')
    return render_template('join_league.html')

# League dashboard route
@app.route('/league_dashboard/<int:league_id>')
@login_required
def league_dashboard(league_id):
    league = League.query.get_or_404(league_id)
    if current_user not in league.members:
        flash('You are not a member of this league.')
        return redirect(url_for('leagues'))
    return render_template('league_dashboard.html', league=league)

# Make transaction route (handle player transactions, trades, and lineup changes)
@app.route('/make_transaction', methods=['POST'])
@login_required
def make_transaction():
    transaction_type = request.form['transaction_type']
    league_id = request.form['league_id']
    player_id = request.form['player_id']
    # Handle the transaction based on its type
    if transaction_type == 'add':
        # Add the player to the user's team in the specified league
        team = current_user.get_team_in_league(league_id)
        team.players.append(Player.query.get(player_id))
        db.session.commit()
        flash('Player added to your team.')
    elif transaction_type == 'drop':
        # Drop the player from the user's team in the specified league
        team = current_user.get_team_in_league(league_id)
        team.players.remove(Player.query.get(player_id))
        db.session.commit()
        flash('Player dropped from your team.')
    elif transaction_type == 'trade':
        # Handle player trades between users in the same league
        team = current_user.get_team_in_league(league_id)
        other_team = User.query.get(request.form['other_user_id']).get_team_in_league(league_id)
        player1 = Player.query.get(request.form['player1_id'])
        player2 = Player.query.get(request.form['player2_id'])
        # Remove player1 from team and add player2 to team
        team.players.remove(player1)
        other_team.players.append(player1)
        # Remove player2 from other_team and add player1 to other_team
        other_team.players.remove(player2)
        team.players.append(player2)
        db.session.commit()
        flash('Trade completed.')
    elif transaction_type == 'set_lineup':
        # Set the user's lineup for the specified league
        team = current_user.get_team_in_league(league_id)
        team.lineup = request.form.getlist('lineup')
        db.session.commit()
        flash('Lineup set.')
    return redirect(url_for('league_dashboard', league_id=league_id))

# Draft room route
@app.route('/draft_room/<int:league_id>')
@login_required
def draft_room(league_id):
    league = League.query.get_or_404(league_id)
    if current_user not in league.members:
        flash('You are not a member of this league.')
        return redirect(url_for('leagues'))
    return render_template('draft_room.html', league=league)

# Chat route
@app